import pandas as pd
from pathlib import Path
CX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
df = pd.read_csv(CX / "data/processed/cex_por_snapshots_wide.csv")

print("=== Fig 1 heatmap 最新季度 share ===")
last = df[df.quarter == df.quarter.max()].set_index("venue")
cols = ["share_BTC","share_ETH","share_USDT_USDC","share_native_token","share_long_tail_alts"]
print(last[cols].round(3))
print()
print("=== Fig 1 caption 事实核查 ===")
print(f"  Binance native > 0.1?           {last.loc['binance','share_native_token']:.3f}   {'✓' if last.loc['binance','share_native_token'] > 0.1 else '✗'}")
print(f"  OKX native on-chain near 0?     {last.loc['okx','share_native_token']:.3f}   {'✓' if last.loc['okx','share_native_token'] < 0.02 else '✗'}")
print(f"  Bybit long-tail alt-heavy?      {last.loc['bybit','share_long_tail_alts']:.3f}   {'✓' if last.loc['bybit','share_long_tail_alts'] > 0.25 else '✗'}")
print()

print("=== Fig 3 caption: BTC share drifts up after spot-BTC ETF approval ===")
for v in ["binance","okx","bybit"]:
    sub = df[df.venue==v].sort_values("quarter")
    pre  = sub[sub.quarter < "2024-Q1"]["share_BTC"].mean()
    post = sub[sub.quarter >= "2024-Q1"]["share_BTC"].mean()
    print(f"  {v:8s}  BTC pre-ETF={pre:.3f}  post-ETF={post:.3f}  Δ={post-pre:+.3f}   {'✓' if post > pre else '✗'}")
print()

print("=== Fig 3 caption: USD-anchored share nearly parallel across venues ===")
for q in ["2023-Q4","2024-Q2","2025-Q1","2025-Q4"]:
    row = df[df.quarter==q].set_index("venue")["share_USDT_USDC"]
    print(f"  {q}  binance={row.get('binance',0):.3f}  okx={row.get('okx',0):.3f}  bybit={row.get('bybit',0):.3f}")
print()

print("=== Fig 3 caption: Binance native (BNB) persistent departure ===")
for q in ["2022-Q4","2023-Q4","2024-Q4","2025-Q4"]:
    row = df[df.quarter==q].set_index("venue")["share_native_token"]
    print(f"  {q}  binance={row.get('binance',0):.3f}  okx={row.get('okx',0):.3f}  bybit={row.get('bybit',0):.3f}")
