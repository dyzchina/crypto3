"""
Phase 4 fact-check: figure captions and Table 1 gap numbers,
cross-referenced with rebuilt data.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
wide = pd.read_csv(ROOT / "data/processed/cex_por_snapshots_wide.csv")

print("=" * 70)
print("Fig 3 caption claims (BTC drift + pre/post-approval delta)")
print("=" * 70)
for v in ["binance","okx","bybit"]:
    sub = wide[wide.venue==v].sort_values("quarter")
    pre  = sub[sub.quarter < "2024-Q1"]["share_BTC"].mean()
    post = sub[sub.quarter >= "2024-Q1"]["share_BTC"].mean()
    delta_pp = (post - pre) * 100
    print(f"  {v:8s}: BTC pre={pre:.4f}  post={post:.4f}  Δ={delta_pp:+.1f}pp")
print("  → tex claims: Binance +9.6, OKX +9.7, Bybit +5.7  (compare above)")

print()
print("=" * 70)
print("Fig 1 caption facts")
print("=" * 70)
last_q = wide.quarter.max()
last = wide[wide.quarter==last_q].set_index("venue")
print(f"  Binance native share: {last.loc['binance','share_native_token']:.3f} (claim: > 0.1)")
print(f"  OKX native share:     {last.loc['okx','share_native_token']:.3f} (claim: near 0)")
print(f"  Bybit long-tail:      {last.loc['bybit','share_long_tail_alts']:.3f} (claim: highest, alt-heavy)")

print()
print("=" * 70)
print("§1 statement: '~$16 billion aggregate customer-liability shortfall'")
print("=" * 70)
gaps = [1.2, 1.3, 8.7, 1.3, 3.4]
print(f"  Table 1 gaps: Celsius 1.2 + Voyager 1.3 + FTX 8.7 + BlockFi 1.3 + Genesis 3.4 = {sum(gaps)}")
print(f"  Tex claim: 'approximately $16 billion' ✓" if abs(sum(gaps) - 16) < 0.5 else "  ✗")

print()
print("=" * 70)
print("§1 statement: 'roughly 8% of the on-chain reserves of the three largest surviving venues'")
print("=" * 70)
total = last["total_usd_billion"].sum()
ratio = sum(gaps) / total * 100
print(f"  15.9 / 209.4 = {ratio:.1f}%")
print(f"  Tex claim: 'roughly 8%' → {'✓' if 7 <= ratio <= 9 else '✗'}")

print()
print("=" * 70)
print("§1 statement: 'events separated by a median of 27 days'")
print("=" * 70)
from datetime import datetime
dates = ["2022-06-13", "2022-07-05", "2022-11-11", "2022-11-28", "2023-01-19"]
ds = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
gaps_d = [(ds[i+1] - ds[i]).days for i in range(len(ds)-1)]
median_gap = sorted(gaps_d)[len(gaps_d)//2]
print(f"  Consecutive gaps (days): {gaps_d}")
print(f"  Median: {median_gap} days")
print(f"  Tex claim: 'median of twenty-seven days' → {'✓' if abs(median_gap - 27) <= 3 else '✗ off by {abs(median_gap-27)} days'}")

print()
print("=" * 70)
print("Data time coverage")
print("=" * 70)
print(f"  Panel quarters: {sorted(wide.quarter.unique())}")
print(f"  Latest quarter: {last_q}")
