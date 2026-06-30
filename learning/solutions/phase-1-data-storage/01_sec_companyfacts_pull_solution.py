"""Reference solution for Exercise 01 - SEC companyfacts pull.

Only the two marked gaps differ from the exercise notebook. Read *why*, don't just copy.
Run:  python 01_sec_companyfacts_pull_solution.py
"""
import urllib.request, json

SEC_USER_AGENT = {"User-Agent": "Aegis Learning Project sunitsingh.bitsg@gmail.com"}


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=SEC_USER_AGENT)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def resolve_cik(ticker: str) -> str:
    table = _get_json("https://www.sec.gov/files/company_tickers.json")
    # ---- gap 1 ----
    # The table values are {cik_str, ticker, title}. Match case-insensitively, then pad.
    # str.zfill(10) left-pads with zeros: 19617 -> "0000019617". The SEC's companyfacts
    # URL is strict about the 10-digit form, so the padding is not optional.
    t = ticker.upper()
    for row in table.values():
        if row["ticker"].upper() == t:
            return str(row["cik_str"]).zfill(10)
    raise ValueError(f"ticker {ticker!r} not found in SEC company_tickers.json")


def get_company_facts(cik: str) -> dict:
    return _get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")


def latest_annual_value(facts: dict, concept: str, taxonomy: str = "us-gaap") -> dict:
    entries = facts["facts"][taxonomy][concept]["units"]["USD"]
    # ---- gap 2 ----
    # Keep annual (10-K) reports only, then take the one with the latest period-end.
    # ISO dates ("2025-12-31") sort lexicographically, so plain max on the string works -
    # no date parsing needed. We could also break ties on 'filed', but 'end' is enough here.
    annual = [e for e in entries if e.get("form") == "10-K"]
    if not annual:
        raise ValueError(f"no 10-K entries for {concept}")
    rec = max(annual, key=lambda e: e["end"])
    return {
        "value": rec["val"],
        "end": rec["end"],
        "fy": rec.get("fy"),
        "form": rec["form"],
        "accn": rec["accn"],
    }


def pull_claim(ticker: str, concept: str) -> dict:
    cik = resolve_cik(ticker)
    facts = get_company_facts(cik)
    rec = latest_annual_value(facts, concept)
    return {
        "source": "sec-xbrl",
        "entity": facts["entityName"],
        "cik": cik,
        "concept": concept,
        "claimed_value": rec["value"],
        "unit": "USD",
        "period_end": rec["end"],
        "provenance": {"form": rec["form"], "fy": rec["fy"], "accession": rec["accn"]},
    }


if __name__ == "__main__":
    cik = resolve_cik("JPM")
    assert cik == "0000019617", cik
    assert resolve_cik("jpm") == "0000019617"
    print("PASS - JPM ->", cik)

    facts = get_company_facts(cik)
    claim = latest_annual_value(facts, "Liabilities")
    assert claim["form"] == "10-K"
    assert isinstance(claim["value"], int) and claim["value"] > 1_000_000_000_000
    print(f"PASS - Liabilities ${claim['value']:,} as of {claim['end']} (accn {claim['accn']})")

    print(json.dumps(pull_claim("JPM", "Liabilities"), indent=2))
