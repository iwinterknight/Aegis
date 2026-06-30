# Project Aegis - System Specification

> **Source of truth.** Living, version-controlled spec, converted from `Project_Aegis_System_Specification_v4.3.docx` (Revision 4.3). Design changes are made here as reviewable diffs.

> PROJECT AEGIS
> System Specification Document
> Autonomous Enterprise M&A Intelligence Platform
> Document Type: System Architecture, Product & Technical Specification
> Target Environment: On-Premise / Bounded Compute (Local-First, Zero-Cloud-Leak Architecture)
> Status: Engineering Blueprint / Spec-Driven Development Seed
> Revision: 4.4 (Working Draft) — Settled Phase 1 ingestion: structured-first via SEC XBRL (`companyfacts`) as the primary claims source with document retrieval deferred to Module 2; a uniform `SourceConnector` contract driven by a declarative, reproducible source descriptor; and an anchored-synthetic ledger (Faker totals tied to real reported figures). Refined FR-IN-1..3, added FR-IN-4..5, updated §10.3. See ADR-0001.

#### Revision Note (v4.4)

This revision settles the Phase 1 data and ingestion architecture (recorded in ADR-0001). Three
coupled decisions: (1) **structured-first ingestion** — the SEC's XBRL data (`companyfacts` / `frames`
/ Financial Statement Data Sets) is the primary *claims* source, pulled as structured JSON without
document parsing, which is sufficient for the SG-1 reconciliation; raw filing documents are cached but
document retrieval (RAPTOR/PageIndex) is explicitly deferred to Module 2 / Phase 3 per P4, honoring the
industry-standard split of *number-from-XBRL, quote-from-document*. (2) A uniform **`SourceConnector`
contract** — a declarative **source descriptor** is resolved by one connector per source *type* via
`resolve → fetch → normalize → emit`, so adding a source is a new adapter, not a new pipeline; the
descriptor is human-readable, reproducible, and the provenance root of a run (NFR-CORR-1). (3) The
**anchored-synthetic ledger** — Faker generates a ledger whose totals are tied to a target filing's
real reported figures (clean or a seeded discrepancy with a known delta), with realism cued from real
public proxies (open-source ERP charts of accounts, realistic distributions, Benford's Law). Liveness
remains deferred: batch pull is primary, and a later CDC trigger emits the same descriptors. FR-IN-1..3
refined, FR-IN-4..5 added, §10.3 updated.

#### Revision Note (v4.3)

This revision generalizes Module 2’s retrieval to compound queries that span multiple sections at different granularities. Navigation now decomposes a query and emits a set of typed (node, intent) instructions; FR-RAG-4’s serve rule is applied per instruction, so a single answer combining a summary from one node and a pinpointed span from another is the expected behaviour, not an edge case. A new assembly step allocates the context budget across the heterogeneous pieces, deduplicates overlap, and flags cross-node conflicts for review. The self-correcting loop is sharpened to distinguish three failure classes — planning (bad decomposition), navigation (wrong node), and extraction (wrong span/summary) — each routed to a different correction, and gains a coverage check that confirms the assembled context addresses every sub-question before generation. New requirements FR-RAG-5..7, an acceptance test, and glossary entries accompany the change. The multi-source navigation paths also enrich the audit trail rather than complicating it.

#### Revision Note (v4.2)

This revision settles the retrieval architecture. Module 2 now specifies a structure-routed hybrid: a PageIndex-style table-of-contents tree navigates by LLM reasoning to the correct section (traceable, explainable, cross-reference-aware), and a within-node RAPTOR mechanism then serves either a compact summary (global queries) or a pinpointed span (local queries) so an oversized section is never dumped into context and a small answer is never buried in a huge one. The composition cures corpus-wide RAPTOR’s severed-context weakness and pure PageIndex’s overflow weakness, keeps the interactive path cheap (navigation reasons only over the compact ToC; per-node sub-trees are built during async ingestion), and makes the navigation path double as audit-trail provenance — particularly valuable for the structure-heavy Legal facet. The change is propagated to the ingestion pipeline (Section 10.3), FR-RAG (with a new FR-RAG-4 for oversized-node serving), the Financial Specialist agent, the roadmap, and the glossary. An oversized-node threshold and table-aware splitting of atomic large units are noted as calibration items.

#### Revision Note (v4.1)

This revision makes the platform truly four-facet while preserving a minimal-data starting point. Three evidence layers are added to the data strategy — a legal-document corpus (contracts, leases, IP, litigation), operational data tables (customer/supplier/HR), and a compliance register (licenses, certifications, violation history) — each pairing real public proxies with simulated internal records, mirroring the accounting facet. Crucially, the system is specified as data-adaptive (Section 10.2): it operates on the minimal set (10-K/10-Q + simulated general ledger + rulebooks), with the Accounting facet fully functional, and progressively lights up the Legal, Operational, and Compliance facets as their evidence layers appear. Facets without an evidence layer are reported as claims-only or not-assessed — never silently treated as verified — and every output carries a coverage/confidence summary (new Principle P11). The ledger-sourcing posture is also corrected: real internal ledgers are lawful in real deployment (provided in a diligence data room under NDA), development uses simulated and public-proxy datasets, and ingestion is source-agnostic so the swap is a configuration change, not a redesign. Nothing here is treated as final; the document continues to evolve.

#### Revision Note (v4.0)

This revision completes Module 6’s evaluation and training detail. It specifies: (1) an evaluation methodology built on a labeled task suite whose ground truth Aegis owns by construction (seeded discrepancies, executable SQL, deterministic projection math), evaluated with the model isolated from retrieval and scored per capability on gold labels; (2) how the same harness benchmarks the sovereign model against external providers, with the provider serving as measuring stick and distillation teacher rather than deployment target; (3) a precise train/don’t-train decision rule — an absolute capability bar first, then a real, model-shaped gap test — expressed as a four-way matrix; and (4) a progressive training ladder that keeps method (QLoRA) distinct from objective (SFT, distillation), compares SFT-only / distillation-only / SFT-then-distillation forks, merges adapters between stages, watches a per-capability curve under regression gating, and stops at the lowest-complexity rung that clears every bar. A matching acceptance criterion was added to Section 7.

#### Revision Note (v3.1)

This revision adds three capabilities and reconciles them with the constitution. (1) Inference is now pluggable: Aegis runs its own fine-tuned “sovereign” model by default but can route to external LLM providers through the same OpenAI-compatible interface. To keep this consistent with zero-egress, external use is an explicit opt-in mode behind a data-classification gate that hard-blocks confidential/MNPI payloads; only public/synthetic data may leave the host. Since the project’s sensitive ledger is simulated and its filings are already public, provider benchmarking is privacy-safe by construction. (2) A sovereign-model strategy is specified — base-model selection plus a staged, evidence-gated training path (instruction fine-tuning, knowledge distillation from a frontier teacher, and DPO for agentic robustness, following AgentQ). (3) A Web Research & Real-Time Grounding agent is added so forecasts can incorporate current public information, with strict provenance and the filings/ledger retained as primary truth. These appear as new Modules 6–7 (Section 11), with corresponding updates to scope, requirements, principles, dependencies, glossary, and roadmap.

#### Revision Note (v3.0)

This revision restructures the document into a seed for Spec-Driven Development. It adds the product and requirements scaffolding that downstream specs, plans, and tasks decompose from: a vision with explicit long- and short-term goals (Section 2), users and personas (Section 3), scope and non-goals (Section 4), enumerated and individually testable functional requirements (Section 5), non-functional requirements (Section 6), measurable success criteria and acceptance tests (Section 7), a binding engineering constitution of guiding principles (Section 8), and assumptions/dependencies/constraints (Section 9). The complete technical view from Rev 2.1 is retained unchanged and renumbered into Sections 10–13, followed by the implementation roadmap (14), an open-items and risk register (15), and a glossary (16).

#### Revision Note (v2.1)

This revision elevates SGLang to a co-primary server engine alongside vLLM. SGLang’s RadixAttention maintains shared KV state across all concurrent requests in a radix tree, enabling multi-level prefix sharing and automatic fork/branch sharing — a closer match to Aegis’s request shape (a fat shared rulebook prefix, common supervisor/system prompts across sub-agents, and forked Bull/Bear scenario branches) than vLLM’s per-request prefix matching. Its constrained-decoding path is also markedly faster, which benefits the structured JSON audit trails. Ollama is correspondingly demoted to development tooling only; it is a convenience wrapper around llama.cpp and is not a concurrent production serving engine. The CAG section (Module 2) has been rewritten to be engine-agnostic, naming SGLang RadixAttention as the preferred mechanism for the regulatory prefix. The earlier v2.0 revision (staged CAG Tier 1 / Tier 2, corrected prefix-cache mechanics, cache isolation) is retained. A list of items still flagged for review appears at the end of the document.

## 1. Executive Summary & Problem Statement

In corporate finance, Corporate Development teams, private equity firms, and investment banks undergo an intensive 3-to-6-month due diligence process during Mergers and Acquisitions (M&A). This phase requires evaluating target assets across accounting records, legal structures, operational histories, and compliance portfolios.

Current enterprise workflows suffer from major inefficiencies:

Extreme Document and Context Volatility: Analysts must extract and synthesize information from thousands of pages of unstructured SEC filings (10-K, 10-Q), which feature complex, deeply nested text-table pairs and cryptic footnotes.

Data Silos and Modality Mismatches: Critical insights are highly decoupled. Narrative-driven risk profiles live in text filings, operational transaction ledgers live in relational ERP systems (SQL databases), and performance metrics live in isolated business intelligence (BI) frameworks like Tableau.

Strict Privacy Boundaries: Due diligence materials contain highly sensitive Material Non-Public Information (MNPI). Transmitting this data to external cloud APIs (e.g., public OpenAI/Anthropic endpoints) violates regulatory compliance protocols and corporate confidentiality agreements. Local execution is non-negotiable.

Context Window Degradation: Long-running evaluation workflows cause token bloat. Standard context windows suffer from “loss in the middle” degradation over multi-turn, multi-week conversations, causing critical accounting anomalies to go unnoticed.

#### The Objective

Project Aegis is an autonomous, event-driven, local hierarchical multi-agent platform. It ingests unstructured public filings and maps them against internal corporate transactional ledgers. Aegis automates comprehensive compliance reviews, highlights high-risk deficits, simulates future operational impacts, and generates deterministic audit trails while running on a bounded local hardware budget.

## 2. Vision, Goals & Objectives

#### Vision (Long-Range)

Project Aegis aims to become a fully autonomous, on-premise “Lead AI Auditor” for M&A due diligence: a system that continuously ingests public filings and internal ledgers, runs cross-document compliance review, simulates forward-looking scenarios, and produces verifiable, self-correcting, fully explainable audit reports — with zero confidential-data egress to external services.

#### Long-Term Goals (12+ month horizon)

LG-1 — Continuous multi-target auditing: Autonomously audit several target companies concurrently, reacting to new filings and ledger updates via event-driven ingestion.

LG-2 — Boardroom-grade projections: Deliver scenario/projection analysis with deterministic, four-tier explainability trusted for executive decision-making.

LG-3 — Production hardening: Operate as a platform-engineering-grade system with drift monitoring, regression-gated optimization, and multi-analyst concurrency.

LG-4 — Portable edge deployment: Run quantized models on isolated analyst hardware for field use without connectivity.

#### Short-Term Goals (MVP / first milestone)

SG-1 — End-to-end discrepancy detection: Ingest one real 10-K plus a matched simulated Postgres ledger and detect a deliberately seeded financial discrepancy end-to-end.

SG-2 — Local serving with CAG Tier 1: Stand up single-node vLLM/SGLang serving with the regulatory rulebook resident as a shared-prefix KV cache.

SG-3 — Grounded agentic RAG: Build the RAPTOR index and the RAGAS self-correcting loop, returning a grounded, cited answer.

SG-4 — One explainable projection: Produce a single “What-If” scenario with the complete four-tier explainability audit trail.

SG-5 — Minimal dual UI + tracing: Ship the analyst workspace and engineer control panel with full agent-step tracing.

## 3. Users & Personas

Financial Analyst (primary): Runs audits, chats with the data, triggers reports and scenarios. Non-technical; depends on grounded, explainable, citation-backed output. Success = trustworthy answers without reading 300-page filings.

Platform / AI Engineer (secondary): Operates the inference stack; monitors drift, cache residency, and regression tests; tunes optimization layers. Success = observable, regression-safe system behaviour.

Compliance Reviewer / Executive (consumer): Consumes final reports and risk dashboards. Requires the deterministic audit trail and source grounding in order to act on findings.

## 4. Scope & Non-Goals

#### In Scope

Real public 10-K / 10-Q ingestion; a matched simulated Postgres ledger; local optimized inference (vLLM / SGLang / llama.cpp); a fine-tuned sovereign model with an optional governed external-provider path and a benchmarking harness; agentic, self-correcting RAG (RAPTOR + CAG); multi-tier agent memory; MCP tooling (Postgres, Tableau, web search); deterministic projections with four-tier explainability, augmented by a Web Research agent for real-time public signals; and the evaluation, drift, and dual-workspace UI suite.

#### Non-Goals (explicitly out of scope)

Not financial / investment advice: Aegis surfaces discrepancies and risks; it does not recommend trades or make investment decisions.

No improperly obtained confidential data: Development uses simulated ledgers and public proxy datasets (e.g., sample ERP schemas, litigation-disclosed records). Real internal ledgers are used only where lawfully provided — e.g., a diligence data room under NDA in real deployment. Confidential public-company ledgers are never obtained out of band; the ingestion path is source-agnostic so simulated data can be swapped for lawfully-provided real data without redesign.

Minimal-data baseline, holistic by expansion: The system must run on the minimal data set (10-K/10-Q + simulated general ledger + rulebooks) with the Accounting facet fully functional, and expand to the Legal, Operational, and Compliance facets as their evidence layers are added — never hard-failing when a facet’s data is absent (see Section 10.2).

No ungoverned cloud egress: Confidential/MNPI data shall never leave the host. External LLM providers are supported only as an explicit opt-in for public/synthetic data (benchmarking and distillation), enforced by a data-classification gate — not as an unrestricted default.

Not a general-purpose chatbot: Scope is bounded to M&A due-diligence auditing, not open-domain assistance.

Synchronous heavy ingestion excluded: Large-document indexing is asynchronous by design; the UI never blocks on a 200-page parse.

Sparse-attention (Quest) deferred: Query-aware KV sparsity is recorded as a future optimization and is not part of the current build.

Not a substitute for professional judgment: Outputs assist, but do not replace, qualified legal/financial review.

## 5. Functional Requirements

Each requirement is phrased to be independently testable and traces to a technical module (Sections 10–13).

#### Ingestion & Data

FR-IN-1: The system shall retrieve real filing data from SEC EDGAR via a programmatic API, **structured-first**: the primary claims source is the XBRL financial data (the `companyfacts` / `frames` APIs and the Financial Statement Data Sets), pulled as structured facts without document parsing. Raw filing documents (10-K / 10-Q) shall be cached at ingestion for later grounding, but document retrieval is not built in this phase (it is deferred to Module 2 / Phase 3 per P4).

FR-IN-2: The system shall generate a simulated Postgres ledger (via Faker) that is **anchored to a target filing's real reported figures** — generating transactions that sum to the filing's claimed value (clean) or to a configured conflicting total (a seeded discrepancy with a known delta). Realism is cued from real public proxies (open-source ERP charts of accounts; realistic distributions; Benford's-Law-conforming amounts).

FR-IN-3: Ingestion shall be **batch-first**, resolving a source descriptor and pulling on demand. It shall be architected so that an asynchronous, event-driven trigger (new-file / change-data-capture) can later emit the *same* descriptors without redesign; heavy ingestion shall never block the user interface.

FR-IN-4: All ingestion shall go through a uniform **`SourceConnector` contract**: a declarative **source descriptor** (`{company, lookback window, filing types, …}`) is resolved by a connector implementing `resolve(descriptor) → fetch → normalize → emit canonical records`, with one connector per source *type* (`sec-xbrl`, `sec-document`, `simulated-ledger`, `rulebook`; later `ffiec-callreport`, `contract-corpus`). Adding a data source shall be a new adapter, not a new pipeline.

FR-IN-5: A source descriptor shall be human-readable, reproducible, and re-runnable, serving as the provenance root of an ingestion run; re-running a saved descriptor shall pull identical data (supporting NFR-CORR-1).

#### Retrieval & RAG

FR-RAG-1: The system shall build a structure-routed hierarchical index (PageIndex-style ToC navigation with within-node RAPTOR summarize-or-split) supporting both global (summary) and local (span) queries.

FR-RAG-4: A section exceeding a configured size threshold shall be served via a within-node summary (global queries) or a within-node span search (local queries), and never by placing the full section into the context window.

FR-RAG-5: Navigation shall decompose a compound query into a set of typed (node, intent) retrieval instructions; the serve rule (FR-RAG-4) applies per instruction, so a single response may combine summaries and spans from different nodes.

FR-RAG-6: An assembly step shall allocate the context budget across retrieved pieces, deduplicate overlap, and flag cross-node conflicts (surfaced for review, never silently resolved).

FR-RAG-7: The self-correcting loop shall include a coverage check verifying the assembled context addresses every decomposed sub-question, and shall route corrections by failure class (planning → re-decompose, navigation → re-navigate, extraction → re-search).

FR-RAG-2: Regulatory rulebooks shall be served via shared-prefix CAG without per-query vector lookup.

FR-RAG-3: Every extraction shall pass through a RAGAS-scored self-correcting loop that reformulates and retries when scores fall below threshold.

#### Memory

FR-MEM-1: The system shall maintain working, episodic, and semantic memory as distinct tiers.

FR-MEM-2: A background compaction worker shall convert episodic logs into semantic facts at a token threshold and purge redundant transcripts.

#### Tooling (MCP)

FR-MCP-1: Agents shall query the Postgres ledger through a parameterized MCP tool over JSON-RPC.

FR-MCP-2: Agents shall create or modify risk dashboards through a Tableau MCP tool.

#### Agents & Orchestration

FR-AG-1: A LangGraph supervisor shall delegate to Financial, Legal/Compliance, Forecasting, Data-Tooling, and Web-Research specialist agents.

FR-AG-2: Every agent step shall be traced (Arize Phoenix / LangSmith).

#### Model Strategy & Providers

FR-MOD-1: Inference backends (local engines and external providers) shall be interchangeable behind a single OpenAI-compatible router.

FR-MOD-2: The system shall default to Sovereign (local-only) mode; routing to external providers shall require explicit opt-in.

FR-MOD-3: A data-classification gate shall block confidential/MNPI-tagged payloads from any external provider, and log all external routing.

FR-MOD-4: The evaluation suite shall benchmark the sovereign model against external providers on identical task sets (quality, latency, cost).

FR-MOD-5: The sovereign model shall be domain-adapted via staged training (SFT → distillation → DPO), with each stage regression-gated before promotion.

#### Web Research & Grounding

FR-WEB-1: A Web Research agent shall retrieve public web data via a provider-agnostic, citation-preserving search interface exposed as an MCP tool.

FR-WEB-2: Every web-sourced claim shall carry its source URL and retrieval timestamp into the audit trail, tagged distinctly from filing-sourced evidence.

FR-WEB-3: Forecasts shall treat filings/ledger as primary truth and web data as augmentation; web-vs-filing conflicts shall trigger the self-correcting loop.

FR-WEB-4: Web queries shall never contain MNPI; zero-data-retention (ZDR) search providers shall be preferred.

#### Data Coverage & Graceful Scaling

FR-DATA-1: The system shall operate on the minimal data set (10-K/10-Q + simulated general ledger + rulebooks) with the Accounting facet fully functional.

FR-DATA-2: The system shall detect which evidence layers are present and enable the corresponding facets (Legal, Operational, Compliance) automatically.

FR-DATA-3: For a facet lacking its evidence layer, the system shall report findings as claims-only/unverified or not-assessed, and shall never present an unverified claim as reconciled.

FR-DATA-4: Every report and the analyst UI shall include a coverage/confidence summary indicating which facets are evidence-backed.

FR-DATA-5: Ledger and record ingestion shall be source-agnostic, so simulated data can be replaced by lawfully-provided real data without redesign.

#### Projections & Explainability

FR-PROJ-1: Scenario arithmetic shall execute in a deterministic sandbox, never as free-form LLM math.

FR-PROJ-2: Every projection / finding shall render the four-tier audit trail (Premise, Parameterization, Equation, Grounding).

FR-PROJ-3: Parallel scenarios (e.g., Bull vs. Bear) shall run in isolated state contexts with no cross-contamination.

#### Evaluation & UI

FR-EVAL-1: The system shall log RAGAS metrics continuously and surface them in the engineer panel.

FR-EVAL-2: Concept/data-drift monitors shall flag when the index needs rebuilding.

FR-EVAL-3: Optimization changes (quantization or engine swaps) shall trigger an automated regression test before adoption.

FR-UI-1: The UI shall provide a Financial Analyst Workspace and a Platform Engineer Control Panel.

## 6. Non-Functional Requirements

NFR-PRIV-1 (Privacy): No confidential/MNPI data shall leave the host. Public/synthetic data may be sent to external providers only under explicit opt-in and only via the data-classification gate; MNPI shall never appear in logs or URLs.

NFR-PRIV-2 (Cache isolation): Prefix-cache reuse shall be isolated per session (e.g., via cache_salt) to prevent cross-session inference.

NFR-PERF-1 (Latency): With a warm cache, interactive chat shall target sub-second time-to-first-token (to be calibrated on target hardware).

NFR-PERF-2 (Decoupling): Heavy ingestion shall not degrade interactive latency (enforced by the async/sync split).

NFR-CORR-1 (Correctness): Numerical projections shall be deterministic and reproducible from the recorded equation and inputs.

NFR-OBS-1 (Observability): Every agent step, tool call, cache hit-rate, and self-correction iteration shall be inspectable.

NFR-RES-1 (Resource bounds): The system shall run within a defined local hardware budget; edge deployment via 4-/8-bit quantization.

NFR-MAINT-1 (Portability): Inference engines and providers shall be interchangeable behind an OpenAI-compatible interface; tools behind MCP contracts.

NFR-GOV-1 (Governance): All external routing shall be policy-enforced, logged, and auditable; the default posture is local-only.

NFR-PROV-1 (Provenance): Every external/web-sourced claim shall carry source and timestamp, distinguishable from internally-grounded evidence.

## 7. Success Criteria & Acceptance Tests

The MVP is accepted when the following are demonstrable:

Discrepancy detection: Given a 10-K asserting a liability of $X and a simulated ledger summing to $Y ≠ $X, the system flags the delta as a high-risk finding, citing both the source quote and the exact SQL used.

Grounded explainability: The finding renders all four audit-trail tiers and the grounding quote is traceable to the source filing.

Self-correction: When RAGAS faithfulness/relevance fall below threshold, the loop reformulates and improves the score on retry (observable in traces).

Zero egress: A network test confirms no outbound calls to external inference/data endpoints during a full audit.

Regression safety: An inference-optimization change (quantization, or a vLLM ↔ SGLang swap) is gated by an automated regression test asserting no degradation in reasoning/math accuracy.

Projection determinism: Re-running a saved scenario reproduces identical numbers from the recorded equation and inputs.

Provider benchmark: The suite produces a head-to-head report of the sovereign model vs. at least one external provider on the public corpus (faithfulness, math/SQL accuracy, latency, cost).

Egress governance (negative test): An attempt to route MNPI-tagged content to an external provider is blocked and logged.

Web-grounded forecast: A forecast incorporates a current public web fact with correct provenance (URL + timestamp) in the audit trail, while the filing/ledger remains the primary basis.

Staged training comparison: The training ladder reports per-capability scores for base, SFT-only, distillation-only, and SFT-then-distillation against the provider baseline, and the stopping rule selects the lowest-complexity rung that clears every capability bar without regressing any other.

Graceful data scaling: Run on the minimal data set, the Accounting facet produces verified findings while Legal/Operational/Compliance are reported as claims-only; when an evidence layer is added, the corresponding facet automatically becomes evidence-backed and the coverage summary updates — with no code change.

Compound, mixed-granularity retrieval: A question spanning two sections at different granularities returns a summary from one node and a span from another, both provenance paths appear in the audit trail, and the coverage check confirms every sub-question is addressed before generation.

## 8. Guiding Principles (Engineering Constitution)

These principles are binding constraints for all downstream specs, plans, and implementation tasks. Where a design decision conflicts with a principle, the principle wins.

P1 — Local-first, confidential zero egress: Confidential/MNPI data never leaves the host. External providers are permitted only for public/synthetic data under an explicit, governed opt-in (benchmarking and distillation), enforced by the data-classification gate.

P2 — Determinism over guesswork: All arithmetic runs in a sandbox; LLMs never perform multi-step math directly.

P3 — Grounded & explainable: Every material claim cites a source; provenance comes from the semantic retrieval layer, never from an efficiency mechanism.

P4 — Measure before optimizing: Build the simplest mechanism first (e.g., CAG Tier 1); add complexity (Tier 2, sparsity) only on observed evidence.

P5 — Honest mechanics: Capabilities are described as they actually behave (best-effort vs. guaranteed); no overstated “zero-latency / locked-in” claims.

P6 — Self-correction by default: Generation is wrapped in evaluation loops that catch and repair low-quality output.

P7 — Uniform contracts: Engines sit behind the OpenAI-compatible API; tools sit behind MCP — no brittle, hardcoded integrations.

P8 — Regression-gated change: No optimization ships without passing the regression suite.

P9 — Privacy by construction: Per-session cache isolation; no sensitive data in logs, URLs, or shared caches.

P10 — Web data augments, never overrides: Real-time web signals add timely context to forecasts, but the filings and ledger remain the primary source of truth; all external evidence is provenance-tagged and conflicts are surfaced, not silently resolved.

P11 — Data-adaptive operation: Aegis runs on the minimal data set and expands to holistic four-facet coverage as evidence layers are added. A facet without its evidence layer is reported as claims-only or not-assessed — never silently treated as verified — and every output carries a coverage/confidence summary.

## 9. Assumptions, Dependencies & Constraints

#### Assumptions

Target 10-K / 10-Q filings are publicly available via SEC EDGAR.

A bounded but GPU-capable local host is available for server-side inference; analyst edge devices are CPU / low-VRAM.

A simulated ledger is acceptable for development and evaluation in place of real MNPI.

#### External Dependencies

SEC EDGAR API; open-weight base models and their licenses (e.g., Qwen3, GLM-5.1, DeepSeek V4, Phi-4); vLLM, SGLang, llama.cpp; a model router (e.g., LiteLLM); training stack for SFT/distillation/DPO (e.g., PEFT/LoRA-QLoRA, TRL/Axolotl); a teacher model for distillation (a frontier provider or large open model); external provider API keys (External mode only); agent-native web search providers (e.g., Exa, Tavily, Firecrawl, Valyu); LangGraph; RAGAS; a vector store (e.g., Qdrant); PostgreSQL; a Tableau-compatible BI target; Arize Phoenix / LangSmith; LMCache (Tier 2 only).

#### Constraints

Fixed local hardware budget; no external network inference; deterministic explainability is mandatory, not optional.

## 10. Core Architecture & Data Strategy

Aegis is designed on an Asynchronous Ingestion / Synchronous Generation split. Long-running ingestion workers process incoming corporate files in the background, ensuring that when an analyst logs into the UI, the system provides sub-second model response times.

### 10.1 Data Strategy Matrix

To test the system thoroughly without relying on live, confidential corporate data, Aegis combines real-world public documentation with simulated internal records. The first four rows are the minimal/accounting baseline; the last three are progressive evidence layers that light up the remaining diligence facets (see Section 10.2).

| Data Source | Modality & Storage | Operational Role | Fidelity Vector |
| --- | --- | --- | --- |
| SEC Filings (10-K / 10-Q) | Unstructured PDF / HTML inside local Vector DB | Establishes the foundational corporate risk text, lease liabilities, and public declarations (the claims layer for all four facets). | 100% real-world data downloaded directly from SEC EDGAR via programmatic APIs. |
| ERP Financial Ledger | Relational data tables inside local PostgreSQL | Provides individual transaction entries, payroll records, and vendor lines to audit text claims (Accounting evidence). | Simulated via Python Faker, scripted to intentionally match or conflict with the totals declared in the 10-K. Source-agnostic: replaceable by a lawfully-provided real ledger. |
| Regulatory Frameworks | Static Markdown files pinned inside memory cache | Acts as strict regulatory guidelines (e.g., GAAP, IRS Tax Codes) to run verification checks (Compliance rules). | 100% real-world legal definitions compiled from regulatory repositories. |
| BI Configurations | JSON metadata schemas via Tableau MCP | Controls the target configurations of internal corporate reporting dashboards. | Locally defined JSON payloads mapped to relational database views. |
| Legal Document Corpus (progressive) | Unstructured contracts / leases / IP / dockets; structure-routed retrieval (ToC navigation + within-node RAPTOR) | Clause-level evidence for the Legal facet — change-of-control, indemnities, exclusivity, IP ownership, litigation exposure. | Real public proxies (EDGAR material-contract exhibits, the CUAD annotated-contract dataset, court dockets) plus a simulated data room with seeded clauses. |
| Operational Data Tables (progressive) | Relational tables inside local PostgreSQL | Granular evidence for the Operational facet — customer concentration/churn, supplier concentration, headcount/attrition, unit economics. | Simulated extension of the Postgres schema (customer/CRM, supplier, HR), optionally seeded with landmines (e.g., revenue concentration). |
| Compliance Register (progressive) | Relational table / structured records in PostgreSQL | Evidence of actual compliance status for the Compliance facet — licenses, permits, certifications, enforcement/violation history — paired with CAG rules. | Simulated register plus optional real public enforcement databases; seeded past violations to test detection. |

### 10.2 Data-Adaptive Operation & Capability Tiers

Aegis is designed to run on whatever evidence is available and to expand gracefully toward the full four-facet audit as more data is supplied. The minimal configuration is always sufficient to operate; additional evidence layers enrich coverage rather than being prerequisites. Each facet has a claims layer (what the filing asserts) and an evidence layer (the records that verify it); the filings supply the claims layer for all four facets, while the evidence layers arrive progressively.

Tier 0 — Minimal (always available): 10-K/10-Q + simulated general ledger + regulatory rulebooks. The Accounting facet is fully functional (the claims-vs-ledger reconciliation gotcha). Legal, Operational, and Compliance are readable at the claims level from the filings, but explicitly marked unverified.

Tier 1 — + Operational tables: Customer/CRM, supplier, and HR tables enable the Operational facet (concentration, churn, attrition). Cheapest expansion — a Postgres schema extension consumed via the existing MCP.

Tier 2 — + Legal corpus: Contracts, leases, IP, and dockets enable the Legal facet (clause-level risk), consumed through the existing RAPTOR layer.

Tier 3 — + Compliance register: Licenses, certifications, and violation history enable the Compliance facet, pairing the register with the CAG rulebooks. All tiers present = full holistic coverage.

The operating contract: at any tier the system runs; a facet without its evidence layer is reported as claims-only (unverified) or not-assessed, never silently presented as reconciled. Every report and the analyst UI carry a coverage/confidence summary stating which facets are evidence-backed. Because the ingestion paths are uniform (documents → RAPTOR, structured records → Postgres MCP, rules → CAG), adding a facet is a data-onboarding step, not an architectural change.

### 10.3 Ingestion Pipeline (SourceConnector contract)

All ingestion flows through a uniform **`SourceConnector`** contract (FR-IN-4). A declarative
**source descriptor** — e.g. `{company: <CIK>, lookback: 5y, forms: [10-K]}` — is resolved by the
connector for its source *type* via `resolve(descriptor) → fetch → normalize → emit canonical
records`. One connector exists per source type (`sec-xbrl`, `sec-document`, `simulated-ledger`,
`rulebook`; later `ffiec-callreport`, `contract-corpus`), so onboarding a new source is a new adapter
rather than a new pipeline. The descriptor is human-readable, reproducible, and re-runnable, and is
the provenance root of the run (FR-IN-5). Ingestion is batch-first today; an event-driven /
change-data-capture trigger can later emit the same descriptors without redesign (FR-IN-3).

**Two ingestion paths sit behind this contract:**

- **Structured claims (primary, this phase).** The `sec-xbrl` connector pulls reported financial
  facts from XBRL (`companyfacts` / `frames`) as structured JSON — no document parsing — sufficient
  for the claims-vs-ledger reconciliation (SG-1). Raw filing documents are cached for later grounding.
- **Document path (Module 2 / Phase 3).** When qualitative grounding and the Legal facet are added, a
  cached document is run through the structure-routed indexing flow below:

When a target asset document is added to the system, an event-driven worker runs an automated background ingestion flow:

[ New 10-K Document ] --> [ Structural Parser (ToC Tree) ] --> [ Per-Node Granularity Decision ] --> [ Within-Node RAPTOR Sub-Trees ]

|

v

[ User Report Trigger ] <-- [ LangGraph Multi-Agent Engine ] <-- [ Postgres SQL Validation Layer ]

Structural Parsing: Documents are broken down by headers, preserving layout syntax and embedding markdown tables cleanly alongside their associated prose.

Hierarchical Indexing: A structural table-of-contents tree is built from the document’s natural headings, and any oversized section is given a within-node RAPTOR sub-tree (summarize-or-split) — the structure-routed hybrid detailed in Module 2.

Cache Preparation: Long-term vector spaces and local key-value caches are pre-warmed before an analyst starts an interaction.

## 11. Technical Execution Modules

### 11.1 Module 1: Model Inference Optimization (The Muscle)

To run massive open-weight models (e.g., Llama-3-70B, Mistral-Large, or deep-reasoning variations) on local enterprise servers, Aegis utilizes low-level inference optimization frameworks. Server-side generation is handled by two co-primary engines; edge execution by a third.

#### Server-Side Deployment (vLLM & SGLang — co-primary)

Both engines expose OpenAI-compatible APIs and share the same core throughput mechanisms (continuous batching and paged attention). They are deployed as interchangeable backends; SGLang is preferred for the prefix-heavy and structured-output paths.

vLLM (baseline concurrent serving): PagedAttention plus continuous batching, broad model coverage, and a mature OpenAI-compatible server. The default engine for general multi-agent concurrency.

SGLang (preferred for CAG + structured output): Adds RadixAttention, which holds the KV cache of all concurrent requests in a radix tree, enabling multi-level prefix sharing and automatic fork/branch sharing. This matches Aegis’s shape — a shared rulebook prefix and supervisor/system prompts reused across every sub-agent, and forked Bull/Bear scenario branches sharing a parent context. Its constrained-decoding path (XGrammar) is also substantially faster, benefiting the structured JSON audit trails.

TensorRT-LLM (optional performance overlay): NVIDIA-only compiled engine for maximum throughput/latency once the model and hardware are frozen. Adopted late: it carries significant setup cost (~1–2 weeks) and single-vendor lock-in, so it is not an iteration-phase engine.

#### Shared Core Mechanisms (both server engines)

Continuous Batching (Iteration-Level Scheduling): Instead of standard request-level batching (which waits for all generations in a batch to complete, wasting GPU cycles on short requests), the engine uses token-level execution scheduling. New incoming agent requests are dynamically integrated into the active execution batch at iteration boundaries, significantly driving up concurrency throughput.

Paged Attention: Mitigates memory bottlenecks caused by the linear growth of the Key-Value (KV) cache. By allocating physical KV cache memory in non-contiguous pages (similar to virtual memory paging in operating systems), Paged Attention sharply reduces KV cache fragmentation, allowing for larger effective context limits and multiple parallel agent operations on a single GPU cluster.

#### Engine Interchangeability & Switching

Because both engines speak the OpenAI-compatible protocol, all LangGraph agents target a single endpoint and remain agnostic to the backend. Switching is therefore a configuration concern, not a code change, escalating as needed:

Deploy-time config (baseline): An environment/config value selects the live engine. This fis also how the vLLM-vs-SGLang comparison is run in the evaluation suite — flip the config, re-run the regression set, compare.

Gateway routing (flexible): A thin router (e.g., a LiteLLM-style proxy) routes per workload — prefix-heavy CAG traffic and structured-JSON generation to SGLang, the remainder to vLLM — behind one endpoint.

Constraint — no shared KV cache: The two engines do not share a KV cache; a prefix warmed on one is not reusable by the other. Routing must therefore be session-sticky (an audit session stays pinned to one engine) to preserve the prefix-cache hits the CAG design depends on.

#### Edge / Client Deployment (llama.cpp & GGUF)

For mobile analysts operating on isolated hardware, models are compiled into GGUF format via llama.cpp.

Weights undergo 4-bit and 8-bit weight quantization (e.g., Q4_K_M and Q8_0 schemas), dropping local VRAM requirements dramatically while keeping perplexity loss minimal.

Development tooling note: Ollama (a convenience wrapper around llama.cpp) is used only for local prototyping and model smoke-testing. It is not a concurrent production serving engine and is never placed on the server path, which belongs exclusively to vLLM / SGLang.

### 11.2 Module 2: Advanced & Agentic RAG (The Knowledge)

Standard semantic search fails on complex financial audits because a single liability risk might be mentioned on page 12 and explained in a footnote on page 240, and because the most-similar chunk is not always the most relevant one. Aegis therefore uses a structure-routed hierarchical retrieval design — a hybrid of PageIndex-style reasoning navigation and RAPTOR-style summarize-or-split — backed by the cache-driven CAG path for static rulebooks.

#### Retrieval Design: Structure-Routed Hierarchical Retrieval (PageIndex × RAPTOR)

Retrieval runs in two phases: structure decides where to look, and a within-node mechanism decides how much to return. This composition cures the characteristic weakness of each technique used alone — RAPTOR’s tendency to sever a fact from the context that explains it, and pure PageIndex’s overflow when a returned section is too large or the answer is a tiny span within it.

Phase 1 — Structural navigation (PageIndex-style routing). At ingestion, a “table-of-contents” tree is built from the document’s natural headings (e.g., Item 8 → Note 14 (Leases) → sub-notes), each node holding a title and a short summary. At query time an LLM reasons over that compact ToC — not the full text — to navigate to the correct node, following cross-references (“see Note 14”) as a human would. The output is a traceable path to the right section, explainable by construction.

Phase 2 — Within-node RAPTOR (summarize-or-split). A node does not store one monolithic blob of section text. At ingestion each section is given a granularity decision against a configured size threshold: if it is small enough to use whole, it is stored as-is; if it is oversized, a mini-RAPTOR index is built over just that section’s content (chunk into ~300-token leaves → embed → cluster → summarize into a small local sub-tree). Retrieval is then served by level — a global question about the section returns the node’s compact summary (which always fits), while a local needle question runs a vector search within that node’s leaves only and returns the precise span.

Global Queries (“What is this firm’s structural exposure to real estate leases?”) are answered from a node’s within-node summary — never by dumping the full section into context.

Local Queries (“What were the precise Q3 maintenance fees?”) are answered by a span search within the already-correct node’s leaves, pinpointing the sentence rather than returning the whole section.

#### Compound Queries: Multi-Node, Mixed-Granularity Retrieval

A real audit question often spans several sections and needs a different granularity from each — the gist of one section and a pinpointed span from another (e.g., “What is the firm’s overall real-estate strategy, and what was the exact Q3 lease payment?”). The design treats this as the general case, not an exception: “global vs. local” is a property of each retrieved piece, not of the whole query. Navigation therefore decomposes a compound query and emits a set of typed instructions rather than selecting a single node.

Typed (node, intent) instructions: Navigation decomposes a compound query into sub-questions and returns a list of (node, intent) pairs — each target node tagged with the intent that selected it (global or local). The navigation step carries why each node was chosen, not merely that it was.

Per-instruction serving (mixed granularity is the norm): FR-RAG-4’s serve rule is applied to each instruction independently — a global-intent node returns its within-node summary; a local-intent node returns a within-node span search. A single answer may therefore combine a summary from one section and a span from another.

Assembly (budget, dedup, conflict): A composition step assembles the heterogeneous pieces into one context — allocating the token budget across blocks (how many spans per local node, demoting summaries when many sections are touched, when to stop adding nodes), deduplicating overlap, and flagging cross-node conflicts (e.g., a liability stated differently in the lease note vs. the tax note) for the self-correcting loop rather than resolving them silently.

Richer provenance, not messier: Because each piece carries its own navigation path, a mixed retrieval yields multi-source grounding — a strategy summary from Item 7 (MD&A) alongside a span from Item 8 → Note 14 — which is exactly the multi-source evidence a real audit finding needs.

#### RAPTOR (the within-node mechanism)

Within an oversized node, RAPTOR (Recursive Abstractive Processing for Tree-Organized Retrieval) builds the local sub-tree bottom-up: ~300-token sentence-aligned leaves are embedded, soft-clustered using Gaussian Mixture Models (GMMs) (so a chunk relevant to two themes can feed both), and each cluster is summarized by a local LLM into a parent node; the summaries are re-embedded and re-clustered recursively up to a local root. The bottom layer holds fine detail (needle retrieval) and the upper layers hold abstraction (global summaries) — confined to the single section the navigation step selected.

#### Why the composition is the chosen design

Cures severed context: Every leaf lives under its section node, reached by an explicit path, so a retrieved fact always carries its structural context (which section, which note) instead of floating free as in corpus-wide RAPTOR.

Bounds similarity error: Vector search runs only within an already-correct section — a small, on-topic pool — so “similar-but-wrong” matches are confined to a region the reasoning step already vouched for.

Keeps the hot path cheap: Navigation reasons only over the compact ToC (titles + summaries), and the expensive per-node sub-trees are built once during async ingestion. One light reasoning call plus a tiny local vector search is far cheaper than reasoning over full sections, preserving the interactive-latency target.

Native provenance: The navigation path is the audit trail — “Item 8 → Note 14 → [span]” drops directly into the four-tier explainability Grounding tier (Section 12). This is especially strong for the Legal facet, where a clause is navigated to by structure, the precise span is extracted, and the clause’s surrounding section remains intact for meaning.

#### Caveats & mitigations

Navigation latency: The routing LLM call adds latency versus pure vector search; mitigated by keeping the ToC compact, caching navigation for recurring query shapes, and falling back to a within-corpus collapsed-tree vector search when a query is latency-critical.

Ingestion cost: Building both a ToC tree and per-node sub-trees is more work, but it is asynchronous and therefore fits the decoupled architecture.

Oversized-node threshold: An explicit, configurable threshold decides when a section gets a sub-tree; it should be calibrated, not hardcoded on intuition.

Atomic oversized leaves: A genuinely indivisible large unit (e.g., one dense table with no sub-structure) still forces a careful, table-aware split — the single place where the “no arbitrary chunking” ideal must bend.

#### Cache-Augmented Generation (CAG) — Staged Implementation

For high-frequency, unchanging regulatory parameters (e.g., active GAAP accounting rules, IRS tax codes), Aegis avoids per-query vector lookups by keeping the rulebook resident as a precomputed KV state rather than retrieving it at runtime. This is implemented in two stages so that the simplest mechanism is built and measured first, with persistence added only when the data justifies it.

Tier 1 — Baseline (shared-prefix KV reuse). The regulatory corpus is ordered as a fixed, byte-identical prompt prefix placed ahead of all per-query content, so the engine’s shared-prefix cache reuses its KV blocks across requests — the rulebook is prefilled once and skipped thereafter. This is genuine CAG: no vector search, no re-encoding of the corpus. Both server engines support this mechanism: vLLM via Automatic Prefix Caching (APC), and SGLang via RadixAttention. SGLang is the preferred engine for this path — its radix-tree cache shares the rulebook prefix (and the common supervisor/system prompts) across all concurrent sub-agents and across forked scenario branches, which fits Aegis’s request shape more closely than APC’s per-request hash matching.

Honest performance characteristic: APC reduces time-to-first-token by eliminating repeated prefill over the rulebook. It is not “zero-latency” — attention is still computed over the cached tokens during decode. The win is the removed prefill, not free inference.

Honest reliability characteristic: APC is best-effort. Cached blocks are reclaimed under an LRU policy when GPU memory is contended, and the in-process cache does not survive an engine restart (a cold first query re-warms it). Under heavy multi-agent concurrency, the rulebook prefix can therefore be evicted and recomputed.

Cache isolation (privacy): Because Aegis handles MNPI, prefix-cache reuse is isolated per session. vLLM exposes a per-request cache_salt for this (only requests sharing the same salt may reuse cached blocks, closing the timing side-channel); whichever engine is deployed must enforce equivalent per-session cache isolation.

Tier 2 — Optional Upgrade (Persistent KV via LMCache). When monitoring shows the rulebook prefix is being evicted and recomputed under real load (see Section 13.1), the KV state is promoted to a persistent tier using LMCache, which provides multi-engine KV storage with tiered GPU→CPU→SSD offload. This guarantees residency across load spikes and process restarts and fits the bounded-hardware, on-prem profile: the rulebook KV lives in CPU/SSD and is loaded into GPU on demand rather than permanently occupying VRAM. Tier 2 is a measured enhancement, not a prerequisite.

Decision rule: Build Tier 1; instrument the rulebook cache hit rate in the Engineer Control Panel; adopt Tier 2 only when observed eviction/recompute of the regulatory prefix degrades latency. This Tier 1 → Tier 2 transition doubles as a concrete regression-suite exercise (before/after TTFT and hit-rate under induced load).

#### Self-Correcting Evaluation Loop

Every document extraction pass runs inside an autonomous verification envelope using RAGAS metrics programmatically:

# Programmatic RAGAS Verification Envelope

faithfulness    = check_faithfulness(retrieved_context, generated_response)

answer_relevance = check_relevance(user_query, generated_response)

if faithfulness < 0.85 or answer_relevance < 0.80:

# Autonomous query reformulation block

new_query = reformulate_search(user_query, generated_response)

retry_retrieval_loop(new_query)

Because retrieval now plans and assembles across nodes, the loop distinguishes three failure classes and routes a different correction to each: a planning failure (decomposition missed a sub-question or mis-assigned its intent) → re-decompose; a navigation failure (routed to the wrong node) → re-navigate; an extraction failure (right node, wrong span or summary) → re-search within the node. Ahead of the faithfulness/relevance gate, a coverage check verifies that the assembled context actually addresses every sub-question the compound query was decomposed into — catching the planning failure that RAGAS faithfulness alone would miss.

### 11.3 Module 3: Advanced Agent Memory Management (The Brain)

An audit covers weeks of analytical iteration. Standard context windows quickly suffer from token explosion or information erasure. Aegis separates state mechanics into a multi-tiered memory architecture:

Working Memory: Stores the current task’s active execution-graph state dictionary within individual LangGraph nodes, tracking localized loop conditions.

Episodic Memory (Short-Term): A rolling context buffer that remembers recent conversational history, analyst adjustments, and intermediate tool responses.

Semantic Memory (Long-Term): A vector-space database that stores durable, verified analytical facts, past transaction insights, and corporate metrics across separate login sessions.

Asynchronous Memory Compaction: To keep token overhead minimal, a background compaction loop triggers when episodic memory reaches a set token limit. It processes raw conversational logs, converts them into flat semantic facts, updates the Semantic Vector store, and purges the redundant text transcripts from the active execution path.

### 11.4 Module 4: Multi-Data Source Integration via MCP (The Hands)

To prevent brittle, hardcoded database endpoints, Aegis uses Anthropic’s open Model Context Protocol (MCP) via standard JSON-RPC protocol engines. This allows agents to interact safely with external tools through a uniform contract.

#### PostgreSQL MCP Server

Exposes secure, parameterized SQL tools to the multi-agent graph. This gives the agent structural system validation access to check corporate text filings against the transactional database.

/* Outgoing JSON-RPC MCP Tool Invoke Request */

{

"jsonrpc": "2.0",

"method": "tools/call",

"params": {

"name": "run_audit_query",

"arguments": {

"sql": "SELECT SUM(amount) FROM operating_ledger WHERE account_type = 'lease_deficit'"

}

},

"id": 42

}

#### Tableau Dashboards MCP Server

Allows the agentic network to generate visual assets automatically. The agent updates JSON layout configurations via the Tableau MCP to create or modify risk dashboards, embedding them directly within the web frontend.

### 11.5 Module 5: Hierarchical Agent Framework (The Backbone)

Aegis handles multi-layered workloads by deploying a Hierarchical Agent State Machine engineered inside LangGraph.

#### Node Topography & Routing Strategy

Supervisor Agent (The Brain): Analyzes the user’s audit goals, initializes the state parameters, coordinates downstream specialists, and runs final synthesis reviews.

Financial Specialist Agent: Interrogates the structure-routed retrieval index (ToC navigation + within-node RAPTOR) and parses complex balance sheets and table metrics.

Legal & Compliance Agent: Audits text disclosures against CAG-pinned regulatory rulebooks to identify hidden liabilities.

Forecasting Agent: Controls forward-looking simulation sandboxes and builds mathematical projection paths.

Data Tooling Agent: Directly acts as the primary caller for active PostgreSQL and Tableau MCP routing configurations.

Web Research Agent: Retrieves high-fidelity public web data (latest news, regulatory/market signals) through a citation-preserving search interface, augmenting forecasts while keeping filings/ledger as primary truth (Module 7).

#### Observability & Trace Instrumentation

Every single step — including token generation speeds, tool latencies, node transitions, and self-correction iterations — is piped into a local Arize Phoenix or LangSmith tracing server to ensure complete visibility into the multi-agent graph’s behavior.

### 11.6 Module 6: Model Strategy, Provider Abstraction & Benchmarking

Aegis runs its own fine-tuned “sovereign” model by default, but treats the model as a pluggable component: any OpenAI-compatible backend — a local engine or an external provider — can be slotted behind the same router used to switch vLLM and SGLang. This yields three benefits: optionality, head-to-head benchmarking of the sovereign model against frontier providers, and the ability to use a frontier provider as a teacher for distillation.

#### Operating Modes & Governed Routing

Sovereign Mode (default): Local-only inference (vLLM / SGLang) with zero external egress. The production mode for any confidential workload.

External / Benchmarking Mode (opt-in): Routes selected requests to external providers (e.g., OpenAI, Anthropic, Google) through the same OpenAI-compatible router (LiteLLM-style).

Data-Classification Gate: Every payload carries a sensitivity tag. Only PUBLIC-classified content may leave the host; CONFIDENTIAL/MNPI content is hard-blocked from external routing and the attempt is logged. Because Aegis’s sensitive ledger is simulated and its filings are already public, provider benchmarking and distillation on the public corpus are privacy-safe by construction. This refines, not breaks, Principle P1.

#### The Sovereign Model — Base Selection

Selection criteria: open weights, a permissive license, strong long-context and agentic tool use, solid numerical/table reasoning, and tractable fine-tuning on bounded hardware. Final choice is decided by the benchmarking harness, not asserted up front (Principle P4). Current (2026) candidates:

Server tier: Qwen3 235B-A22B (Apache-2.0 MoE, broad fine-tune ecosystem); GLM-5.1 (MIT license — a real advantage for commercial fine-tuning, strong agentic/long-horizon reasoning); DeepSeek V4 (best performance-to-cost, ~1M context with a low KV-cache footprint, well suited to retrieval-heavy long-document work).

Edge / fast-iteration tier: Qwen3.6-35B-A3B (Apache-2.0 MoE, 35B total / 3B active, ~262K context — strong on bounded hardware); Phi-4 (small, MIT, cheap/fast training iterations — ideal for SFT experimentation); Gemma 4 / Mistral Small 4 (single-GPU and GGUF edge deployment via llama.cpp).

Recommendation: A two-model family trained on the same data — a larger server model (lead candidates Qwen3-235B or GLM-5.1) and a small edge model (Phi-4 or Qwen3.6-35B-A3B compiled to GGUF).

#### Training Strategy (staged, evidence-gated)

The stages below are the conceptual sequence. QLoRA is the training method used throughout (not a separate stage); SFT and distillation are the objectives. How they are compared, gated, and stopped is specified in the Progressive Training Ladder later in this module.

Stage 0 — Baseline, no training: Start with a strong instruction-tuned base plus CAG/RAPTOR retrieval and prompting; benchmark against providers. Often retrieval plus a good base suffices — do not train prematurely (P4).

Stage 1 — Instruction fine-tuning (SFT, LoRA/QLoRA): Adapt to Aegis task formats — faithful 10-K table/footnote extraction, Postgres-MCP SQL generation, and strict four-tier JSON audit trails. Parameter-efficient LoRA/QLoRA keeps training within the hardware budget. Data: curated instruction pairs over real filings + synthetic ledger + regulatory rules mapped to gold audit outputs.

Stage 2 — Knowledge distillation from a frontier teacher: Use a frontier model (an external provider in External Mode, or a large open model such as DeepSeek V4-Pro / Kimi K2.6) as a teacher to generate high-quality reasoning traces, audit explanations, and tool-use trajectories, then distill the smaller sovereign model on them (response-level and rationale/CoT distillation). This is the second payoff of the provider option — providers serve as teachers, not just benchmarks. Distillation data passes through the governance gate (public/synthetic only).

Stage 3 — Preference optimization (DPO) for agentic robustness: Pure SFT on static demonstrations compounds errors on multi-step tasks. Following AgentQ, generate preference pairs via guided Monte Carlo Tree Search plus AI self-critique over agent trajectories, then train with an off-policy DPO variant so the agent learns from both successful and sub-optimal paths — improving multi-step planning, tool use, and self-healing. This applies to the audit agents and especially the Web Research agent (Module 7).

Regression gating: Every checkpoint runs the evaluation/regression suite before promotion (Principle P8).

#### Evaluation Methodology (Labeled Task Suite)

All model decisions — train or not, which provider, which training stage — are made against a fixed, versioned benchmark of representative tasks, each with a known-correct answer. Aegis can build this ground truth cheaply because it already owns the truth: ledger discrepancies are seeded deliberately (the correct delta, account, and risk flag are known), generated SQL can be executed and compared to the true figure, and projection math has a deterministic correct output. The suite spans the system’s capabilities: discrepancy detection, local/global extraction, SQL generation, projection math, and audit-trail formatting.

Isolate the model from retrieval: Each candidate (sovereign base, provider A/B, trained variants) is fed the identical retrieved context, so only the model varies. Items where all candidates fail on the same context indicate a retrieval problem (fix RAPTOR/CAG/prompting), not a model problem — training cannot fix those.

Per-capability, gold-label metrics: Discrepancy recall (the headline), SQL execution accuracy, projection numeric exactness, audit-trail completeness (a schema check on the four tiers), and RAGAS faithfulness for open-ended extraction — plus latency and dollar-cost per task. Where an LLM-as-judge is unavoidable, a provider never grades its own output; gold labels or a neutral judge are used to avoid bias.

Reproducibility: Evaluation runs at temperature 0 so deltas reflect capability, not sampling noise; gaps are confirmed with a paired significance test across items before they count.

#### Benchmarking Against External Providers

Because local and external backends share one OpenAI-compatible interface, the same suite runs unchanged against the sovereign model and each external provider. The provider score is not a target to switch to — it is the rung marker that quantifies how far the local model is from the frontier and, when training is warranted, supplies the distillation teacher. The destination is always Sovereign mode; the provider is the measuring stick and the teacher, not the deployment.

#### Train / Don’t-Train Decision Rule

“Underperforms” is only actionable once made precise. The decision is two ordered questions, not “is base worse than the provider”:

Does base + retrieval clear the absolute bar the task requires? Bars are set from the use case, not the provider (illustrative defaults, to be calibrated: discrepancy recall ≥ 95%, SQL execution accuracy ≥ 98%, faithfulness ≥ 0.85, audit-trail completeness = 100%). If base clears the bar, ship base and stop — even if a provider scores higher. Staying local is itself a value (P1); the application needs “good enough,” not “better.”

If base fails the bar, is the gap real and model-shaped? Real = statistically significant across enough items, not run-to-run variance. Model-shaped = the provider cleared it on the same retrieved context, confirming capability rather than retrieval.

This yields a four-way decision:

| Base vs. bar | Gap to provider | Diagnosis | Action |
| --- | --- | --- | --- |
| Clears bar | Small | Adequate | Ship base locally — stop. |
| Clears bar | Large | Adequate but behind frontier | Usually ship base; train only if the gap materially helps the use case and lifecycle cost is justified. |
| Fails bar | Provider also weak | Retrieval / data problem | Fix RAPTOR / CAG / prompting; do not train. |
| Fails bar | Provider clears it | Genuine capability gap | Train; use the provider as the distillation teacher. |

Judge per capability, not globally: base may clear the bar for extraction yet fail SQL generation, in which case only the SQL skill is trained — cheaper and lower-risk than retraining everything.

#### Progressive Training Ladder

When training is warranted, it runs as a measured staircase, each rung benchmarked against the provider baseline so the gain of each step is attributable. A category distinction is kept explicit: QLoRA is the training method (held constant — it fits training on bounded hardware by freezing a quantized base and training small low-rank adapters); SFT and knowledge distillation are training objectives run through that method. They differ only in where the labels come from — SFT uses Aegis’s own gold targets; distillation uses the teacher provider’s outputs and reasoning traces.

Three objective configurations, all via QLoRA: SFT-only, distillation-only, and SFT-then-distillation — each forked from the same base. The combined run is the likely production recipe; the two isolated runs are diagnostic, revealing whether the stages are additive, redundant, or in conflict.

Merge between stages: For SFT-then-distillation, the SFT adapter is merged into the base before the distillation pass, so each rung is a clean frozen starting point and adapter interactions do not confound the measurement.

Watch a per-capability curve, not one number: Training often trades one skill for another (e.g., improving SQL while degrading faithfulness). Each rung is gated by the Optimization Regression Engine (Section 13.1): no previously-passing capability may regress.

Stopping rule: Climb only until a rung clears every capability bar, then ship that rung — the lowest-complexity variant that passes — even if the provider is still nominally ahead. If SFT-only clears the bar, distillation is never paid for.

Diagnostic payoff: The gap closed at each rung is itself informative: if SFT closes most of it, the problem was format/behaviour; if only distillation closes it, the problem is genuine reasoning capability — which may instead argue for a larger base model rather than more distillation.

### 11.7 Module 7: Web Research & Real-Time Grounding Agent

Forecasts must reflect current reality — latest news, tariff and regulatory announcements, market conditions — not only the filings. Aegis adds a Web Research agent (a LangGraph specialist) that retrieves high-fidelity public web data and folds it into projections, while the SEC filings and ledger remain the primary source of truth.

#### Retrieval Layer (agent-native search, not raw SERP)

The agent uses AI-native search APIs that return clean, structured, cited content with source URLs and timestamps (for the audit trail), rather than human-oriented result snippets that require a separate scraping layer.

Candidates (2026): Exa (semantic search with company/finance/news categories, field-level citations, and a zero-data-retention option); Tavily (agent-native, with finance and news topics, recency filters, and a multi-step research endpoint); Firecrawl (clean markdown plus full metadata/timestamps, strong deep extraction); Valyu (covers SEC filings and finance sources, strong on finance and time-sensitive benchmarks); Perplexity Sonar / Brave for synthesized or independent-index needs.

Recommendation: A provider-agnostic search abstraction (mirroring the model abstraction), integrated via MCP — these providers publish MCP servers, consistent with P7 — defaulting to a finance-capable, citation-preserving, ZDR provider (Exa or Valyu) with Firecrawl for deep page extraction. Prefer primary sources (SEC, company investor relations, reputable financial press).

#### Autonomous Research Loop (AgentQ-inspired)

For multi-step research the agent runs an iterative deep-research loop: decompose the objective, search, read/extract, update its working knowledge, re-query with refined questions, and stop at a coverage or budget limit — the documented shift from one-shot search to agentic research. It borrows AgentQ’s robustness mechanisms: guided search (MCTS-style exploration balancing exploration and exploitation), AI self-critique at each step as an intermediate reward to steer the search and catch dead ends, and — when training — DPO over successful versus failed research trajectories to make the agent self-healing and resistant to compounding errors.

#### Grounding & Provenance Discipline (non-negotiable)

Augmentation, not authority: Web data adds timely context (e.g., a just-announced tariff that sharpens a bear case); the crux of every forecast derives from the filings and ledger the system already holds.

Provenance: Every web-sourced claim carries its source URL and retrieval timestamp into the Grounding tier of the four-tier audit trail, tagged distinctly from filing-sourced claims so reviewers can separate internal from external evidence.

Conflict handling: Disagreements between web data and filings trigger the RAGAS self-correcting loop and are surfaced, never silently resolved.

Quality controls: Recency/time-range filters, source reputation and whitelisting, deduplication, and faithfulness scoring of web-augmented answers.

#### Privacy & Governance

Web queries are built from public entity names and public facts only; MNPI and ledger specifics are never placed in a query or URL. ZDR search providers are preferred, and the agent is subject to the same data-classification gate as Module 6.

## 12. Projections, Scenario Analysis, & Hyper-Granular Explainability

Aegis goes beyond traditional search paradigms by allowing analysts to run predictive “What-If” calculations (e.g., “Simulate a 15% increase in operational supply costs due to the supply chain tariffs flagged on page 45 of the 10-K”). Scenarios may incorporate real-time signals supplied by the Web Research agent (Module 7) — provenance-tagged and treated as augmentation — while the filings and ledger remain the primary basis for every projection.

### 12.1 Deterministic Arithmetic Sandboxing

LLMs are notoriously unreliable for multi-step math calculations. To ensure complete numerical accuracy, the Forecasting Agent never attempts complex math inline. Instead, it extracts the target metrics via the Postgres MCP, writes a clean Python calculation script, and executes it inside an isolated code sandbox. The calculated data matrices are then parsed back into the agentic workflow.

### 12.2 The Mathematical Audit Trail

To ensure boardroom trust, any projection or discovered deficit must produce an explicit, granular explanation trail.

Let B represent the historical financial baseline pulled from the PostgreSQL ledger, δ represent the user’s parameter variance modifier, and L_f define the projected future operational liability. The agent processes calculations using a deterministic sequence:

L_f = B * (1 + δ)^t

The generated answer is displayed in the UI using a Four-Tier Verification Layout:

The Premise: The baseline value extracted from the Postgres ledger (including transaction log references).

The Parameterization: The specific user input delta applied to the calculation matrix.

The Equation: The explicit formula executed within the calculation sandbox.

The Grounding: The exact section text and page quote extracted from the RAPTOR index, explaining why that specific risk is compounding.

+----------------------------------------------------------------------------+

|                          EXPLAINABILITY AUDIT TRAIL                        |

+----------------------------------------------------------------------------+

| [1] LEDGER BASELINE (Postgres MCP): $142,500,000.00 (ID: L-98421)          |

| [2] USER VARIANCE PARAMETER       : Delta +15.00% Operational Cost Surge   |

| [3] APPLIED CALCULATED MATRIX     : $142,500,000 * (1 + 0.15)^1 = $163,875,000 |

| [4] GROUNDED SOURCE TEXT (RAPTOR) : 'Section 1A, Risk Factors, p. 45:      |

|     Tariff re-adjustments on raw materials projected to drive base +12-18%'|

+----------------------------------------------------------------------------+

### 12.3 Memory Compartmentalization

When running multiple scenario models simultaneously (e.g., Bull Case vs. Bear Case), the Supervisor Agent instantiates completely separate LangGraph thread contexts. This keeps the data streams isolated and prevents numbers from Scenario A from leaking into the context window of Scenario B.

## 13. Evaluation, Drift Suite, & User Interface

To move this system beyond an experimental phase and turn it into a true AI platform engineering piece, Aegis features a production-grade testing and optimization workspace.

### 13.1 The Continuous Evaluation Suite

The system includes a dedicated engineering panel running automated continuous assessment engines:

Continuous RAGAS Logging: Tracks Faithfulness, Context Recall, and Answer Relevance scores over all active sessions to capture long-term performance trends.

Data & Concept Drift Monitors: Monitors the distribution characteristics of incoming document formats and database transaction volumes. If target firms shift their reporting styles or tax codes change, the monitor triggers a “Concept Drift Warning,” indicating that the RAPTOR index tree needs to be rebuilt.

Optimization Regression Engine: Whenever a system administrator changes optimization layers (e.g., swapping a 4-bit model in llama.cpp for an 8-bit weights-only configuration on a vLLM node, or switching the server engine between vLLM and SGLang), the system initiates a background testing script. This engine runs synthetic multi-step prompt evaluation sets to verify that the optimized layout has not caused a regression in the model’s analytical reasoning or mathematical accuracy.

KV Cache Residency Monitor (new in v2.0): Tracks the hit rate and eviction frequency of the CAG regulatory prefix (Module 2, Tier 1). A sustained drop in hit rate under concurrent load is the explicit trigger for promoting the rulebook to the Tier 2 persistent cache (LMCache). Before/after time-to-first-token is captured as a regression-suite artifact.

### 13.2 User Interface Architecture

The front-end layout is cleanly divided into two separate workspaces:

The Financial Analyst Workspace: A streamlined interface containing document drop nodes, conversational panels, report configuration triggers, and interactive Tableau charts showing projected operational deficits.

The Platform Engineer Control Panel: Provides deep system observability. It monitors vLLM / SGLang iteration batching speeds, token-per-second generation metrics, active memory allocations across the multi-tiered memory caches, RAGAS health indices, KV cache residency / hit-rate (including RadixAttention prefix reuse), and system drift parameters.

## 14. Implementation Roadmap

To begin building Project Aegis step-by-step, follow a structured execution path:

Phase 1 (Data & Storage Setup): Write the initial script to download target 10-K filings using programmatic SEC tools and build the Python Faker template to populate the matching local PostgreSQL ledger.

Phase 2 (Inference Architecture): Stand up the co-primary server engines (vLLM and SGLang) behind a single OpenAI-compatible endpoint, enable shared-prefix KV reuse (APC / RadixAttention) with per-session cache isolation, configure llama.cpp / GGUF for edge clients, and verify token delivery metrics. Ollama is used for local dev only.

Phase 3 (Ingestion & RAG): Build the structure-routed hybrid index (PageIndex-style ToC navigation + within-node RAPTOR summarize-or-split with an oversized-node threshold), construct the self-correcting RAG loop, and establish the CAG rulebook prefix (Tier 1).

Phase 4 (Agentic Routing): Define the multi-agent LangGraph node relationships and implement the Model Context Protocol (MCP) integrations.

Phase 5 (Evaluation & Hardening): Stand up the RAGAS logging, drift monitors, regression engine, and KV residency monitor; evaluate whether the Tier 2 persistent cache is warranted.

Phase 6 (Model Strategy & Benchmarking): Build the provider abstraction and data-classification gate; baseline the sovereign base model against external providers; then run staged training (SFT → distillation → DPO), each stage regression-gated, and pick the production model from the benchmark.

Phase 7 (Web Research Agent): Add the provider-agnostic web search abstraction via MCP, implement the AgentQ-style autonomous research loop, and wire web provenance and conflict handling into the audit trail and self-correcting loop.

Phase 8 (Holistic Data Expansion): Light up the remaining facets in order of cost — Operational (extend the Postgres schema with customer/supplier/HR tables), then Legal (onboard a contract corpus via RAPTOR using EDGAR exhibits / CUAD / a simulated data room), then Compliance (add the compliance register paired with CAG rules). Each facet ships behind the data-adaptive contract (Section 10.2), with coverage reporting, before the next is added.

## 15. Open Items & Risk Register

The following technical claims from the original draft were left unchanged in this revision but should be pressure-tested before implementation:

Paged Attention fragmentation figure: The original draft cited a reduction from ~60% fragmentation to “near 0%.” The qualitative claim (large reduction) is sound; the specific figures should be replaced with measured numbers from your own hardware rather than stated as fact.

RAGAS threshold values: The faithfulness < 0.85 and answer_relevance < 0.80 cutoffs are placeholders. These should be calibrated against a labeled validation set, not hardcoded on intuition.

RAPTOR leaf size (~300 tokens): A reasonable default, but optimal chunk size for dense financial tables vs. prose differs; worth an ablation.

## 16. Glossary

RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval — a hierarchical index built by recursively clustering and summarizing text into a tree; used here as the within-node summarize-or-split mechanism.

PageIndex: A vectorless, reasoning-based retrieval approach that builds a table-of-contents tree from a document’s natural structure and uses LLM reasoning to navigate to relevant sections; used here for the structural-navigation phase.

Structure-Routed Hybrid Retrieval: Aegis’s retrieval design — PageIndex-style ToC navigation to the correct node, then within-node RAPTOR (summary for global queries, span search for local queries) to avoid context overflow and needle-in-section loss.

Retrieval Plan / (node, intent) instruction: The set of typed instructions navigation emits for a compound query, each pairing a target node with the granularity its sub-question needs (global summary or local span).

Coverage Check: A verification, ahead of the faithfulness gate, that the assembled retrieved context addresses every sub-question a compound query was decomposed into.

CAG (Cache-Augmented Generation): Serving a fixed corpus by keeping its precomputed KV state resident and reused, instead of retrieving it per query.

KV Cache: The Key/Value vectors computed per token during prefill; caching them avoids recomputation on reuse.

APC (Automatic Prefix Caching): vLLM’s best-effort reuse of KV blocks across requests that share an exact prompt prefix; LRU-evicted.

RadixAttention: SGLang’s prefix-cache mechanism storing KV state in a radix tree, enabling multi-level prefix sharing and fork/branch sharing across all concurrent requests.

PagedAttention: vLLM technique that stores the KV cache in non-contiguous fixed-size pages to eliminate memory fragmentation.

Continuous Batching: Iteration-level scheduling that admits new requests into the running batch at token boundaries to raise throughput.

TTFT: Time-to-first-token — latency from request to the first generated token; reduced by prefix caching.

GGUF: The quantized model file format used by llama.cpp for edge/CPU deployment.

Quantization (Q4_K_M / Q8_0): Reducing weight precision to 4-/8-bit to cut memory use with minimal quality loss.

MCP (Model Context Protocol): Anthropic’s open JSON-RPC protocol letting agents call external tools (e.g., Postgres, Tableau) through a uniform contract.

RAGAS: A framework of metrics (e.g., faithfulness, answer relevance, context recall) used to score and gate RAG output.

GMM (Gaussian Mixture Model): The clustering method RAPTOR uses to group leaf embeddings before summarization.

MNPI: Material Non-Public Information — confidential data whose external transmission is prohibited.

LMCache: A persistent, tiered (GPU→CPU→SSD) KV-cache store used for CAG Tier 2 residency guarantees.

Working / Episodic / Semantic Memory: Active task state / short-term session buffer / long-term durable fact store, respectively.

Memory Compaction: A background process that distills episodic logs into semantic facts and purges redundant transcripts.

Concept / Data Drift: Shifts in document structure, reporting style, or data distribution that may require index rebuilds.

Self-Correcting Loop: A generation cycle wrapped in RAGAS scoring that reformulates and retries when quality is too low.

Supervisor / Specialist Agent: The orchestrating LangGraph node and its delegated domain nodes (Financial, Legal, Forecasting, Data-Tooling).

LangGraph: The framework used to express the hierarchical agent state machine.

Vector DB (Qdrant): The store holding embeddings for RAPTOR leaves and semantic memory.

EDGAR: The SEC’s public system for downloading company filings (10-K / 10-Q).

CDC (Change Data Capture): Detecting new/changed records (files or ledger rows) to trigger event-driven ingestion.

Claims layer vs. Evidence layer: What a filing asserts (claims) versus the granular records that verify it (evidence); auditing is the cross-check of one against the other.

Capability Tiers / Data-Adaptive Operation: The model by which Aegis runs on a minimal data set and progressively enables more diligence facets (Legal, Operational, Compliance) as their evidence layers are added.

Data Room: The secured repository where, in a real transaction, a target company lawfully provides its internal records (including MNPI) to the diligence party under NDA.

CUAD: The Contract Understanding Atticus Dataset — a public, clause-annotated corpus of legal contracts usable as a real proxy for the Legal facet.

Sovereign Model: Aegis’s own fine-tuned, locally-hosted model — the default inference backend.

Provider Abstraction / Operating Modes: A router that makes local engines and external providers interchangeable; Sovereign Mode is local-only, External Mode is governed opt-in.

Data-Classification Gate: Policy layer that blocks confidential/MNPI payloads from external routing, permitting only public/synthetic data to leave the host.

SFT (Supervised / Instruction Fine-Tuning): Training a base model on curated instruction–response pairs to adapt it to task formats.

LoRA / QLoRA: Parameter-efficient fine-tuning methods that train small adapter weights (QLoRA over a quantized base), enabling training on bounded hardware.

Knowledge Distillation (Teacher/Student): Training a smaller student model on the outputs or reasoning traces of a larger teacher model.

DPO (Direct Preference Optimization): Preference-based training on pairs of better/worse responses; used here for multi-step agentic robustness.

MCTS (Monte Carlo Tree Search): A guided search over action sequences balancing exploration and exploitation; used in AgentQ to generate agent trajectories.

AgentQ: A web-agent training framework (MultiOn) combining guided MCTS, AI self-critique, and off-policy DPO for self-healing autonomous agents.

ZDR (Zero Data Retention): A provider mode that purges queries/data after serving, preferred for privacy-sensitive web search.

Deep Research Loop: An iterative search–read–refine–research cycle that gathers and cross-checks many sources before answering.

Exa / Tavily / Firecrawl / Valyu: Agent-native web search/extraction APIs returning clean, cited, structured content; Valyu additionally covers SEC and finance sources.
