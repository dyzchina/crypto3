"""pull_defillama_cex.py -- fetch Binance/OKX/Bybit on-chain composition from DefiLlama.

DefiLlama's /protocol/{slug} endpoint provides per-day, per-token USD value
across 20-30+ chains for indexed CEXs. This gives us the on-chain-visible
reserve composition -- a rigorous proxy for the venue's asset-class mix.

Coinbase + Kraken need separate pullers (SEC 10-Q / audit PDF).
"""
from __future__ import annotations
import sys, json, time, datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (detect_windows_proxy, retry, QUARTERS,
                     save_json, ASSET_CLASSES, classify)

detect_windows_proxy()

import requests

BASE = Path(__file__).resolve().parent.parent / r"data/raw_por"  # cex_contagion_v2.0 root

VENUES = {
    "binance": "Binance-CEX",
    "okx":     "okx",
    "bybit":   "Bybit",
}

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

def fetch(url):
    def do():
        r = requests.get(url, headers=HEADERS, timeout=45)
        r.raise_for_status()
        return r.json()
    return retry(do, n=3, delay=5)

def main():
    for venue, slug in VENUES.items():
        out_dir = BASE / venue
        out_dir.mkdir(parents=True, exist_ok=True)
        url = f"https://api.llama.fi/protocol/{slug}"
        try:
            print(f"[fetch] {venue} <- {url}", flush=True)
            data = fetch(url)
            # Save full raw
            raw_path = out_dir / f"_{venue}_raw.json"
            save_json(raw_path, data)
            size_mb = raw_path.stat().st_size / 1024 / 1024
            print(f"  [ok] raw {size_mb:.1f} MB")

            # tokens is list of {date: int (unix ts), tokens: {SYM: qty}}
            tokens_ts = data.get("tokens", [])
            print(f"  [ok] {len(tokens_ts)} daily snapshots")
            if not tokens_ts:
                continue

            # Also tokensInUsd (already in USD -- best for aggregation)
            tokens_usd = data.get("tokensInUsd", [])
            print(f"  [ok] {len(tokens_usd)} tokensInUsd snapshots")

            # For each canonical quarter-end, pick the closest snapshot
            per_quarter = {}
            for y, q, qend in QUARTERS:
                qend_ts = int(dt.datetime(qend.year, qend.month, qend.day).timestamp())
                # find closest in tokens_usd
                if tokens_usd:
                    closest = min(tokens_usd,
                                  key=lambda s: abs(s.get("date", 0) - qend_ts))
                    snap_date = dt.date.fromtimestamp(closest["date"])
                    per_quarter[f"{y}-Q{q}"] = {
                        "canonical_qend": qend.isoformat(),
                        "actual_snapshot_date": snap_date.isoformat(),
                        "days_off": abs((snap_date - qend).days),
                        "tokens_usd": closest.get("tokens", {}),
                    }
            save_json(out_dir / f"{venue}_quarterly.json", per_quarter)
            print(f"  [ok] {len(per_quarter)} quarterly snapshots written")
        except Exception as e:
            print(f"  [fail] {venue}: {e}", file=sys.stderr)
            save_json(out_dir / f"_FAILED_{venue}.json", {"error": str(e), "url": url})

if __name__ == "__main__":
    main()
