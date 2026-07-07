# ADR-0002: Pydantic v2 as the canonical ingestion data contract

- **Status:** Accepted
- **Date:** 2026-07-07
- **Relates to:** FR-IN-2, FR-IN-3, FR-IN-4, FR-IN-5, FR-DATA-5, NFR-CORR-1, NFR-PROV, NFR-MAINT, SG-1, §10.1, §10.3
- **Extends:** [ADR-0001](0001-structured-first-ingestion-and-source-connectors.md) · **Resolves:** WI-1

## Context

ADR-0001 established the `SourceConnector` contract — `resolve(descriptor) → fetch → normalize →
**emit canonical records**` — but deliberately left *what a canonical record actually is* unspecified.
The Phase 1 exercises (01–04) carried records as ad-hoc `dict`s and tuples. That is fine for a
notebook; it is a liability in `src/`, because a bare `dict` makes **no guarantees**: any field can be
missing, any type can be wrong, and a monetary value can silently arrive as a binary `float`. The
error surfaces far downstream (a bad SG-1 reconciliation, a corrupted row in the store) rather than at
the source, which is the most expensive place for a data bug to appear.

As step ④ (the `src/` build) opens, we must choose the concrete representation that crosses the
boundary between the **untrusted external world** (SEC XBRL, the synthetic ledger, later FFIEC Call
Reports) and the **trusted Aegis interior** (storage, agents, evaluation). Forces:

1. **Untrusted input must be validated exactly once, at one boundary** — not re-checked defensively at
   every call site, and not trusted blindly.
2. **Money must be exact.** Our binding rule is *money is always `Decimal`*; JSON has no decimal type,
   so serialization must preserve exact cents (a `float` round-trip corrupts them).
3. **One connector can emit different shapes** (a batch of SEC claims vs. a synthetic ledger), and the
   consumer must be able to tell which, safely.
4. **Provenance and reproducibility** (NFR-PROV, NFR-CORR-1) require each record and each run to carry
   structured source metadata / descriptor, not free-form strings.
5. **Maintainability** (NFR-MAINT): when the SEC renames an XBRL field, the fix must live in one place.

## Decision

Adopt **Pydantic v2** (a Rust-cored Python data-validation library) as the canonical ingestion
contract. The connector boundary is defined structurally by the following models.

1. **Canonical record models.** `ClaimRecord` (one fact pulled from SEC XBRL — concept, value,
   period, unit, source provenance) and `LedgerRow` (one row of the anchored-synthetic ledger —
   amount, date, account, anchor reference). These are the concrete "canonical records" ADR-0001
   referred to. They are the **anti-corruption layer**: external field names/quirks are mapped into
   Aegis's domain vocabulary here and nowhere else.

2. **`IngestionResult` as a discriminated (tagged) union on `kind`.** A connector run returns one of a
   fixed set of shapes — e.g. `kind="claims"` carrying `ClaimRecord`s, `kind="ledger"` carrying
   `LedgerRow`s — distinguished by a literal `kind` tag. Consumers branch on `kind` with the type
   system and the validator both guaranteeing exhaustiveness. This is a sum type expressed in code.

3. **Per-connector descriptor models.** The ADR-0001 source descriptor (`{company, lookback, filing
   types, …}`) becomes a typed model per connector type (`sec-xbrl`, `simulated-ledger`, …), so the
   provenance root of every run (NFR-PROV) is validated and re-runnable (NFR-CORR-1).

4. **Validation fires at model construction, at the connector boundary.** Raw data is parsed *into*
   these models the moment a connector produces it; an invalid record is rejected there, loudly, with
   a field-level error — never admitted as a half-valid `dict`. ("Parse, don't validate" — after the
   boundary the *type* is the proof of validity; illegal states are unrepresentable.)

5. **`Decimal` money, serialized as string.** Every monetary field is typed `Decimal`; models
   serialize `Decimal` to a JSON **string** to preserve exact cents. Floats are never used for money.

## Consequences

- **Errors move to the source.** A malformed SEC payload or a mis-summed ledger fails at ingestion
  with a precise field error, not three layers downstream — the cheapest place to catch it.
- **SG-1 gets typed operands.** Seeded-discrepancy detection compares `ClaimRecord.value` against a
  `LedgerRow` sum, both guaranteed `Decimal` and well-formed — the comparison is trustworthy by
  construction.
- **One place to absorb change** (NFR-MAINT): an SEC field rename or a taxonomy quirk is a one-line
  model edit; call sites are untouched.
- **Provenance is structural** (NFR-PROV, NFR-CORR-1): descriptors and source metadata are validated
  models, so a saved run re-pulls identical, self-describing data.
- **Serialization boundary is explicit:** models own their JSON shape (Decimal-as-string), so the
  store layer (SQLite now, PostgreSQL `NUMERIC(20,2)` at WI-5) receives exact values.
- **Runtime dependency added:** `pydantic>=2` enters `src/`'s dependency set (the exercises stay
  stdlib-first; this is a `src/`-only adoption). Validation has a small per-record cost, mitigated by
  v2's compiled Rust core (`pydantic-core`).
- **Contract, not just types:** because construction validates, the models double as the ingestion
  test surface — a fixture that fails to construct is a caught regression.

## Alternatives considered

- **Bare `dict` / `TypedDict` (status quo from the exercises).** Rejected: `TypedDict` gives
  *static* hints only — **zero runtime enforcement**. Nothing stops a wrong-typed or missing field at
  the actual boundary, which is exactly where untrusted data enters.
- **`@dataclass` (stdlib).** Rejected as the boundary type: dataclasses store fields but do **not
  validate or coerce** them, have no built-in discriminated-union support, and no `Decimal`-aware
  serialization. Good for pure interior value objects; wrong tool for an untrusted boundary.
- **`marshmallow` / `attrs` + validators.** Rejected: `marshmallow` separates schema from the object
  (two artifacts to keep in sync); `attrs` needs bolted-on validators and lacks first-class tagged
  unions and serialization. Pydantic v2 unifies model, validation, union, and serialization in one
  declaration.
- **Pydantic v1.** Rejected: v2 is the current standard — faster (Rust core), with native
  discriminated unions and a cleaner serialization model; no reason to adopt the legacy line for new
  code.
- **Hand-rolled validation functions.** Rejected: reinvents field-level error reporting, coercion, and
  serialization; scatters checks; violates the single-boundary principle this ADR exists to enforce.