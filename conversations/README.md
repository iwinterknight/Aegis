# `conversations/` — Claude Code thread (auto-managed)

**Do not hand-edit.** This folder is written automatically by the git sync hooks
(`.githooks/pre-commit`). It holds copies of this project's Claude Code conversation transcripts
(`*.jsonl`), so the `</>` Code thread travels with the repo and is available on every machine.

- **Captured** into this folder by the `pre-commit` hook on every commit.
- **Restored** into `~/.claude/projects/<slug>/` by the `post-merge` / `post-checkout` hooks after a
  pull/clone, so Claude Code can list/resume them locally.

Setup and full details: [`docs/MULTI_MACHINE_SYNC.md`](../docs/MULTI_MACHINE_SYNC.md).

> **Privacy:** these transcripts can contain anything discussed in the session. Keep this repository
> **private**.
