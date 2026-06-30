# Project Aegis — Operating Model (How We Build & Learn)

This document is the **contract** for how Project Aegis is developed. It is binding on every
module until we revise it together. It exists because this build is, by design, a **learning
exercise first** and a software delivery second: when a module is done, the goal is that I
(the developer) understand the technology's inner workings, how Aegis uses it, and how I'd
apply it to an enterprise standard.

## Roles

- **Developer (Sunit):** Strong software engineer, newer to ML / LLM infrastructure. Drives the
  learning — asks questions, does independent research, pushes back on design.
- **Claude:** Spec-driven development partner, instructor, and pair. Runs the loop below, keeps
  the spec and git history honest, and produces all learning + reporting artifacts.

## Compute envelope

- **Local dev:** Laptop — NVIDIA RTX 3080 Ti Laptop GPU, **16 GB VRAM**, Ampere (compute 8.6),
  driver 581.95. Good for: embedding models, RAPTOR/RAG dev, quantized 7–8B serving, GGUF/llama.cpp
  edge work, QLoRA on small bases (e.g. Phi-class). bf16 + FlashAttention supported.
- **Heavy lifting:** Google Colab top tier (A100 40 GB) — used for larger QLoRA, distillation,
  bigger-model serving demos, and throughput benchmarks.
- **Principle:** Exercises always teach the *mechanism* even when scaled to fit. We state when a
  demo is scaled down and what the production-scale version would change.

## The per-module loop (five phases)

Every technical module runs this loop. Artifacts in **bold**.

1. **① Deep Dive (discussion).** Concepts introduced top-down: *problem it solves → where it sits
   in Aegis → how it works under the hood → industry/enterprise-standard usage*. Developer
   interrogates and researches. Produces **`docs/discussion-notes/<module>.md`** (a running log of
   salient points, updated live) and a **`docs/primers/<concept>.md`** concept primer per cluster.
2. **② Guided Exercises (Coursera-style).** Executable notebooks/scripts under
   **`learning/<module>/`**. Each fully explains the code, then has the developer implement marked
   sections (fill-in-the-blank → build-this-function). They run and show real results.
3. **③ Checkpoint quiz.** Short, targeted — **`learning/<module>/quiz.md`** — to lock foundations
   before building.
4. **④ SDD Build.** Spec → plan → tasks → implement. Production code under **`src/`**, small commits,
   each message referencing the FR-ID it satisfies. Branch per module, tag per phase.
5. **⑤ Build Summary.** **`docs/build-summaries/<module>.md`**, written top-down:
   *module objective → functional composition → syntax-level salients*, explicitly citing the
   concepts from ①, calling out the **SWE/MLOps principles** in play, and ending with a
   **"Salient Points from Our Discussion"** recap gathered from the deep-dive notes.

We do not start ④ until the developer signals they're clear on ①–③.

## Git discipline

- **Branch per module/phase:** e.g. `phase-1/data-storage`, `phase-2/inference`.
- **Conventional commits referencing FR-IDs:** `feat(ingestion): async EDGAR pull [FR-IN-1]`,
  `test(ledger): seeded-discrepancy fixture [SG-1]`.
- **Tag at phase completion:** `v0.1-phase1`, etc.
- **Commit/push only when asked.** The build log (`docs/BUILD_LOG.md`) records what landed and why.
- **Living spec:** `docs/specs/Project_Aegis_System_Specification.md` is the source of truth.
  Design refinements from discussion are committed there as reviewable diffs (the `.docx` is the
  original seed, kept for reference).
- **Multi-machine sync (binding):** development spans two machines. Run `scripts/setup-sync.*` once
  per machine; thereafter every commit auto-includes the SDD files **and** the Claude Code
  conversation thread (`conversations/`). Pull when starting, push before stopping/switching. Full
  detail: `docs/MULTI_MACHINE_SYNC.md`.

## Repository layout

```
docs/                     # all prose/document artifacts (see docs/README.md)
  specs/                  # living Markdown spec (source of truth) + original .docx seed
  primers/                # concept primers from deep dives
  discussion-notes/       # running salient-point logs per build phase
  build-summaries/        # top-down module write-ups
  adr/                    # architecture decision records (design changes & why)
  reference/              # external reference material, cheat-sheets, links
  BUILD_LOG.md            # chronological build log tied to commits/FR-IDs
  00_OPERATING_MODEL.md   # this file
learning/                 # hands-on learning artifacts (see learning/README.md)
  exercises/<phase>/      # Coursera-style notebooks/scripts with marked gaps
  quizzes/<phase>/        # checkpoint quizzes
  solutions/<phase>/      # reference solutions (kept separate from exercises)
src/                       # the Aegis system itself
```

Each directory carries its own `README.md` explaining its purpose, so the tree is self-documenting.

## Reporting standard (top-down, three altitudes)

Every build summary answers, in order:
1. **Objective altitude** — what the module is *for* in Aegis and which FRs/principles it serves.
2. **Functional altitude** — how the pieces fit: data flow, components, the design decisions.
3. **Syntax altitude** — the salient lines of code: idioms, gotchas, why-this-not-that.

## Concept coverage commitment

Industry-standard concepts to be taught to enterprise-application depth across the build include
(non-exhaustive): PagedAttention, continuous batching, RadixAttention (SGLang), APC (vLLM), CAG,
LMCache, quantization/GGUF; Agentic RAG, RAPTOR, PageIndex, structure-routed retrieval, metadata
filtering, GMM clustering, RAGAS self-correction; MCP/JSON-RPC tooling; LangGraph hierarchical
agents; QLoRA, SFT, knowledge distillation, DPO, AgentQ/MCTS; agent-native web search; plus the
SWE/MLOps practices (event-driven/async pipelines, CDC, observability/tracing, regression gating,
drift monitoring, reproducibility) that make it enterprise-grade.
