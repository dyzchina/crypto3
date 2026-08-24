"""
Coinbase 10-Q metadata-only puller.

REMOVED in v2.0-f: the placeholder asset-class share table has been
deleted per data-charter red line ("no fabricated data"). This script
now only fetches EDGAR filing metadata (index of accession numbers and
primary-document URLs) for downstream manual extraction.

Downstream steps that require Coinbase quarterly asset-class shares
must parse the primary 10-Q iXBRL exhibit (Note 5, Customer Custodial
Funds) directly and combine with Coinbase's quarterly shareholder
letters. That parse is deferred to the companion release; the main
manuscript is 3-venue only.
"""
from pathlib import Path
import json
import urllib.request
import os

os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7890")
os.environ.setdefault("HTTP_PROXY",  "http://127.0.0.1:7890")

UA = "ICBC-Research gouhongjun_bs@cq.icbc.com.cn"

def http_get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Encoding": "identity",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

CIK_COIN = "0001679788"

def list_10q(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    j = json.loads(http_get(url))
    r = j["filings"]["recent"]
    keys = ["accessionNumber", "form", "filingDate", "reportDate", "primaryDocument"]
    return [{k: r[k][i] for k in keys}
            for i, form in enumerate(r["form"]) if form == "10-Q"]

ROOT = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
OUT = ROOT / "data/raw_por/coinbase/edgar_10q_index.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

try:
    filings = list_10q(CIK_COIN)
    OUT.write_text(json.dumps(filings, indent=2), encoding="utf-8")
    print(f"[ok] {len(filings)} 10-Q filings")
    print(f"[write] {OUT}")
    print()
    print("Primary-document URLs (deferred to companion release for extraction):")
    for f in filings[:10]:
        acc = f["accessionNumber"].replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{int(CIK_COIN)}/{acc}/{f['primaryDocument']}"
        print(f"  {f['reportDate']}  {url}")
except Exception as e:
    print(f"[error] EDGAR unreachable: {e}")
