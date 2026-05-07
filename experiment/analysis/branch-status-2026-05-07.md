# Branch Status Check

Date: 2026-05-07

User reported that the Codex UI still appeared to show `dev` even after switching to `experiment`.

Terminal checks from `/Users/cyan/Project/novilab`:

```text
git status --short --branch
## experiment
?? physical_ai_agent_experiment_guidance.md

git branch --show-current
experiment

git rev-parse --abbrev-ref HEAD
experiment

git symbolic-ref -q HEAD
refs/heads/experiment

git worktree list --porcelain
worktree /Users/cyan/Project/novilab
HEAD ad1b0a28ede78e20a5ae04278db0d6fd42e60239
branch refs/heads/experiment
```

Conclusion: the repository worktree is actually on `experiment`. If Codex still displays `dev`, it is likely a UI/thread metadata cache issue rather than a Git state issue.

