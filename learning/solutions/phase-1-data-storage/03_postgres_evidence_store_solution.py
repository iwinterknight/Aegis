"""Reference solution for Exercise 03 - database evidence store + parameterized SQL reconciliation.

Only the two marked gaps differ from the exercise notebook.
Run:  python 03_postgres_evidence_store_solution.py   (needs `pip install faker`)
"""
import sqlite3, random, urllib.request, json
from decimal import Decimal
from faker import Faker

SEC_USER_AGENT = {"User-Agent": "Aegis Learning Project sunitsingh.bitsg@gmail.com"}


def _pull_claim(ticker="JPM", concept="Liabilities"):
    try:
        def get(u):
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=SEC_USER_AGENT), timeout=60))
        tbl = get("https://www.sec.gov/files/company_tickers.json")
        cik = next(str(r["cik_str"]).zfill(10) for r in tbl.values() if r["ticker"].upper() == ticker.upper())
        facts = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
        rec = max((e for e in facts["facts"]["us-gaap"][concept]["units"]["USD"] if e.get("form") == "10-K"),
                  key=lambda e: e["end"])
        return {"entity": facts["entityName"], "concept": concept, "claimed_value": rec["val"],
                "provenance": {"form": rec["form"], "fy": rec.get("fy"), "accession": rec["accn"]}}
    except Exception as e:
        print("offline, recorded claim:", e)
        return {"entity": "JPMORGAN CHASE & CO", "concept": "Liabilities", "claimed_value": 4062462000000,
                "provenance": {"form": "10-K", "fy": 2025, "accession": "0001628280-26-008131"}}


def make_ledger(target_total, n, seed, account):
    rng = random.Random(seed); fake = Faker(); fake.seed_instance(seed)
    tc = int((target_total * 100).to_integral_value())
    w = [rng.random() for _ in range(n)]; s = sum(w)
    cents = [int(tc * x / s) for x in w]; cents[-1] += tc - sum(cents)
    return [{"txn_id": f"{account[:3].upper()}-{seed}-{i:05d}", "date": fake.date_between(start_date="-1y").isoformat(),
             "counterparty": fake.company(), "account": account, "amount": Decimal(cents[i]) / 100} for i in range(n)]


def to_cents(amount: Decimal) -> int:
    return int((amount * 100).to_integral_value())


def load_ledger(conn, rows):
    params = [(r["txn_id"], r["date"], r["counterparty"], r["account"], to_cents(r["amount"])) for r in rows]
    # ---- gap 1: parameterized bulk insert ----
    # executemany binds each tuple to the five ? placeholders. The data never touches the SQL text,
    # so values like O'Brien & Co (an apostrophe) or an injection string can't break or hijack it.
    conn.executemany(
        "INSERT INTO ledger (txn_id, txn_date, counterparty, account, amount_cents) VALUES (?, ?, ?, ?, ?)",
        params,
    )
    conn.commit()


def ledger_sum(conn, account: str) -> Decimal:
    # ---- gap 2: parameterized reconciliation query ----
    # The account is BOUND (the ,(account,) tuple), not formatted in. In Postgres the placeholder is %s.
    row = conn.execute("SELECT SUM(amount_cents) FROM ledger WHERE account = ?", (account,)).fetchone()
    cents = row[0] or 0           # SUM over zero matching rows returns NULL -> treat as 0
    return Decimal(cents) / 100


def unsafe_sum(conn, account):
    sql = f"SELECT SUM(amount_cents) FROM ledger WHERE account = '{account}'"   # NEVER do this
    return Decimal(conn.execute(sql).fetchone()[0] or 0) / 100


def reconcile_via_sql(conn, claim, account="operating_lease_liability"):
    claimed = Decimal(claim["claimed_value"])
    total = ledger_sum(conn, account)
    delta = claimed - total
    return {"status": "MATCH" if delta == 0 else "DISCREPANCY", "claimed": claimed, "total": total, "delta": delta}


if __name__ == "__main__":
    claim = _pull_claim()
    CLAIMED = Decimal(claim["claimed_value"])
    all_rows = (make_ledger(CLAIMED, 500, 42, "operating_lease_liability")
                + make_ledger(Decimal("88000000.00"), 50, 99, "accounts_payable"))

    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE ledger (txn_id TEXT PRIMARY KEY, txn_date TEXT, counterparty TEXT, "
                 "account TEXT, amount_cents INTEGER NOT NULL)")
    load_ledger(conn, all_rows)
    assert conn.execute("SELECT COUNT(*) FROM ledger").fetchone()[0] == 550
    print("PASS - loaded 550 rows")

    assert ledger_sum(conn, "operating_lease_liability") == CLAIMED
    assert ledger_sum(conn, "no_such_account") == Decimal("0")
    print("PASS - lease sums to exactly", f"${ledger_sum(conn, 'operating_lease_liability'):,}")

    mal = "x' OR '1'='1"
    full = ledger_sum(conn, "operating_lease_liability") + ledger_sum(conn, "accounts_payable")
    print(f"injection: unsafe leaks ${unsafe_sum(conn, mal):,} (full ${full:,}); safe returns ${ledger_sum(conn, mal):,}")
    assert unsafe_sum(conn, mal) == full and ledger_sum(conn, mal) == Decimal("0")
    print("PASS - parameterization neutralizes the injection")

    conn2 = sqlite3.connect(":memory:")
    conn2.execute("CREATE TABLE ledger (txn_id TEXT PRIMARY KEY, txn_date TEXT, counterparty TEXT, account TEXT, amount_cents INTEGER)")
    load_ledger(conn2, make_ledger(CLAIMED - Decimal("125000000.00"), 500, 7, "operating_lease_liability"))
    f = reconcile_via_sql(conn2, claim)
    assert f["status"] == "DISCREPANCY" and f["delta"] == Decimal("125000000.00")
    print("PASS - dirty DB ->", f["status"], "delta", f"${f['delta']:,}")
