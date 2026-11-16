# Draft pull request workflow

AtlasAgent OS supports **explicitly approved** draft PR creation from two
existing GitHub branches. It does not write code, push commits, review changes,
merge PRs, or independently execute a complete coding task.

Set a GitHub fine-grained token with minimal pull-request write permission
for the target repository, then run:

```powershell
$env:GITHUB_TOKEN="your-github-token"
python -m atlasagent.github_pr_cli --repo OWNER/REPO --head feature/demo --base main --title "Feature" --body "Changes and tests"
```

The CLI displays the payload and asks for `YES` before any network call.
It always creates **draft** pull requests. Never put tokens in source files.
Revoke leaked tokens immediately. Human review and merge remain separate.
