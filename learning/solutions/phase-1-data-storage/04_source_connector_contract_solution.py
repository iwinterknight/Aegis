"""Reference solution for Exercise 04 - the SourceConnector contract.

Only the two marked gaps differ from the exercise notebook.
Run:  python 04_source_connector_contract_solution.py   (needs `pip install faker`)
"""
import urllib.request, json, random
from decimal import Decimal
from dataclasses import dataclass, field
from faker import Faker

SEC_USER_AGENT = {"User-Agent": "Aegis Learning Project sunitsingh.bitsg@gmail.com"}


def _sec_pull(ticker, concept):
    def get(u):
        return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=SEC_USER_AGENT), timeout=60))
    tbl = get("https://www.sec.gov/files/company_tickers.json")
    cik = next(str(r["cik_str"]).zfill(10) for r in tbl.values() if r["ticker"].upper() == ticker.upper())
    facts = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    rec = max((e for e in facts["facts"]["us-gaap"][concept]["units"]["USD"] if e.get("form") == "10-K"),
              key=lambda e: e["end"])
    return facts["entityName"], cik, rec


def make_ledger(target_total, n, seed, account):
    rng = random.Random(seed); fake = Faker(); fake.seed_instance(seed)
    tc = int((target_total * 100).to_integral_value())
    w = [rng.random() for _ in range(n)]; s = sum(w)
    cents = [int(tc * x / s) for x in w]; cents[-1] += tc - sum(cents)
    return [{"txn_id": f"{account[:3].upper()}-{seed}-{i:05d}", "date": fake.date_between(start_date="-1y").isoformat(),
             "counterparty": fake.company(), "account": account, "amount": Decimal(cents[i]) / 100} for i in range(n)]


@dataclass
class IngestionResult:
    source: str
    kind: str
    entity: str
    records: list
    descriptor: dict
    provenance: dict = field(default_factory=dict)


class SourceConnector:
    source = None
    def pull(self, descriptor: dict) -> IngestionResult:
        raise NotImplementedError


CONNECTORS = {}
def register(cls):
    CONNECTORS[cls.source] = cls()
    return cls


def ingest(descriptor: dict) -> IngestionResult:
    # ---- gap 1: the dispatcher ----
    # One front door: route by the descriptor's declared source. The clear error matters - a typo'd
    # source should fail loudly with the list of valid options, not a cryptic KeyError.
    source = descriptor["source"]
    if source not in CONNECTORS:
        raise ValueError(f"no connector for source {source!r}; known: {sorted(CONNECTORS)}")
    return CONNECTORS[source].pull(descriptor)


@register
class SecXbrlConnector(SourceConnector):
    source = "sec-xbrl"
    def pull(self, d):
        try:
            entity, cik, rec = _sec_pull(d["ticker"], d["concept"])
        except Exception as e:
            print("  (offline, recorded JPM claim)", e)
            entity, cik, rec = "JPMORGAN CHASE & CO", "0000019617", {
                "val": 4062462000000, "end": "2025-12-31", "fy": 2025, "form": "10-K", "accn": "0001628280-26-008131"}
        claim = {"concept": d["concept"], "claimed_value": rec["val"], "period_end": rec["end"],
                 "provenance": {"form": rec["form"], "fy": rec.get("fy"), "accession": rec["accn"]}}
        return IngestionResult("sec-xbrl", "claim", entity, [claim], d, claim["provenance"])


@register
class SimulatedLedgerConnector(SourceConnector):
    source = "simulated-ledger"
    def pull(self, d):
        rows = make_ledger(Decimal(str(d["target_total"])), d["n"], d["seed"], d["account"])
        # ---- gap 2: return the canonical envelope ----
        # The seed in provenance is what makes the pull reproducible (FR-IN-5).
        return IngestionResult("simulated-ledger", "ledger", d["entity"], rows, d,
                               {"seed": d["seed"], "rows": len(rows)})


@register
class FfiecCallReportConnector(SourceConnector):
    source = "ffiec-callreport"
    def pull(self, d):
        claim = {"concept": d["concept"], "claimed_value": d["value"],
                 "provenance": {"source": "FFIEC", "rssd": d["rssd"]}}
        return IngestionResult("ffiec-callreport", "claim", d["entity"], [claim], d, claim["provenance"])


def reconcile(claim_res, ledger_res):
    claimed = Decimal(claim_res.records[0]["claimed_value"])
    total = sum((r["amount"] for r in ledger_res.records), Decimal("0"))
    delta = claimed - total
    return {"entity": claim_res.entity, "status": "MATCH" if delta == 0 else "DISCREPANCY",
            "claimed": claimed, "total": total, "delta": delta}


if __name__ == "__main__":
    r = ingest({"source": "simulated-ledger", "entity": "ACME", "target_total": "1000000.00",
                "n": 10, "seed": 1, "account": "operating_lease_liability"})
    assert r.kind == "ledger" and len(r.records) == 10 and r.provenance["seed"] == 1
    print("PASS - simulated-ledger envelope")

    claim_res = ingest({"source": "sec-xbrl", "ticker": "JPM", "concept": "Liabilities"})
    claimed = Decimal(claim_res.records[0]["claimed_value"])
    ledger_res = ingest({"source": "simulated-ledger", "entity": claim_res.entity,
                         "target_total": str(claimed - Decimal("125000000.00")),
                         "n": 500, "seed": 7, "account": "operating_lease_liability"})
    f = reconcile(claim_res, ledger_res)
    assert f["status"] == "DISCREPANCY" and f["delta"] == Decimal("125000000.00")
    print(f"PASS - SG-1 through the contract: [{f['status']}] delta ${f['delta']:,}")

    cr = ingest({"source": "ffiec-callreport", "entity": "SOME BANK", "rssd": 480228,
                 "concept": "TotalDeposits", "value": 123456000000})
    assert cr.kind == "claim" and cr.records[0]["claimed_value"] == 123456000000
    print("PASS - new source added in ~6 lines, same ingest():", list(CONNECTORS))

    d = {"source": "simulated-ledger", "entity": "ACME", "target_total": "500000.00",
         "n": 100, "seed": 2025, "account": "operating_lease_liability"}
    assert [x["amount"] for x in ingest(d).records] == [x["amount"] for x in ingest(d).records]
    print("PASS - reproducible from descriptor")

    try:
        ingest({"source": "typo-source"})
    except ValueError as e:
        print("PASS - unknown source fails loudly:", e)
