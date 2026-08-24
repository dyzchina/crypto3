"""aggregate_por.py -- combine quarterly PoR snapshots into 5-asset-class simplex CSV.

Reads data/raw_por/{venue}/{venue}_quarterly.json for each venue,
aggregates each snapshot's token-USD dict into the 5 asset classes,
row-normalises, and writes:
- data/processed/cex_por_snapshots.csv  (long form, one row per venue-quarter-class)
- data/processed/cex_por_snapshots_wide.csv  (wide form for direct heatmap use)
"""
from __future__ import annotations
import sys, json, csv
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from _common import ASSET_CLASSES, classify, QUARTERS

BASE = Path(__file__).resolve().parent.parent / r"data"  # cex_contagion_v2.0 root
PROCESSED = BASE / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

VENUES = ["binance", "okx", "bybit"]

def aggregate_one(venue, tokens_usd):
    """tokens_usd: dict SYM -> USD value on snapshot day."""
    bucket = defaultdict(float)
    total = 0.0
    for sym, usd in tokens_usd.items():
        cls = classify(sym, venue)
        bucket[cls] += float(usd)
        total += float(usd)
    if total <= 0:
        return {k: 0.0 for k in ASSET_CLASSES}, 0.0
    return {k: bucket[k] / total for k in ASSET_CLASSES}, total

def main():
    rows_long = []
    rows_wide = []
    for venue in VENUES:
        qfile = BASE / "raw_por" / venue / f"{venue}_quarterly.json"
        if not qfile.exists():
            print(f"[skip] no data for {venue}: {qfile}", file=sys.stderr)
            continue
        quarterly = json.loads(qfile.read_text(encoding="utf-8"))
        for qkey in sorted(quarterly.keys()):
            snap = quarterly[qkey]
            shares, total_usd = aggregate_one(venue, snap["tokens_usd"])
            row_w = {
                "venue": venue,
                "quarter": qkey,
                "snapshot_date": snap["actual_snapshot_date"],
                "days_off_qend": snap["days_off"],
                "total_usd_billion": round(total_usd / 1e9, 3),
                **{f"share_{k}": round(shares[k], 4) for k in ASSET_CLASSES},
            }
            rows_wide.append(row_w)
            for k in ASSET_CLASSES:
                rows_long.append({
                    "venue": venue,
                    "quarter": qkey,
                    "snapshot_date": snap["actual_snapshot_date"],
                    "asset_class": k,
                    "share": round(shares[k], 4),
                    "total_usd_billion": round(total_usd / 1e9, 3),
                })
    # Write long
    with (PROCESSED / "cex_por_snapshots.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows_long[0].keys())
        w.writeheader()
        w.writerows(rows_long)
    # Write wide
    with (PROCESSED / "cex_por_snapshots_wide.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows_wide[0].keys())
        w.writeheader()
        w.writerows(rows_wide)
    print(f"[ok] {len(rows_long)} long rows, {len(rows_wide)} wide rows")
    print(f"[ok] {PROCESSED / 'cex_por_snapshots.csv'}")
    print(f"[ok] {PROCESSED / 'cex_por_snapshots_wide.csv'}")

    # Print a quick sanity table
    print("\n=== Sanity: latest snapshot per venue ===")
    for venue in VENUES:
        latest = [r for r in rows_wide if r["venue"] == venue][-1]
        print(f"{venue:10s} {latest['snapshot_date']}  total=${latest['total_usd_billion']:.1f}B  "
              f"BTC={latest['share_BTC']:.2f} ETH={latest['share_ETH']:.2f} "
              f"USD={latest['share_USDT_USDC']:.2f} native={latest['share_native_token']:.2f} "
              f"alt={latest['share_long_tail_alts']:.2f}")

if __name__ == "__main__":
    main()
