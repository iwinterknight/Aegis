# Multi-Machine Sync (SDD + Claude Code conversation thread)

**Binding workflow** for working on Project Aegis interchangeably across two (or more) machines. It
ensures every commit, from either machine, carries **both** the SDD files **and** the Claude Code
`</>` conversation thread — by default, with no manual steps per commit.

## One-time setup per machine (required)

After cloning, from the repo root, enable the sync hooks once:

```bash
# macOS / Linux / Git Bash:
sh scripts/setup-sync.sh
```
```powershell
# Windows PowerShell:
./scripts/setup-sync.ps1
```

This sets `git config core.hooksPath .githooks` (a local setting, not stored in the repo — hence the
per-machine step) and does an initial restore of any transcripts already in the repo into
`~/.claude/`. **Until you run this on a machine, that machine's commits will NOT capture the thread.**

## What syncs, and how

| Item | Mechanism | Synced? |
|---|---|---|
| **SDD files** (spec, ADRs, primers, exercises, build log, `CLAUDE.md`, …) | ordinary tracked repo content | ✅ via normal git |
| **Claude Code conversation thread** (`*.jsonl`) | `pre-commit` copies `~/.claude/projects/<slug>/*.jsonl` → `conversations/` and stages them | ✅ automatically on every commit |
| **Restore on the other machine** | `post-merge` / `post-checkout` copy `conversations/*.jsonl` → `~/.claude/projects/<slug>/` after pull/clone | ✅ (only files missing locally, so a live local transcript is never clobbered) |

The `<slug>` is how Claude Code names a project's folder: its absolute path with `:` `/` `\` replaced
by `-` (e.g. `C:/Users/thewi/Documents/Projects/Aegis` → `C--Users-thewi-Documents-Projects-Aegis`).
The hooks compute it from the repo path, so they work on each machine without configuration.

## Daily workflow

1. **Sit down:** `git pull` (restores any new thread snapshots into `~/.claude`).
2. **Work** in Claude Code as normal. Resume context via **Option A**: open the workspace and tell
   Claude *"read `docs/PROJECT_STATE.md` and continue"* — `CLAUDE.md` auto-loads the project brain.
3. **Before you stop:** `git push` (or ask Claude to commit + push). The pre-commit hook captures the
   latest thread into the commit automatically.

## Honest limitations

- **The committed transcript is a snapshot at commit time.** The current session keeps being written
  after the commit, so the last few exchanges land in the *next* commit. → **Push before you stop.**
- **Cross-machine resume gives the last-committed snapshot**, not a live tail. For the freshest copy
  of a given thread, resume it on the machine where it was last active.
- **Repo growth:** transcripts are a few MB and re-committed as they grow. Fine for now; if it gets
  heavy, migrate `conversations/*.jsonl` to Git LFS.
- **Privacy:** transcripts can contain anything from a session — **keep the repo private.**
