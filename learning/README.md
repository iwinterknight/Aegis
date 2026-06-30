# `learning/` — Programming Exercises & Quizzes

The hands-on half of the learning loop. Where `docs/primers/` *explains* a concept, this is where
you *practice* it. Organized by **type first, then build phase** so exercises and quizzes are cleanly
separated (as requested).

| Directory | Contents |
|---|---|
| [`exercises/`](exercises/) | Coursera-style programming exercises — notebooks (`.ipynb`) or executable scripts. Each fully explains the code, then has you implement marked `# TODO` sections. They run and show real results. |
| [`quizzes/`](quizzes/) | Checkpoint quizzes (Markdown) — short, targeted questions to lock in foundations before the build. |
| [`solutions/`](solutions/) | Reference solutions, kept **separate** so the exercise files stay unsolved. Open only after attempting. |

Each of the three is subdivided by build phase, e.g. `exercises/phase-1-data-storage/`.

## Exercise conventions

- **Marked gaps:** code you write is fenced by `# ==== YOUR CODE HERE (start) ====` /
  `# ==== YOUR CODE HERE (end) ====`, with a one-line spec of the expected behavior above it.
- **Runnable:** every exercise runs end-to-end and prints/plots a result you can verify against an
  expected output stated in the notebook.
- **Self-checks:** where practical, an `assert`-based check cell tells you if your implementation is
  correct before you peek at `solutions/`.
- **Scale notes:** when a demo is scaled down to fit the 16 GB laptop GPU, the notebook says so and
  notes what the production-scale version (Colab A100) would change.

## Naming

`exercises/phase-<N>-<slug>/<NN>_<topic>.ipynb` — e.g. `phase-1-data-storage/01_faker_seeded_ledger.ipynb`.
Quizzes mirror it: `quizzes/phase-1-data-storage/checkpoint.md`.
