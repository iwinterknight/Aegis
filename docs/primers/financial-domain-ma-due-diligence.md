# Primer: The Financial Domain — M&A Due Diligence (and IPO valuation)

The "what and why" of the finance that Project Aegis automates, written for a strong software
engineer who is new to finance. Software analogies are used deliberately.

---

## 1. The business context: M&A and due diligence

**M&A (Mergers & Acquisitions)** = one company buying or combining with another. The buyer is the
**acquirer**; the company being bought is the **target**. Done for growth, synergies, market access,
talent, technology, or to remove a competitor — often for hundreds of millions to billions of dollars.

**Deal lifecycle:** sourcing → Letter of Intent (LOI) → **due diligence** → negotiation → close →
integration.

**Due diligence (DD)** is the investigation phase: "trust, but verify." Before committing billions,
the buyer examines the target's books, contracts, operations, and compliance to find anything that
changes the price or kills the deal. It takes **3–6 months** because it spans thousands of documents
and many specialists, with enormous stakes.

The core economic reason DD exists is **information asymmetry**: the seller knows far more about the
target than the buyer. DD shrinks that gap. A **hidden liability** discovered in DD is either a
deal-killer or a price-renegotiation lever — which is exactly what Aegis hunts for.

Who does it: Corporate Development teams (in-house M&A), private equity firms, investment banks, plus
their lawyers and accountants. (These are Aegis's personas, §3.)

---

## 2. The four facets (what gets investigated)

Diligence examines a target along four **facets**. Aegis mirrors this exactly (§10.2):

| Facet | The question it answers | Aegis status |
|---|---|---|
| **Accounting / Financial** | Are the numbers real? Do the statements reflect reality? | **MVP focus** — fully functional on minimal data |
| **Legal** | What's in the contracts? Change-of-control, IP, litigation, leases? | Progressive (Tier 2) |
| **Operational** | Customer concentration/churn, supplier risk, employee attrition? | Progressive (Tier 1) |
| **Compliance** | Licenses, permits, certifications, past violations? | Progressive (Tier 3) |

The unifying idea — **claims vs evidence** — is the most important concept in the whole project:

- **Claims layer** = what the target *asserts*. Lives in the filings (public, narrative, summarized).
- **Evidence layer** = the *granular records* that verify or contradict the claim (transaction-level,
  detailed, internal).

> **Auditing = cross-checking the claims layer against the evidence layer.** That single sentence is
> what turns Aegis from a search engine into an *auditor*. (Spec glossary: "Claims layer vs Evidence
> layer".)

---

## 3. SEC filings & financial statements (the claims layer)

US public companies must file with the **SEC (Securities and Exchange Commission)**. Key filings:

| Filing | What it is |
|---|---|
| **10-K** | Annual report. Comprehensive: business overview, risk factors, MD&A, **audited** financial statements, and footnotes. The primary Aegis input. |
| **10-Q** | Quarterly report. Lighter, **unaudited**. |
| **8-K** | "Current report" — material events as they happen (ad hoc). |
| **S-1** | IPO registration statement (the second vertical). |

Inside a 10-K, the three core **financial statements**:

1. **Balance Sheet** — a *snapshot* at a point in time. Governed by the fundamental accounting
   equation: **Assets = Liabilities + Equity** (what you own = what you owe + the owners' stake).
2. **Income Statement (P&L)** — over a *period*: **Revenue − Expenses = Net Income**. Did they profit?
3. **Cash Flow Statement** — actual cash in/out (operating, investing, financing). Crucial because
   **profit ≠ cash** (you can be profitable on paper and out of cash).

Two narrative-but-critical parts:
- **Footnotes** — "the devil is in the footnotes": lease terms, contingencies, debt covenants,
  accounting policies. The spec's running example — a lease liability mentioned on p.12 and explained
  in a footnote on p.240 — lives here. (This is *why* Module 2's structure-routed retrieval exists.)
- **MD&A (Management Discussion & Analysis)** — management's narrative on results and risks.

---

## 4. The general ledger & double-entry (the evidence layer) — the key mechanism

This is where the audit actually bites, and where the software analogies are strongest.

- **General Ledger (GL)** = the complete record of *every* financial transaction, the source from
  which the financial statements are *summarized*. **Analogy:** the financial statements are a
  `GROUP BY ... SUM()` aggregation; the GL is the raw transactions table underneath.
- **Double-entry bookkeeping** = every transaction touches at least two accounts, a **debit** and a
  **credit**, that must always balance (**debits = credits**). **Analogy:** a built-in checksum /
  conservation invariant on every write — a 600-year-old error-detection system. If the books don't
  balance, something is wrong by construction.
- **Chart of accounts** = the typed categories every entry maps to: assets, liabilities, equity,
  revenue, expenses.

**Why this is the heart of Aegis (SG-1, FR-IN-2):**
The 10-K claims "lease liabilities = $X" — a single aggregate *claim*. The ledger holds the
individual lease transactions that should `SUM()` to $X — the *evidence*. If
`SUM(ledger rows) ≠ claimed $X`, that delta is a discrepancy — a potential hidden liability. Aegis's
MVP is literally: pull the claim, sum the evidence, flag the delta, cite both sides.

### The constraint that shapes ALL data decisions

```
PUBLIC  (filed with SEC, audited, summarized)   →  10-K, financial statements    ← CLAIMS are real & live
------------------------------------- waterline -------------------------------------
PRIVATE (internal, transaction-level, MNPI)     →  trial balance, GL, journals   ← EVIDENCE is never public
```

A public company publishes **summarized, audited statements** (the claims) but **never** its
transaction-level general ledger — that's internal, confidential, and for a real target it is **MNPI
(Material Non-Public Information)**. In a real deal it's disclosed only inside a **data room** under
**NDA**.

Consequence for Aegis (and for our "use real/live data" goal):
- The **claims** layer (filings) **can be 100% real, live, and free** — straight from SEC EDGAR.
- The **evidence** layer (the GL) **cannot be real** for a public company — so the spec **simulates**
  it with Faker, deliberately scripted to *match or conflict* with the filing (FR-IN-2). Ingestion is
  **source-agnostic** (FR-DATA-5) so a lawfully-provided real ledger could swap in later with no
  redesign. This is not a shortcut — it's the only lawful design, and it's *why* Aegis can own its
  evaluation ground truth by construction (§11.6).

---

## 5. What auditors actually hunt (so "seeded discrepancy" means something)

Real-world financial red flags Aegis is modeling:

- **Revenue recognition games** — booking revenue too early, channel stuffing, round-tripping.
- **Hidden / understated liabilities** — off-balance-sheet items, under-reported leases (the spec's
  example), undisclosed debt.
- **Related-party transactions** — deals with insiders that inflate results.
- **Earnings management** — "cookie-jar" reserves smoothed across quarters.
- **Inventory / asset misstatement**, **expense capitalization** tricks.

A **seeded discrepancy** = we deliberately plant one of these (e.g. ledger sums to $Y while the filing
claims $X) so we have a **known-correct answer** to test detection against. This is the engine behind
Aegis's evaluation strategy: because we built the landmine, we know exactly where it is.

---

## 6. The regulatory rulebooks (the rules layer)

- **GAAP (Generally Accepted Accounting Principles)** — the US rulebook for how transactions are
  recorded and reported (IFRS is the international counterpart).
- **IRS tax codes** — tax rules.

These are large, stable, and consulted constantly — so they go in the **CAG (Cache-Augmented
Generation)** prefix cache (Module 2), not per-query retrieval. The compliance check is: *does this
accounting treatment comply with the rule?*

---

## 7. The IPO vertical (the second vertical) — valuation, not audit

An **IPO (Initial Public Offering)** is a private company going public; it files an **S-1**. The
question shifts from *"are the numbers real?"* (audit) to *"what is it worth?"* (valuation):

- **Comparables ("comps")** — value the company by peer multiples:
  - **EV/Revenue**, **EV/EBITDA**, **P/E**.
  - **EV (Enterprise Value)** = market value of the whole business (equity + debt − cash).
  - **EBITDA** = Earnings Before Interest, Taxes, Depreciation & Amortization — a rough proxy for
    operating cash generation.
  - **P/E** = Price / Earnings.
- **DCF (Discounted Cash Flow)** — project future cash flows and discount them to today's value.
- **Bull / Bear** = optimistic vs pessimistic assumption sets fed through the same deterministic math
  (FR-PROJ-1/3) — *scenario analysis with explainability*, never a buy/price recommendation (stays
  inside Non-Goal #1).

---

## 8. Concept → spec mapping (the "why" behind the requirements)

| Financial concept | Why the spec is the way it is |
|---|---|
| Claims vs evidence | The entire premise; `FR-DATA-3` forbids presenting an unverified claim as reconciled |
| GL summarizes to statements | `FR-IN-2`, `SG-1`: sum the ledger, compare to the filing's claim |
| GL is private / MNPI | `FR-IN-2` simulates the ledger; `P1` zero-egress; `FR-DATA-5` source-agnostic swap |
| Footnotes hold the real risk | Module 2 structure-routed retrieval (find p.240 from a hint on p.12) |
| Double-entry must balance | Determinism (`P2`, `FR-PROJ-1`): arithmetic in a sandbox, never LLM guesswork |
| GAAP/IRS are stable references | CAG prefix cache (`FR-RAG-2`), not per-query retrieval |
| Auditors hunt known red flags | Seeded discrepancies give owned ground truth (`§11.6` eval) |
| Four facets | Data-adaptive tiers (`§10.2`, `P11`): operate on minimal data, light up facets as evidence arrives |
| Valuation (IPO) | Deterministic comps/DCF in the sandbox (`FR-PROJ-*`); bull/bear isolation (`FR-PROJ-3`) |
