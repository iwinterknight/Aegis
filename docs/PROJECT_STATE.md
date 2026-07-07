# Project State — Start Here (especially on a new machine)

This file is the portable entry point. The repo is self-sufficient for continuing development; read
this, then the linked docs, and you have the full context.

## What this project is

Project Aegis — a local-first, multi-agent M&A due-diligence platform — built via **Spec-Driven
Development** as a deep learning exercise. Read [`specs/Project_Aegis_System_Specification.md`](specs/Project_Aegis_System_Specification.md)
(the source of truth) and [`00_OPERATING_MODEL.md`](00_OPERATING_MODEL.md) (how we build & learn).

## How we work (the loop)

Every module runs: ① Deep Dive (discussion → `primers/`, `discussion-notes/`) → ② Guided Exercises
(`../learning/exercises/`) → ③ Checkpoint Quiz (`../learning/quizzes/`) → ④ SDD Build (`../src/`) →
⑤ Build Summary (`build-summaries/`). Git: branch per phase, conventional commits citing FR-IDs,
commit/push only when asked. Full detail in [`00_OPERATING_MODEL.md`](00_OPERATING_MODEL.md).

## Where we are right now (2026-07-07)

- **Phase 1 — Data & Storage.** Deep dives done: SDD methodology, financial domain. Data architecture
  decided in **[ADR-0001](adr/0001-structured-first-ingestion-and-source-connectors.md)** (structured-first
  XBRL + `SourceConnector` contract + anchored-synthetic ledger); spec is at **v4.4**.
- **Loop steps ②–③ complete:** Phase 1 exercises **01–04** authored, with reference solutions, all
  verified green (SEC `companyfacts` claims pull → anchored Faker ledger + seeded discrepancy → SQLite
  evidence store + parameterized SQL injection demo → the `SourceConnector` contract; SG-1 works
  end-to-end). The **③ checkpoint quiz** is written (`learning/quizzes/phase-1-data-storage/`). The
  **assessment ladder** (midterm WI-11, final exam WI-12) is captured in the operating model.
- **Glass-Box Build protocol adopted** (binding, in `00_OPERATING_MODEL.md` + `CLAUDE.md`): step ④ is
  built one *teachable unit* at a time through Concept Brief → Build Narration → **interactive**
  objective→func→syntax walkthrough (Claude stops for Sunit's syntax questions per part) → Command Gate.
- **④ SDD Build in progress.** **ADR-0002** accepted (Pydantic v2 ingestion contract, resolves WI-1).
  **Unit 1 — `ClaimRecord`** built through the full Glass-Box loop and **tested green** (`src/aegis/
  ingestion/models.py`; `tests/ingestion/test_claim_record.py`, 20 pytest cases). Dev env: `.venv` +
  `requirements-dev.txt` (pydantic, pytest); `pytest.ini` puts `src/` on the path. WI-13 captured
  (bitemporal fact retention + restated-fact selection resolver).
- **Next (RESUME HERE):** **Unit 2 — `LedgerRow`** (the ledger side of SG-1) through the Glass-Box
  loop — will surface the shared-provenance/DRY question and lead into **`IngestionResult`** (the
  `kind`-discriminated union) and the per-connector descriptors. Then the `sec-xbrl` connector,
  SQLite → PostgreSQL (WI-5), Postgres MCP module (WI-9). Finish with **⑤ the Phase 1 build summary**.
- On resume: greet, then start Unit 2 (`LedgerRow`) at beat ① (Concept Brief). Check `docs/BACKLOG.md`
  for the captured work items (`WI-n`) to fold into the `src/` build.

See [`BUILD_LOG.md`](BUILD_LOG.md) for the full chronology and [`discussion-notes/phase-1-data-storage.md`](discussion-notes/phase-1-data-storage.md)
for the running discussion log.

## Environment / setup on a fresh machine

```bash
git clone https://github.com/iwinterknight/Aegis.git && cd Aegis
sh scripts/setup-sync.sh                              # ONCE per machine: enable thread sync hooks
python -m venv .venv && . .venv/Scripts/activate      # Windows; use bin/activate on macOS/Linux
pip install -r learning/exercises/phase-1-data-storage/requirements.txt   # currently just: faker
```

**Multi-machine:** `git pull` when starting, `git push` before stopping/switching machines. Every
commit auto-includes the SDD files and the Claude Code thread. See [`MULTI_MACHINE_SYNC.md`](MULTI_MACHINE_SYNC.md).
Exercise 01 is stdlib-only; 02–04 need Faker. SEC calls need internet (offline fallbacks included).

- **Compute:** local dev = laptop RTX 3080 Ti (16 GB, Ampere); heavy ML work = Google Colab A100.
- **Database:** exercises use stdlib `sqlite3` as a Postgres stand-in. Real PostgreSQL is stood up at
  the `src/` build (Phase 1 step ④).

## Note on assistant memory

Claude's persistent memory lives outside this repo (`~/.claude/...`) and does **not** travel via git.
On a new machine, this file plus `docs/` are the portable source of truth — the assistant reconstructs
its working memory from them.
