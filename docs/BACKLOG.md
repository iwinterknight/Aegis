# Backlog — Captured Work Items

Living capture of decisions, enhancements, follow-ups, calibration items, and open questions that
surface during deep dives, exercises, inspection/retrospection, and reviews — so they **convert into
real work** instead of evaporating in discussion.

**Process (binding):** the moment something worth doing surfaces, add a row here — don't wait. Review
this list at every **phase boundary** and pull `OPEN` items into the active plan (promoting `DECISION`
items to ADRs before their code is written). When an item is actioned, set it `DONE` and link the
ADR / commit / module that resolved it.

- **Status:** `OPEN` (captured) · `PLANNED` (scheduled into a phase) · `DONE` (link resolution) ·
  `DROPPED` (with reason)
- **Type:** `DECISION` (→ ADR) · `ENHANCEMENT` · `TECH-DEBT` · `CALIBRATION` · `QUESTION` · `SCOPE`

| ID | Captured | Context | Type | Item | Target | Status |
|---|---|---|---|---|---|---|
| WI-1 | 2026-06-30 | P1 ex04 retrospection | DECISION | Adopt **Pydantic v2** for the ingestion contract: canonical record models (`ClaimRecord`, `LedgerRow`), an `IngestionResult` **discriminated union** on `kind`, and per-connector **descriptor** models; validate at the connector boundary; serialize `Decimal` as string. | → **ADR-0002** when `src/` build opens (phase ④) | OPEN |
| WI-2 | 2026-06-27 | P1 ADR-0001 follow-up | CALIBRATION | Calibrate **Benford's-Law realism** of synthetic ledger amounts (uniform-random amounts don't match real ledgers). | `src/` ledger generator | OPEN |
| WI-3 | 2026-06-27 | P1 ADR-0001 follow-up | ENHANCEMENT | Real **FFIEC Call Report** connector (RSSD lookup) beyond the exercise stub — bank-specific evidence. | Holistic data expansion | OPEN |
| WI-4 | 2026-06-27 | P1 ADR-0001 follow-up | QUESTION | Confirm **XBRL coverage quirks** for bank taxonomies (us-gaap vs ffiec concepts, regulatory line items). | During `src/` ingestion build | OPEN |
| WI-5 | 2026-06-27 | P1 build plan | TECH-DEBT | Stand up **real PostgreSQL**; migrate SQLite exercise code → `psycopg` (`%s` params, `NUMERIC(20,2)`); expose as the parameterized Postgres **MCP** tool (FR-MCP-1). | Phase ④ `src/` | OPEN |
| WI-6 | 2026-06-27 | P1 ADR-0001 | ENHANCEMENT | **Liveness:** event-driven / CDC ingestion trigger emitting the same descriptors (FR-IN-3), continual live pulls. | Later phase | OPEN |
| WI-7 | 2026-06-27 | Deep dive (scope) | SCOPE | **IPO forecasting vertical** (bull/bear valuation; S-1; comps/DCF) — reframe vision to a two-vertical platform. | Post-MVP; ADR when adopted | OPEN (deferred) |
| WI-8 | 2026-06-27 | Deep dive (scope) | SCOPE | **AWS / Bedrock AgentCore** managed-cloud mirror ("Part II"). | Post-MVP capstone | OPEN (deferred) |

_Add new items at the bottom with the next `WI-n`. Keep the table the single source of truth for
"things we said we'd do." Big deferred scope items (WI-7/8) are also noted in the discussion log._
