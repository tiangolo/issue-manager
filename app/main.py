import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set
from typing_extensions import Literal

from github import Github
from github.PaginatedList import PaginatedList
from github.IssueComment import IssueComment
from github.Issue import Issue
from github.IssueEvent import IssueEvent
from pydantic import BaseModel, SecretStr, validator
from pydantic_settings import BaseSettings

REMINDER_MARKER = "<!-- reminder -->"


class Reminder(BaseModel):
    message: str = "This issue will be closed automatically in 1 day if no further activity."
    delay: timedelta = timedelta(days=1)


class KeywordMeta(BaseModel):
    delay: timedelta = timedelta(days=10)
    message: str = (
        "Assuming the original need was handled, this will be automatically closed now."
    )
    remove_label_on_comment: bool = True
    remove_label_on_close: bool = False
    reminder: Optional[Reminder] = None


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


def filter_comments(
    comments: PaginatedList[IssueComment], include: Literal["regular", "reminder"]
) -> list[IssueComment]:
    if include == "regular":
        return [
            comment
            for comment in comments
            if not comment.body.startswith(REMINDER_MARKER)
        ]
    elif include == "reminder":
        return [
            comment for comment in comments if comment.body.startswith(REMINDER_MARKER)
        ]
    else:
        raise ValueError(f"Unsupported value of include ({include})")


def get_last_interaction_date(issue: Issue) -> Optional[datetime]:
    last_date: Optional[datetime] = None
    comments = filter_comments(issue.get_comments(), include="regular")
    if issue.pull_request:
        pr = issue.as_pull_request()
        commits = list(pr.get_commits())
        reviews = list(pr.get_reviews())
        pr_comments = list(pr.get_comments())
        interactions = comments + pr_comments
        interaction_dates = [interaction.created_at for interaction in interactions]
        interaction_dates.extend([commit.commit.author.date for commit in commits])
        interaction_dates.extend([review.submitted_at for review in reviews])
    else:
        interactions = comments
        interaction_dates = [interaction.created_at for interaction in interactions]
    for item_date in interaction_dates:
        if not last_date:
            last_date = item_date
        elif item_date > last_date:
            last_date = item_date
    return last_date


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


def get_last_reminder_date(issue: Issue) -> Optional[datetime]:
    """Get date of last reminder message was sent"""
    last_date: Optional[datetime] = None
    comments = filter_comments(issue.get_comments(), include="reminder")
    comment_dates = [comment.created_at for comment in comments]
    for item_date in comment_dates:
        if not last_date:
            last_date = item_date
        elif item_date > last_date:
            last_date = item_date
    return last_date


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


def send_reminder(*, issue: Issue, keyword_meta: KeywordMeta) -> None:
    assert keyword_meta.reminder is not None
    message = keyword_meta.reminder.message
    logging.info(f"Send reminder: #{issue.number} with message: {message}")
    issue.create_comment(f"{REMINDER_MARKER}\n{message}")


def process_issue(*, issue: Issue, settings: Settings) -> None:
    logging.info(f"Processing issue: #{issue.number}")
    label_strs = set([label.name for label in issue.get_labels()])
    events = list(issue.get_events())
    labeled_events = get_labeled_events(events)
    last_date = get_last_interaction_date(issue)
    last_reminder_date = get_last_reminder_date(issue)
    now = datetime.now(timezone.utc)
    for keyword, keyword_meta in settings.input_config.items():
        # Check closable delay, if enough time passed and the issue could be closed
        closable_delay = last_date is None or (now - keyword_meta.delay) > last_date
        # Check label, optionally removing it if there's a comment after adding it
        if keyword in label_strs:
            logging.info(f'Keyword: "{keyword}" in issue labels')
            keyword_event = get_last_event_for_label(
                labeled_events=labeled_events, label=keyword
            )
            # Check if we need to send a reminder
            scheduled_close_date = keyword_event.created_at + keyword_meta.delay
            need_send_reminder = False
            if keyword_meta.reminder and keyword_meta.reminder.delay:
                remind_time = (  # Time point after which we should send reminder
                    scheduled_close_date - keyword_meta.reminder.delay
                )
                need_send_reminder = (
                    (now > remind_time)  # It's time to send reminder
                    and (  # .. and it hasn't been sent yet
                        not last_reminder_date or (last_reminder_date < remind_time)
                    )
                )
            if last_date and keyword_event and last_date > keyword_event.created_at:
                logging.info(
                    f"Not closing as the last comment was written after adding the "
                    f'label: "{keyword}"'
                )
                if keyword_meta.remove_label_on_comment:
                    logging.info(f'Removing label: "{keyword}"')
                    issue.remove_from_labels(keyword)
            elif need_send_reminder:
                send_reminder(issue=issue, keyword_meta=keyword_meta)
                break
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
        github_event = PartialGitHubEvent.model_validate_json(contents)
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
