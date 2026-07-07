"""Tests for the ClaimRecord ingestion model (ADR-0002).

These lock the boundary invariants the model exists to guarantee:
exact-Decimal money, immutability, required/constrained fields, the cross-field
period check, strict extras (typo protection), and lossless Decimal-as-string
JSON round-trips. The six Command-Gate scenarios are formalized here so a
regression is a red test, not a silent data bug downstream.
"""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from aegis.ingestion import ClaimRecord


def valid_kwargs(**overrides):
    """A complete, valid ClaimRecord field set; override one field to probe a rule."""
    base = dict(
        concept="Liabilities",
        unit="USD",
        value="4060000000000",
        period_end=date(2025, 12, 31),
        fiscal_year=2025,
        fiscal_period="FY",
        form="10-K",
        filed=date(2026, 2, 15),
        accession="0000019617-26-000123",
        cik="0000019617",
    )
    return {**base, **overrides}


# --- happy path ---------------------------------------------------------

def test_constructs_and_coerces_money_to_decimal():
    rec = ClaimRecord(**valid_kwargs())
    assert isinstance(rec.value, Decimal)
    assert rec.value == Decimal("4060000000000")
    assert rec.period_start is None  # optional; defaults to None (instant concept)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("5", Decimal("5")),            # string coerces
        (5, Decimal("5")),              # int coerces
        (Decimal("5.00"), Decimal("5.00")),  # Decimal passes through, scale kept
    ],
)
def test_money_accepts_exact_types(raw, expected):
    rec = ClaimRecord(**valid_kwargs(value=raw))
    assert isinstance(rec.value, Decimal)
    assert rec.value == expected


# --- money invariant (Q1) ----------------------------------------------

def test_float_money_is_rejected():
    with pytest.raises(ValidationError) as excinfo:
        ClaimRecord(**valid_kwargs(value=4060000000000.0))
    assert "float" in str(excinfo.value)


# --- immutability -------------------------------------------------------

def test_record_is_frozen():
    rec = ClaimRecord(**valid_kwargs())
    with pytest.raises(ValidationError):
        rec.value = Decimal("1")


# --- cross-field period invariant (Q3) ---------------------------------

def test_period_start_after_end_is_rejected():
    with pytest.raises(ValidationError) as excinfo:
        ClaimRecord(**valid_kwargs(period_start=date(2026, 3, 31)))  # end = 2025-12-31
    assert "period_start" in str(excinfo.value)


def test_period_start_on_or_before_end_ok():
    rec = ClaimRecord(**valid_kwargs(period_start=date(2025, 1, 1)))
    assert rec.period_start == date(2025, 1, 1)


# --- required / constrained fields (Q4) --------------------------------

@pytest.mark.parametrize(
    "field", ["concept", "unit", "fiscal_period", "form", "accession", "cik"]
)
def test_empty_string_fields_are_rejected(field):
    with pytest.raises(ValidationError):
        ClaimRecord(**valid_kwargs(**{field: ""}))


@pytest.mark.parametrize("year", [1899, 2201])
def test_fiscal_year_out_of_range_is_rejected(year):
    with pytest.raises(ValidationError):
        ClaimRecord(**valid_kwargs(fiscal_year=year))


# --- strict extras: typo protection (Q5) -------------------------------

def test_typo_reports_both_missing_and_extra():
    kw = valid_kwargs()
    kw.pop("accession")
    kw["acession"] = "0000019617-26-000123"  # misspelled
    with pytest.raises(ValidationError) as excinfo:
        ClaimRecord(**kw)
    error_types = {e["type"] for e in excinfo.value.errors()}
    assert "missing" in error_types          # real field absent
    assert "extra_forbidden" in error_types  # typo'd key rejected


# --- serialization boundary (Q6) ---------------------------------------

def test_json_emits_money_as_string():
    rec = ClaimRecord(**valid_kwargs())
    assert '"value":"4060000000000"' in rec.model_dump_json()  # string, not bare number


def test_python_dump_keeps_decimal():
    rec = ClaimRecord(**valid_kwargs())
    assert isinstance(rec.model_dump()["value"], Decimal)


def test_json_round_trip_is_lossless():
    rec = ClaimRecord(**valid_kwargs(value="0.30"))  # a value a float would corrupt
    restored = ClaimRecord.model_validate_json(rec.model_dump_json())
    assert restored == rec
    assert restored.value == Decimal("0.30")