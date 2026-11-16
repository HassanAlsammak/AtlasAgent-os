"""Human-confirmed draft pull request CLI."""
from __future__ import annotations
import argparse
from .github_pr import DraftPR, create_draft_pr


def main():
    p = argparse.ArgumentParser(description="Create a GitHub draft PR from existing branches")
    p.add_argument("--repo", required=True, help="owner/repo")
    p.add_argument("--head", required=True)
    p.add_argument("--base", default="main")
    p.add_argument("--title", required=True)
    p.add_argument("--body", required=True)
    args = p.parse_args()
    pr = DraftPR(args.repo, args.head, args.base, args.title, args.body)
    print("Proposed DRAFT PR:", pr.payload())
    if input("Create this draft PR? Type YES: ").strip() != "YES":
        print("Cancelled")
        return
    print(create_draft_pr(pr, confirm=True))


if __name__ == "__main__":
    main()
