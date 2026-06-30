# Phase 1 — Data & Storage · Exercises

Run `pip install -r requirements.txt` first (01 is stdlib-only; 02+ need Faker).

- ✅ `01_sec_companyfacts_pull.ipynb` — structured-first SEC XBRL claims pull; filing/fact anatomy [FR-IN-1].
- ✅ `02_faker_seeded_ledger.ipynb` — deterministic, anchored synthetic ledger + seeded discrepancy +
  reconciliation [FR-IN-2, SG-1].
- ✅ `03_postgres_evidence_store.ipynb` — schema-as-evidence-store; parameterized SQL reconciliation +
  SQL-injection demo [FR-MCP-1]. (SQLite stand-in; real Postgres at `src/` build time.)
- ✅ `04_source_connector_contract.ipynb` — the `SourceConnector`/descriptor contract; registry +
  dispatch; canonical envelope; SG-1 through the contract; add-a-source-in-6-lines [FR-IN-4/5].

**Phase 1 exercise set complete (01–04).** Next: checkpoint quiz, then the real `src/` build.
