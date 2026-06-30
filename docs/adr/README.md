# `docs/adr/` — Architecture Decision Records

One short, immutable record per significant design decision: the context, the choice, and the
consequences. ADRs are append-only — when a decision is reversed, write a new ADR that supersedes
the old one rather than editing history. This is how we keep the *why* behind the spec auditable.

- **`0000-template.md`** — copy this for new records.
- Naming: `NNNN-short-title.md`, zero-padded, incrementing.

Write an ADR when: choosing between technologies (e.g. vLLM vs SGLang routing), changing a spec
decision, or making a tradeoff a future reader would otherwise question.
