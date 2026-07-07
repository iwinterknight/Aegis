"""Canonical ingestion records — the contract boundary of Project Aegis.

These Pydantic v2 models sit between the *untrusted external world* (SEC XBRL /
`companyfacts` JSON, the synthetic ledger, later FFIEC Call Reports) and the
*trusted Aegis interior* (evidence store, agents, evaluation). Validation fires
at construction: a record that violates an invariant here never comes into
existence — so everything downstream can assume the data is well-formed.

Design decision & alternatives: docs/adr/0002-pydantic-v2-ingestion-contract.md.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)


class ClaimRecord(BaseModel):
    """One financial fact a company *claims* in an SEC filing.

    A single reported figure — e.g. *JPMorgan Liabilities = $4.06T as of
    2025-12-31, Form 10-K* — carrying the provenance needed to trust and trace
    it. This is the concrete "canonical record" ADR-0001 referred to, and the
    left operand of SG-1 (claimed value vs. ledger sum).

    Bitemporal by construction — a fact lives on two independent time axes:
      * *valid time*     — ``period_end`` (+ optional ``period_start``): the
                            period the fact describes.
      * *knowledge time* — ``filed`` / ``accession``: when we learned it.
    A restatement is a *new* ``ClaimRecord`` with the same valid time and a
    later knowledge time. Records are immutable and stored append-only, so the
    history (as-originally-reported vs. as-restated) is never lost. Choosing a
    single value for a given purpose is a separate, read-time concern (WI-13),
    deliberately kept out of this value object.
    """

    # frozen -> immutable value object (a reported fact is history; never mutate
    # it) and hashable (safe to dedup/cache). extra="forbid" -> since we build
    # these ourselves, a mis-named kwarg fails loudly instead of being ignored.
    model_config = ConfigDict(frozen=True, extra="forbid")

    # --- what was claimed -------------------------------------------------
    concept: str = Field(min_length=1)   # us-gaap tag, e.g. "Liabilities"
    unit: str = Field(min_length=1)      # e.g. "USD" — never assumed
    value: Decimal                       # money -> exact; the SG-1 operand

    # --- which period it describes (valid time) ---------------------------
    period_end: date                     # the "as of" instant / balance-sheet date
    period_start: date | None = None     # set only for *duration* concepts (Revenue)

    # --- provenance / knowledge time (trace it back to the exact filing) --
    fiscal_year: int = Field(ge=1900, le=2200)
    fiscal_period: str = Field(min_length=1)  # "FY", "Q1", ...
    form: str = Field(min_length=1)           # "10-K", "10-Q", ...
    filed: date                               # when it hit EDGAR
    accession: str = Field(min_length=1)      # unique filing id — trace-back key
    cik: str = Field(min_length=1)            # SEC Central Index Key — whose fact

    @field_validator("value", mode="before")
    @classmethod
    def _reject_float_money(cls, v: object) -> object:
        """Guard the money invariant *before* coercion.

        A ``float`` has already lost precision before it reaches us (JSON's
        `1.23` is IEEE-754, not exact cents). Require the caller to pass a
        ``str`` / ``int`` / ``Decimal`` so exactness is preserved end to end.
        """
        if isinstance(v, float):
            raise ValueError(
                "monetary value must not be a float (precision loss); "
                "pass a str, int, or Decimal"
            )
        return v

    @model_validator(mode="after")
    def _check_period_order(self) -> ClaimRecord:
        """Cross-field invariant: a duration cannot end before it starts."""
        if self.period_start is not None and self.period_start > self.period_end:
            raise ValueError(
                f"period_start ({self.period_start}) must be <= "
                f"period_end ({self.period_end})"
            )
        return self

    @field_serializer("value", when_used="json")
    def _serialize_value(self, v: Decimal) -> str:
        """Emit money as a JSON *string* to preserve exact cents.

        JSON has no decimal type; a float round-trip would corrupt the value.
        (Pydantic v2 already does this by default — we make the binding
        money-as-string guarantee explicit so it can't silently change.)
        """
        return str(v)