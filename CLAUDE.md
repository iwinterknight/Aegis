# CLAUDE.md — Project Aegis

Auto-loaded by Claude Code on any machine. This is the **portable project brain**: reading this plus
[`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) restores full working context. (Claude's per-machine
`~/.claude` memory does **not** sync across machines — this committed file is the source of truth, so
the assistant behaves the same on every system that clones the repo.)

## What this is

Project Aegis — a local-first, multi-agent **M&A due-diligence platform** — built via **Spec-Driven
Development (SDD)** as a deep **learning exercise**. Source of truth:
[`docs/specs/Project_Aegis_System_Specification.md`](docs/specs/Project_Aegis_System_Specification.md).

## Who I'm working with

**Sunit** — strong software engineer, newer to ML/LLM infrastructure. **Learning-first:** go deep on
internals (attention/KV-cache/serving, RAG, agents, fine-tuning) to enterprise standard; keep general
SWE light. **Expand every acronym on first use.** Decoder for spec IDs:
[`docs/reference/requirement-id-glossary.md`](docs/reference/requirement-id-glossary.md).

## How we work — the 5-phase loop (full detail: `docs/00_OPERATING_MODEL.md`)

Per module: **① Deep Dive** (discussion → `docs/primers/`, `docs/discussion-notes/`) → **② Guided
Exercises** (`learning/exercises/` — Coursera-style, marked `# YOUR CODE HERE` gaps, runnable, with
verified solutions in `learning/solutions/`) → **③ Checkpoint Quiz** (`learning/quizzes/`) → **④ SDD
Build** (`src/`) → **⑤ Build Summary** (`docs/build-summaries/`).

**Do not start ④ (build) until Sunit signals he's clear on ①–③.**

## Discipline (binding)

- **SDD:** the spec is the source of truth; code/plans/tasks/tests trace to FR/NFR/P IDs.
- **Decisions become ADRs** (`docs/adr/`) *before* code.
- **Git:** branch per phase; conventional commits citing FR-IDs; **commit/push only when asked**.
  Multi-machine rule: **pull when starting, push before stopping**, so the two systems never diverge.
- **Exercises:** stdlib-first and runnable; money is always `Decimal`; verify solutions run green
  before handing over.
- **Keep living docs current:** `docs/BUILD_LOG.md` and the active `docs/discussion-notes/*` log get
  updated as we go; fold discussion salients into the build summary at module end.
- **Teaching reporting is top-down:** objective → functional → syntax-level.

## Current state (live detail in `docs/PROJECT_STATE.md` + `docs/BUILD_LOG.md`)

**Phase 1 — Data & Storage.** Deep dives done (SDD methodology, financial domain). **ADR-0001** set the
ingestion design (structured-first SEC XBRL + `SourceConnector` contract + anchored-synthetic ledger);
spec at **v4.4**. Exercises **01–04 complete** and verified (SG-1 seeded-discrepancy detection works
end-to-end). **Next:** ③ checkpoint quiz → ④ build `src/` (notebook functions → tested modules;
SQLite → PostgreSQL).

## Compute

Local dev: laptop **RTX 3080 Ti, 16 GB** (Ampere). Heavy ML: **Google Colab A100**. Scale demos to fit
the laptop but always teach the production-scale mechanism and say when something is scaled down.

## Resuming on another machine

`git clone` → read `docs/PROJECT_STATE.md` → continue. The live conversation transcript itself does not
sync via git (it lives in `~/.claude/projects/…`); this file + `docs/` carry the context instead.
