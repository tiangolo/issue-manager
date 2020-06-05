from datetime import datetime, timedelta
import logging
from pathlib import Path
from typing import Dict, List, Optional

from github import Github
from github.Issue import Issue
from github.IssueComment import IssueComment
from github.IssueEvent import IssueEvent
from github.NamedUser import NamedUser
from pydantic import BaseModel, BaseSettings, SecretStr


class KeywordMeta(BaseModel):
    delay: timedelta = timedelta(days=10)
    users: List[str] = []
    message: str = "Assuming the original issue was solved, it will be automatically closed now."
    remove_label: bool = True


class Settings(BaseSettings):
    input_config: Dict[str, KeywordMeta]
    github_repository: str
    input_token: SecretStr
    github_event_path: Path
    github_event_name: Optional[str] = None


class PartialGitHubEventIssue(BaseModel):
    number: int


class PartialGitHubEvent(BaseModel):
    issue: Optional[PartialGitHubEventIssue] = None


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
) -> IssueEvent:
    last_event: Optional[IssueEvent] = None
    for event in labeled_events:
        if event.label.name == label:
            if not last_event:
                last_event = event
                continue
            if event.created_at > last_event.created_at:
                last_event = event
    return last_event


def close_issue(*, issue: Issue, keyword_meta: KeywordMeta) -> None:
    logging.info(
        f"Clossing issue: #{issue.number} with message: {keyword_meta.message}"
    )
    issue.create_comment(keyword_meta.message)
    issue.edit(state="closed")


def process_issue(*, issue: Issue, settings: Settings, owner: NamedUser) -> None:
    logging.info(f"Processing issue: #{issue.number}")
    label_strs = set([l.name for l in issue.get_labels()])
    events = list(issue.get_events())
    labeled_events = get_labeled_events(events)
    last_comment = get_last_comment(issue)
    for keyword, keyword_meta in settings.input_config.items():
        # Check closable delay, if enough time passed and the issue could be closed
        closable_delay = False
        if (
            last_comment is None
            or (datetime.utcnow() - keyword_meta.delay) > last_comment.created_at
        ):
            closable_delay = True
        # Check label, optionally removing it if there's a comment after adding it
        if keyword in label_strs:
            logging.info(f'Keyword: "{keyword}" in issue labels')
            keyword_event = get_last_event_for_label(
                labeled_events=labeled_events, label=keyword
            )
            if last_comment and last_comment.created_at > keyword_event.created_at:
                logging.info(
                    f"Not closing as the last comment was written after adding the "
                    f'label: "{keyword}"'
                )
                if keyword_meta.remove_label:
                    logging.info(f'Removing label: "{keyword}"')
                    issue.remove_from_labels(keyword)
            elif closable_delay:
                close_issue(issue=issue, keyword_meta=keyword_meta)
                break
        # Check HTML comments by allowed users
        if (
            last_comment
            and f"<!-- issue-manager: {keyword} -->" in last_comment.body
            and closable_delay
            and last_comment.user.login in keyword_meta.users + [owner.login]
        ):
            logging.info(
                f'Last comment by user: "{last_comment.user.login}" had HTML keyword '
                f'comment: "{keyword}" and there\'s a closable delay.'
            )
            close_issue(issue=issue, keyword_meta=keyword_meta)
            break


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    logging.info(f"Using config: {settings.json()}")
    g = Github(settings.input_token.get_secret_value())
    repo = g.get_repo(settings.github_repository)
    owner: NamedUser = repo.owner
    github_event: Optional[PartialGitHubEvent] = None
    if settings.github_event_path.is_file():
        contents = settings.github_event_path.read_text()
        github_event = PartialGitHubEvent.parse_raw(contents)
    if (
        settings.github_event_name == "issues"
        or settings.github_event_name == "issue_comment"
    ):
        if github_event and github_event.issue:
            issue = repo.get_issue(github_event.issue.number)
            if issue.state == "open":
                process_issue(issue=issue, settings=settings, owner=owner)
    else:
        for issue in repo.get_issues(state="open"):
            process_issue(issue=issue, settings=settings, owner=owner)
    logging.info(f"Finished")
