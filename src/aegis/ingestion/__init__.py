"""Ingestion: the boundary that turns untrusted external data into trusted,
validated Aegis records. See docs/adr/0002-pydantic-v2-ingestion-contract.md."""

from .models import ClaimRecord

__all__ = ["ClaimRecord"]