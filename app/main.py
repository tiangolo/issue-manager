from datetime import datetime, timedelta
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

from github import Github
from github.Issue import Issue
from github.IssueComment import IssueComment
from github.IssueEvent import IssueEvent
from pydantic import BaseModel, BaseSettings, SecretStr, validator


class KeywordMeta(BaseModel):
    delay: timedelta = timedelta(days=10)
    message: str = "Assuming the original need was handled, this will be automatically closed now."
    remove_label_on_comment: bool = True
    remove_label_on_close: bool = False


class Settings(BaseSettings):
    input_config: Dict[str, KeywordMeta]
    github_repository: str
    input_token: SecretStr
    github_event_path: Path
    github_event_name: Optional[str] = None

    @validator("input_config", pre=True)
    def discard_schema(cls, v):
        if "$schema" in v:
            del v["$schema"]
        return v


class PartialGitHubEventIssue(BaseModel):
    number: int


class PartialGitHubEvent(BaseModel):
    issue: Optional[PartialGitHubEventIssue] = None
    pull_request: Optional[PartialGitHubEventIssue] = None


def get_last_comment(issue: Issue) -> Optional[IssueComment]:
    last_comment: Optional[IssueComment] = None
    comment: IssueComment
    for comment in issue.get_comments():
        if not last_comment:
            last_comment = comment
        elif comment.created_at > last_comment.created_at:
            last_comment = comment
    return last_comment


def get_labeled_events(events: List[IssueEvent]) -> List[IssueEvent]:
    labeled_events = []
    for event in events:
        if event.event == "labeled":
            labeled_events.append(event)
    return labeled_events


def get_last_event_for_label(
    *, labeled_events: List[IssueEvent], label: str
) -> Optional[IssueEvent]:
    last_event: Optional[IssueEvent] = None
    for event in labeled_events:
        if event.label and event.label.name == label:
            if not last_event:
                last_event = event
                continue
            if event.created_at > last_event.created_at:
                last_event = event
    return last_event


def close_issue(
    *, issue: Issue, keyword_meta: KeywordMeta, keyword: str, label_strs: Set[str]
) -> None:
    logging.info(
        f"Clossing issue: #{issue.number} with message: {keyword_meta.message}"
    )
    issue.create_comment(keyword_meta.message)
    issue.edit(state="closed")
    if keyword_meta.remove_label_on_close:
        if keyword in label_strs:
            issue.remove_from_labels(keyword)


def process_issue(*, issue: Issue, settings: Settings) -> None:
    logging.info(f"Processing issue: #{issue.number}")
    label_strs = set([label.name for label in issue.get_labels()])
    events = list(issue.get_events())
    labeled_events = get_labeled_events(events)
    last_comment = get_last_comment(issue)
    for keyword, keyword_meta in settings.input_config.items():
        # Check closable delay, if enough time passed and the issue could be closed
        closable_delay = (
            last_comment is None
            or (datetime.utcnow() - keyword_meta.delay) > last_comment.created_at
        )
        # Check label, optionally removing it if there's a comment after adding it
        if keyword in label_strs:
            logging.info(f'Keyword: "{keyword}" in issue labels')
            keyword_event = get_last_event_for_label(
                labeled_events=labeled_events, label=keyword
            )
            if (
                last_comment
                and keyword_event
                and last_comment.created_at > keyword_event.created_at
            ):
                logging.info(
                    f"Not closing as the last comment was written after adding the "
                    f'label: "{keyword}"'
                )
                if keyword_meta.remove_label_on_comment:
                    logging.info(f'Removing label: "{keyword}"')
                    issue.remove_from_labels(keyword)
            elif closable_delay:
                close_issue(
                    issue=issue,
                    keyword_meta=keyword_meta,
                    keyword=keyword,
                    label_strs=label_strs,
                )
                break
            else:
                logging.info(
                    f"Not clossing issue: #{issue.number} as the delay hasn't been reached: {keyword_meta.delay}"
                )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    logging.info(f"Using config: {settings.json()}")
    g = Github(settings.input_token.get_secret_value())
    repo = g.get_repo(settings.github_repository)
    github_event: Optional[PartialGitHubEvent] = None
    if settings.github_event_path.is_file():
        contents = settings.github_event_path.read_text()
        github_event = PartialGitHubEvent.parse_raw(contents)
    if (
        settings.github_event_name == "issues"
        or settings.github_event_name == "pull_request_target"
        or settings.github_event_name == "issue_comment"
    ):
        if github_event:
            issue_number: Optional[int] = None
            if github_event.issue:
                issue_number = github_event.issue.number
            elif github_event.pull_request:
                issue_number = github_event.pull_request.number
            if issue_number is not None:
                issue = repo.get_issue(issue_number)
                if issue.state == "open":
                    process_issue(issue=issue, settings=settings)
    else:
        for keyword, keyword_meta in settings.input_config.items():
            for issue in repo.get_issues(state="open", labels=[keyword]):
                process_issue(issue=issue, settings=settings)
    logging.info("Finished")
