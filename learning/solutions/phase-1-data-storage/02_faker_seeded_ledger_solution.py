"""Reference solution for Exercise 02 - anchored synthetic ledger + reconciliation (SG-1).

Only the two marked gaps differ from the exercise notebook.
Run:  python 02_faker_seeded_ledger_solution.py   (needs `pip install faker`)
"""
import urllib.request, json, random
from decimal import Decimal
from faker import Faker

SEC_USER_AGENT = {"User-Agent": "Aegis Learning Project sunitsingh.bitsg@gmail.com"}


def _pull_claim_live(ticker, concept="Liabilities"):
    def get(u):
        return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=SEC_USER_AGENT), timeout=60))
    tbl = get("https://www.sec.gov/files/company_tickers.json")
    cik = next(str(r["cik_str"]).zfill(10) for r in tbl.values() if r["ticker"].upper() == ticker.upper())
    facts = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    rec = max((e for e in facts["facts"]["us-gaap"][concept]["units"]["USD"] if e.get("form") == "10-K"),
              key=lambda e: e["end"])
    return {"entity": facts["entityName"], "cik": cik, "concept": concept,
            "claimed_value": rec["val"], "period_end": rec["end"],
            "provenance": {"form": rec["form"], "fy": rec.get("fy"), "accession": rec["accn"]}}


def make_ledger(target_total: Decimal, n: int, seed: int, account="operating_lease_liability") -> list:
    rng = random.Random(seed)
    fake = Faker(); fake.seed_instance(seed)
    target_cents = int((target_total * 100).to_integral_value())
    weights = [rng.random() for _ in range(n)]
    wsum = sum(weights)
    cents = [int(target_cents * w / wsum) for w in weights]
    # ---- gap 1: remainder fix-up ----
    # Integer rounding above drops a few cents; push the leftover onto the last row so the
    # ledger sums to target_cents EXACTLY. Working in ints means zero floating drift.
    cents[-1] += target_cents - sum(cents)
    rows = []
    for i in range(n):
        rows.append({
            "txn_id": f"L-{seed}-{i:05d}",
            "date": fake.date_between(start_date="-1y").isoformat(),
            "counterparty": fake.company(),
            "account": account,
            "amount": Decimal(cents[i]) / 100,
        })
    return rows


def ledger_total(rows) -> Decimal:
    return sum((r["amount"] for r in rows), Decimal("0"))


def reconcile(claim_record: dict, ledger: list) -> dict:
    claimed = Decimal(claim_record["claimed_value"])
    # ---- gap 2: the audit diff ----
    # Decimal arithmetic is exact, so a clean book gives delta == 0 with no tolerance fudge.
    total = ledger_total(ledger)
    delta = claimed - total
    status = "MATCH" if delta == 0 else "DISCREPANCY"
    return {
        "entity": claim_record["entity"], "concept": claim_record["concept"],
        "claimed_value": claimed, "ledger_total": total, "delta": delta, "status": status,
        "claim_provenance": claim_record["provenance"], "evidence_rows": len(ledger),
    }


if __name__ == "__main__":
    try:
        claim = _pull_claim_live("JPM")
    except Exception as e:
        print("offline, using recorded claim:", e)
        claim = {"entity": "JPMORGAN CHASE & CO", "cik": "0000019617", "concept": "Liabilities",
                 "claimed_value": 4062462000000, "period_end": "2025-12-31",
                 "provenance": {"form": "10-K", "fy": 2025, "accession": "0001628280-26-008131"}}
    CLAIMED = Decimal(claim["claimed_value"])

    clean = make_ledger(CLAIMED, 500, seed=42)
    assert ledger_total(clean) == CLAIMED
    assert [r["amount"] for r in clean] == [r["amount"] for r in make_ledger(CLAIMED, 500, seed=42)]
    print("PASS - clean ledger sums to exactly", f"${ledger_total(clean):,}", "and is reproducible")

    delta = Decimal("125000000.00")
    disc = make_ledger(CLAIMED - delta, 500, seed=7)
    cf, df = reconcile(claim, clean), reconcile(claim, disc)
    assert cf["status"] == "MATCH" and cf["delta"] == 0
    assert df["status"] == "DISCREPANCY" and df["delta"] == delta
    print("PASS - clean -> MATCH; discrepant -> DISCREPANCY, delta", f"${df['delta']:,}")
    pct = df["delta"] / df["claimed_value"] * 100
    print(f"FINDING [{df['status']}] {df['entity']}/{df['concept']}: "
          f"claim ${df['claimed_value']:,} vs ledger ${df['ledger_total']:,} "
          f"-> delta ${df['delta']:,} ({pct:.4f}%)")
