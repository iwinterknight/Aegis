# Cheat-Sheet: Requirement IDs & Acronyms

Quick decoder for the short codes used throughout the spec and our discussions. The deep *technical*
terms (RAPTOR, PageIndex, PagedAttention, RadixAttention, etc.) live in the spec's own glossary,
§16 of `../specs/Project_Aegis_System_Specification.md`.

## ID types

| Code | Full form | Plain meaning |
|---|---|---|
| `FR` | Functional Requirement | Something the system must *do* |
| `NFR` | Non-Functional Requirement | *How well* it must do it — quality bars |
| `P` | Principle | A binding project-wide rule (the "constitution", P1–P11) |
| `SG` | Short-term Goal | An MVP milestone (SG-1…SG-5) |
| `LG` | Long-term Goal | The 12-month+ ambition |
| `§N` | Section N | "§" just means "section" of the spec |
| `M1`…`M7` | Module 1…7 | The seven technical execution modules |

Reading an ID: `FR-IN-2` = Functional Requirement · Ingestion area · item 2.

## FR family tags (the part after `FR-`)

| Tag | Area | Tag | Area |
|---|---|---|---|
| `FR-IN` | Ingestion & data | `FR-MOD` | Model strategy & providers |
| `FR-RAG` | Retrieval / RAG | `FR-WEB` | Web research & grounding |
| `FR-MEM` | Memory | `FR-DATA` | Data coverage & graceful scaling |
| `FR-MCP` | Tooling (MCP) | `FR-PROJ` | Projections & explainability |
| `FR-AG` | Agents & orchestration | `FR-EVAL` | Evaluation |
| | | `FR-UI` | User interface |

## NFR tags

| Tag | Quality attribute | Tag | Quality attribute |
|---|---|---|---|
| `NFR-PRIV` | Privacy | `NFR-RES` | Resource bounds |
| `NFR-PERF` | Performance / latency | `NFR-MAINT` | Maintainability / portability |
| `NFR-CORR` | Correctness | `NFR-GOV` | Governance |
| `NFR-OBS` | Observability | `NFR-PROV` | Provenance |

## Methodology & process acronyms

| Code | Full form | Notes |
|---|---|---|
| SDD | Spec-Driven Development | A versioned spec is the source of truth; code/plans/tasks/tests/evals derive from it |
| TDD | Test-Driven Development | Failing unit test first, then code to pass it |
| BDD | Behavior-Driven Development | Plain-English Given/When/Then scenarios |
| ADR | Architecture Decision Record | One file per significant design decision (`../adr/`) |
| MLOps | Machine Learning Operations | DevOps practices adapted for ML systems |
| CDC | Change Data Capture | Detecting new/changed records to trigger ingestion |

## Recurring technical acronyms (full forms; details in spec §16)

| Code | Full form |
|---|---|
| RAG | Retrieval-Augmented Generation |
| RAGAS | RAG Assessment (scoring framework: faithfulness, relevance, context recall) |
| MCP | Model Context Protocol (Anthropic's open tool-calling protocol over JSON-RPC) |
| KV cache | Key-Value cache (the per-token attention state; central to Module 1) |
| CAG | Cache-Augmented Generation |
| QLoRA / LoRA | (Quantized) Low-Rank Adaptation — parameter-efficient fine-tuning |
| SFT / DPO | Supervised Fine-Tuning / Direct Preference Optimization |
| MNPI | Material Non-Public Information (confidential data that must not leave the host) |
| M&A | Mergers & Acquisitions |
| IPO | Initial Public Offering |
| TTFT | Time-To-First-Token (latency to the first generated token) |
