# Discussion Notes — Phase 1 (Data & Storage)

Live log of salient points from our Phase 1 deep dive. Distilled into the build summary at the end.

## Deep Dive #1 — Spec-Driven Development (Stop 1)

- **SDD inverts code-first.** A versioned spec is the source of truth; code, plans, tasks, tests,
  and evals are *derived artifacts* that must trace back to it. Especially important for
  non-deterministic AI systems where behavior isn't captured by any single file.
- **Traceability chain:** Principle → Requirement → Plan → Task → Code → Test → Trace. Aegis's spec
  already uses addressable IDs (`FR-IN-1`, `SG-1`, `P2`) — that's the spine, not decoration.
- **Rhythm:** Specify (what/why) → Plan (how, architecture altitude) → Tasks (small, traceable) →
  Implement (commit per task). Don't skip upward; untraceable code is a smell.
- **Industry context:** GitHub Spec Kit, Amazon Kiro, "specs as the new source code" — LLMs make
  *generating* code cheap, so *precisely specifying intent* becomes the scarce skill. In regulated
  settings the spec→code→test matrix is often an audit requirement.
- **MLOps tie-in:** SDD's "trace to a versioned spec" is the same instinct as reproducibility
  (NFR-CORR-1) and regression-gated change (P8) — nothing changes behavior without a written,
  testable reason.

## Scope discussion — two proposed additions (PENDING DECISION, 2026-06-27)

Sunit proposed two scope additions. Analysis captured here; no spec/ADR changes made yet.

### A. IPO forecasting as a second vertical (bull/bear) — recommend ADOPT, build second
- ~80% reuse: forecasting, bull/bear isolation (FR-PROJ-3), deterministic sandbox (FR-PROJ-1),
  four-tier explainability, web grounding (M7) already exist.
- Genuinely new: S-1/S-1A ingestion (same EDGAR pipe — trivial); a deterministic **valuation/comps
  layer** in the sandbox (EV/Rev, EV/EBITDA, P/E, simple DCF, dilution/lockup) with bull/bear as
  parameter sets; a comparable-company evidence layer (via existing Postgres MCP); an Offering facet
  or extended Forecasting agent.
- **Hard part:** evaluation ground truth. M&A audit owns truth by construction (seeded discrepancies);
  IPO forecasting is probabilistic → Module 6 eval must score *reasoning/grounding/determinism/
  reproducibility*, not "did it predict the price." Bounded spec change, not a redesign.
- **Constitution check:** stays inside Non-Goal #1 (not investment advice) by being *scenario analysis
  with explainability*, never a buy/price-target recommendation — same discipline bull/bear already uses.
- **Recommendation:** reframe vision (§2/§4) to a two-vertical corporate-finance event-intelligence
  platform — *Diligence* (M&A) + *Offering* (IPO). Build M&A MVP first, add IPO as the cheap second
  vertical (validates the architecture). Spec impact: §2/§4/§5 + new FRs + module extension + ADR.

### B. Mirror the build on AWS with Bedrock AgentCore — recommend ADOPT as post-MVP capstone
- Clean component mapping: LangGraph→AgentCore Runtime; MCP→Gateway; tiered memory→AgentCore Memory;
  sandbox→Code Interpreter; web agent→Browser; tracing→Observability; gate→Identity+IAM+Guardrails;
  Postgres→RDS/Aurora; Qdrant→OpenSearch/pgvector/Knowledge Bases; training→SageMaker/Custom Model Import.
- **Caveat A — reframes P1:** "never leaves the host" → "never leaves your controlled cloud boundary"
  (VPC/PrivateLink/no-train/GovCloud). Legit enterprise posture, but a *variant constitution* — state it.
- **Caveat B — M1 learning:** managed Bedrock hides KV-cache internals (you get prompt caching as a
  black box). To keep PagedAttention/RadixAttention/LMCache learning, self-host vLLM/SGLang on
  SageMaker/EC2 and benchmark managed-vs-self-hosted (mirrors §11.6's sovereign-vs-provider philosophy).
- **Why cheap:** P7 (OpenAI-compatible router) + MCP contracts make it largely translation + new ops
  (IaC/CDK/Terraform, IAM, VPC, CloudWatch), not re-architecture. Verify current AgentCore feature
  surface when scoping (fast-moving product).
- **Recommendation:** "Part II — Managed Cloud Deployment" capstone after the sovereign build.

### Overall sequence proposed: M&A MVP → IPO vertical → AWS/AgentCore mirror.

## Deep Dive #1 — SDD methodology Q&A (Stop 1 cont.)

- **Sync on spec change = handled like a schema migration:** impact-analysis via requirement IDs
  (`git log --grep=FR-XXX`), propagate spec→plan→tasks→code/tests, §7 acceptance tests are the
  tripwire, AI can patch derived artifacts but they're human/test-gated. Sync is discipline+tooling,
  not automatic; spec-reality drift is the #1 risk.
- **SDD vs TDD/BDD:** different altitudes, they compose. TDD = unit/test-first; BDD = feature/Given-
  When-Then; SDD = whole-system intent in a versioned spec with plan/tasks/code/**evals** derived.
  SDD *contains* TDD/BDD (deterministic parts get asserts; §7 is BDD-flavored) and adds **evals** as a
  first-class artifact for non-deterministic parts (RAGAS thresholds, gold labels, temp-0 + paired
  significance) — the MLOps core that classic TDD/BDD lack.
- **Where SDD breaks down:** spec-reality drift; waterfall-in-disguise; specifying the un-specifiable
  (specify constraints/acceptance bands, not exact LLM outputs); granularity trap; misplaced trust in
  LLM-derived artifacts (gates non-negotiable); overkill on small/throwaway work.

## Deep Dive #2 — Financial domain (Stop 2)

Full primer written: `../primers/financial-domain-ma-due-diligence.md`. Salient points:

- **M&A due diligence** = the "trust but verify" investigation phase of a deal; exists to reduce
  buyer-seller **information asymmetry**. Hidden liabilities = deal-killers / price levers.
- **Four facets:** Accounting (MVP), Legal, Operational, Compliance — each has a **claims** layer
  (filing asserts) vs an **evidence** layer (granular records). **Auditing = cross-checking the two.**
- **Filings (claims):** 10-K (annual, audited), 10-Q (quarterly, unaudited), 8-K (events), S-1 (IPO).
  Three statements: Balance Sheet (Assets = Liabilities + Equity), Income Statement, Cash Flow.
  Footnotes/MD&A hold the real risk (drives Module 2 retrieval).
- **General ledger (evidence)** + **double-entry** (debits = credits, a checksum). Statements are a
  `GROUP BY SUM` of the GL. SG-1 = sum the ledger, compare to the filing's claimed aggregate.
- **CRITICAL DATA CONSTRAINT:** claims (filings) are public/real/live & free (EDGAR); the GL is
  **never public** (MNPI, only in a data-room under NDA) → spec *simulates* the ledger (FR-IN-2),
  ingestion source-agnostic (FR-DATA-5). This shapes the entire data discussion.
- **Seeded discrepancy** = deliberately planted landmine → owned ground truth for eval (§11.6).
- **Rulebooks:** GAAP / IRS codes → stable → CAG prefix cache, not RAG.
- **IPO vertical** = valuation not audit: comps (EV/Revenue, EV/EBITDA, P/E), DCF; bull/bear =
  assumption sets through the deterministic sandbox.

## Data discussion — DECISIONS (Sunit-driven, 2026-06-27)

1. **Corpus scope:** Banks first. Batch-pull by descriptor `{company, lookback window (yrs+mos from
   today), filing types}`. Start one bank, short window. **Liveness deferred** — later a scheduler /
   CDC (FR-IN-3) emits the *same* descriptors, so batch-now costs nothing architecturally. Bank
   filings are the complex end (reg capital, loan-loss provisions) — good stress test.
2. **Structured-first (~95%):** Pull the entire **claims** layer from **XBRL** via SEC
   `companyfacts` API (also `frames`, bulk Financial Statement Data Sets) — clean JSON, no parsing,
   deterministic → perfect for SG-1 reconciliation. **Caveat:** XBRL has numbers + some tagged
   footnote facts but NOT qualitative narrative (risk factors, MD&A) or grounding quotes / legal
   clauses. Industry standard = *number from XBRL, quote from document*. So: cache raw filing docs
   but build NO document retrieval in Phase 1 — that's Module 2 (RAPTOR/PageIndex) in Phase 3 (P4).
   **Bonus (banks):** FFIEC Call Reports / FR Y-9C = granular public regulatory data, optional
   richer source via the same connector contract.
3. **Simulated ledger (Faker), anchored to real claims:** No real public-company GL exists (MNPI).
   Design: pull real claimed `$X` from XBRL → Faker generates transactions summing to `$X` (clean) or
   `$Y≠$X` (seeded discrepancy, known delta). Realism cues from real public proxies: open-source ERP
   chart-of-accounts (ERPNext/Odoo/GnuCash), realistic distributions/dates/counterparties, and
   **Benford's Law** (forensic technique — also a future exercise + detector). Later facets: CUAD
   (Legal), enforcement DBs (Compliance).
4. **Point-and-pull architecture (RECOMMENDED, mockup shown):**
   - **Engineering:** a uniform `SourceConnector` contract — `resolve(descriptor)→fetch→normalize→
     emit canonical records`. One adapter per source *type* (`sec-xbrl`, `sec-document`,
     `simulated-ledger`, `rulebook`, later `ffiec-callreport`, `contract-corpus`). Adding a source =
     new adapter, not new pipeline+UI. The **descriptor is the uniform contract** (axis 4) and
     generalizes to all modules (§10.2 uniform ingestion paths).
   - **UX:** compose, don't browse. Live typeahead resolves company→CIK against EDGAR; user sets
     window + forms. Descriptor is human-readable, reproducible (NFR-CORR-1), re-runnable. Maps to
     §13.2 "report configuration triggers" (+ "document drop nodes" for ad-hoc docs). No mega-catalog.
5. Freshness: covered by (1) — batch now, live later.

> "GO" given 2026-06-27 → **DONE**: ADR-0001 accepted; spec bumped to v4.4 (FR-IN-1..3 refined,
> FR-IN-4..5 added, §10.3 rewritten). Next: loop phase ② exercises.
