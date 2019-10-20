import logging
from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel, BaseSettings, SecretStr

from github import Github
from github.Issue import Issue
from github.IssueComment import IssueComment
from github.NamedUser import NamedUser


class KeywordMeta(BaseModel):
    keyword: str
    delay: timedelta = timedelta(days=10)
    users: List[str] = []
    message: str = "Assuming the original issue was solved, this issue will be automatically closed now."


class Settings(BaseSettings):
    input_config: List[KeywordMeta]
    github_repository: str
    input_token: SecretStr


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    logging.info(f"Using config: {settings.json()}")
    g = Github(settings.input_token.get_secret_value())
    repo = g.get_repo(settings.github_repository)
    owner: NamedUser = repo.owner

    issue: Issue
    for issue in repo.get_issues(state="open"):
        logging.info(f"Processing issue: #{issue.number}")
        last_comment: IssueComment = None
        comment: IssueComment
        for comment in issue.get_comments():
            if not last_comment:
                last_comment = comment
            elif comment.created_at > last_comment.created_at:
                last_comment = comment
        if not last_comment:
            continue
        user: NamedUser = last_comment.user
        for keyword_meta in settings.input_config:
            if (
                f"<!-- issue-manager: {keyword_meta.keyword} -->" in last_comment.body
                and (datetime.utcnow() - keyword_meta.delay)
                > last_comment.created_at
                and last_comment.user.login in keyword_meta.users + [owner.login]
            ):
                logging.info(f"Clossing issue: #{issue.number} with message: {keyword_meta.message}")
                issue.create_comment(keyword_meta.message)
                issue.edit(state="closed")
                break
