# ADR-0001: Structured-first ingestion, the SourceConnector contract, and the anchored-synthetic ledger

- **Status:** Accepted
- **Date:** 2026-06-27
- **Relates to:** FR-IN-1, FR-IN-2, FR-IN-3, FR-IN-4 (new), FR-IN-5 (new), FR-DATA-5, NFR-CORR-1, P4, §10.1, §10.3

## Context

Phase 1 (Data & Storage) must deliver the SG-1 path: pull a real filing's claimed figure and
reconcile it against a ledger. Three forces shaped the design during the Phase 1 data discussion:

1. **The public/private waterline.** A public company's filings (the *claims* layer) are real,
   live, and free; its transaction-level general ledger (the *evidence* layer) is MNPI and never
   public. So claims can be real data; evidence must be simulated until a lawful real ledger is
   provided (a diligence data room).
2. **"Point-and-pull" vs. pipeline-sprawl.** The desired UX is to point the system at a source
   (which company, how many years, which forms) and have it pull — but a bespoke pipeline per source
   does not scale as sources multiply (banks → other sectors → contracts → call reports).
3. **Measure before optimizing (P4).** Document retrieval (RAPTOR/PageIndex) is heavy and belongs to
   Module 2 / Phase 3. Phase 1 should not build it prematurely.

## Decision

We will adopt three coupled decisions.

1. **Structured-first ingestion via XBRL.** The primary claims source is the SEC's structured XBRL
   data (the `companyfacts` and `frames` APIs, and the bulk Financial Statement Data Sets), not
   document parsing. This delivers every reported financial figure as clean JSON, deterministically,
   which is sufficient for SG-1 reconciliation. Raw filing documents are *cached* at ingestion but
   **no document retrieval is built in Phase 1** — that is deferred to Module 2 (Phase 3), where the
   qualitative grounding quote and the Legal facet justify it. Industry-standard practice is honored:
   the *number* comes from XBRL; the *quote* comes from the document.

2. **The `SourceConnector` contract + declarative descriptor.** All ingestion goes through a uniform
   contract. A **source descriptor** (`{company, lookback window, filing types, …}`) is resolved by a
   **connector** implementing one interface: `resolve(descriptor) → fetch → normalize → emit
   canonical records`. There is one connector per source *type* (`sec-xbrl`, `sec-document`,
   `simulated-ledger`, `rulebook`; later `ffiec-callreport`, `contract-corpus`). Adding a source is a
   new adapter, not a new pipeline. The descriptor is human-readable, reproducible, and re-runnable;
   it is the provenance root of a run and gives NFR-CORR-1 reproducibility for free.

3. **The anchored-synthetic ledger.** The simulated ledger (Faker) is *anchored to real claimed
   figures*: pull the real reported value `$X` from XBRL, then generate transactions that sum to `$X`
   (clean) or to `$Y ≠ $X` (a seeded discrepancy with a known delta). Realism is cued from real
   public proxies — open-source ERP charts of accounts (ERPNext/Odoo/GnuCash), realistic
   distributions/dates/counterparties, and Benford's-Law-conforming amounts. This keeps the evidence
   synthetic but reconcilable against genuinely-reported numbers, and means Aegis owns its evaluation
   ground truth by construction.

## Consequences

- **Easier:** SG-1 becomes a deterministic, parse-free pull + sum + compare. The UX is a compose
  form (search → scope → pull), not a catalog. New sources onboard cheaply behind the contract.
- **Reproducible:** a saved descriptor re-pulls identical data (NFR-CORR-1).
- **Deferred, not dropped:** document retrieval is postponed to Phase 3 (P4); we cache source docs
  now so the grounding layer can be added without re-fetching.
- **Constraints accepted:** XBRL omits qualitative narrative and legal-clause text — Phase 1
  findings are numeric/reconciliation-shaped; grounding quotes arrive with Module 2.
- **Liveness deferred:** batch pull is primary; a later scheduler/CDC (FR-IN-3) emits the *same*
  descriptors, so liveness is an add-on, not a redesign.
- **Follow-up:** calibrate Benford realism; decide whether FFIEC Call Reports become a bank-specific
  connector; confirm XBRL coverage quirks for bank taxonomies during the exercises.

## Alternatives considered

- **Document-first (parse 10-K HTML/PDF up front).** Rejected for Phase 1: heavy, brittle, and
  unnecessary for reconciliation; it front-loads Module 2 complexity against P4.
- **Bespoke pipeline per source.** Rejected: does not scale as sources multiply; the connector
  contract is the scaling answer.
- **A pre-rendered catalog/dashboard of all companies.** Rejected: the EDGAR universe is searched
  live (typeahead → CIK); compose-don't-browse is simpler and more general.
