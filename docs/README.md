# `docs/` — Documentation

All **prose/document** artifacts for Project Aegis. Code lives in `src/`; learning material
(exercises, quizzes) lives in `learning/`. Each subdirectory holds one *type* of document.

| Directory | Document type | Produced during |
|---|---|---|
| [`specs/`](specs/) | The living, version-controlled system specification (source of truth) + the original `.docx` seed | Maintained continuously |
| [`primers/`](primers/) | Concept primers — top-down explainers of one technology/concept (problem → place in Aegis → internals → enterprise usage) | Loop phase ① Deep Dive |
| [`discussion-notes/`](discussion-notes/) | Running logs of salient points from our deep-dive discussions, per build phase | Loop phase ① Deep Dive |
| [`build-summaries/`](build-summaries/) | Top-down write-ups of a completed module (objective → functional → syntax), citing concepts + principles + a discussion recap | Loop phase ⑤ Build Summary |
| [`adr/`](adr/) | Architecture Decision Records — one file per significant design decision and its rationale | Whenever a design choice is made/changed |
| [`reference/`](reference/) | External reference material, cheat-sheets, links, glossaries | As needed |

Top-level docs:
- [`00_OPERATING_MODEL.md`](00_OPERATING_MODEL.md) — the binding contract for how we build & learn.
- [`BUILD_LOG.md`](BUILD_LOG.md) — chronological log tied to commits and FR-IDs.

See [`00_OPERATING_MODEL.md`](00_OPERATING_MODEL.md) for the full 5-phase loop these artifacts come from.
