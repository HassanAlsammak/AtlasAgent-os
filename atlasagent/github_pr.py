"""Minimal opt-in GitHub draft PR creation. No merge, no code execution."""
from __future__ import annotations
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,199}$")


@dataclass(frozen=True)
class DraftPR:
    repository: str
    head: str
    base: str
    title: str
    body: str

    def validate(self) -> None:
        if not _REPO.fullmatch(self.repository):
            raise ValueError("Expected owner/repo")
        for branch in (self.head, self.base):
            if not _BRANCH.fullmatch(branch) or ".." in branch or "//" in branch or branch.endswith(("/", ".")):
                raise ValueError("Invalid branch")
        if self.head == self.base:
            raise ValueError("Head and base must differ")
        if not 1 <= len(self.title.strip()) <= 200 or not 1 <= len(self.body.strip()) <= 10000:
            raise ValueError("Title/body missing or too long")

    def payload(self) -> dict:
        self.validate()
        return {"title": self.title, "head": self.head, "base": self.base,
                "body": self.body, "draft": True, "maintainer_can_modify": True}


def create_draft_pr(request: DraftPR, *, token: str | None = None,
                    confirm: bool = False, opener=None) -> str:
    """Explicit confirmation required; token has repository PR write permissions.

    This function creates ONLY a draft PR from existing branches.
    """
    payload = request.payload()
    if not confirm:
        raise PermissionError("Explicit confirmation required to create a draft PR")
    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is required")
    owner, repo = request.repository.split("/")
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28"},
        method="POST")
    opener = opener or urllib.request.urlopen
    with opener(req, timeout=20) as response:
        result = json.load(response)
    link = result.get("html_url")
    if not isinstance(link, str) or not link.startswith("https://github.com/"):
        raise ValueError("GitHub returned unexpected PR URL")
    return link
