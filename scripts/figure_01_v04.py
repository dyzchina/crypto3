"""figure_01_v04.py -- Fig 1 rebuilt from real DefiLlama on-chain PoR data.

Uses data/processed/cex_por_snapshots_wide.csv (latest quarter per venue).
Coinbase + Kraken -> N/A hatch (DefiLlama does not index their wallets;
Step-2b will pull from SEC 10-Q / Kraken audit PDFs).
"""
import os, csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root
CSV_PATH = BASE / "data" / "processed" / "cex_por_snapshots_wide.csv"
OUT = BASE / "manuscript" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# --- Read CSV, take the latest quarter per venue for the snapshot figure ---
with CSV_PATH.open(encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
latest_per_venue = {}
for r in rows:
    v = r["venue"]
    latest_per_venue[v] = r  # last write wins (rows are sorted)

# Canonical 5-venue order for the paper
venues_row = ["Binance", "Coinbase", "Kraken", "OKX", "Bybit"]
venue_key  = {"Binance": "binance", "Coinbase": None, "Kraken": None,
              "OKX": "okx",       "Bybit":    "bybit"}
assets = ["BTC", "ETH", "USDT+USDC", "Native token\n(BNB/OKB/etc.)", "Long-tail alts"]
asset_keys = ["share_BTC", "share_ETH", "share_USDT_USDC",
              "share_native_token", "share_long_tail_alts"]

data = np.full((len(venues_row), len(assets)), np.nan)
snapshot_dates = {}
totals = {}
for i, vname in enumerate(venues_row):
    k = venue_key[vname]
    if k is None:
        continue
    r = latest_per_venue.get(k)
    if r is None:
        continue
    for j, ak in enumerate(asset_keys):
        data[i, j] = float(r[ak])
    snapshot_dates[vname] = r["snapshot_date"]
    totals[vname] = float(r["total_usd_billion"])

# --- Plot ---
fig, ax = plt.subplots(figsize=(7.6, 4.4))
masked = np.ma.masked_invalid(data)
cmap = plt.get_cmap("viridis").copy()
cmap.set_bad(color="lightgray")
im = ax.imshow(masked, cmap=cmap, aspect="auto", vmin=0, vmax=0.45)

ax.set_xticks(range(len(assets)))
ax.set_xticklabels(assets, fontsize=9)
ax.set_yticks(range(len(venues_row)))
# Row labels include snapshot date + total
ylabels = []
for v in venues_row:
    if v in snapshot_dates:
        ylabels.append(f"{v}\n{snapshot_dates[v]}\n\\${totals[v]:.0f}B on-chain")
    else:
        ylabels.append(f"{v}\n(N/A)\nsee App E")
ax.set_yticklabels(ylabels, fontsize=8)

# Cell values + N/A hatching for masked rows
for i in range(len(venues_row)):
    for j in range(len(assets)):
        v = data[i, j]
        if np.isnan(v):
            ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1,
                                   fill=False, hatch="//", edgecolor="dimgray",
                                   linewidth=0.4))
            if j == len(assets) // 2:
                ax.text(j, i, "N/A", ha="center", va="center",
                        color="dimgray", fontsize=8, fontweight="bold")
        else:
            color = "white" if v < 0.22 else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    color=color, fontsize=9)

cbar = plt.colorbar(im, ax=ax, fraction=0.036, pad=0.03)
cbar.set_label("Reserve share (row sum = 1)", fontsize=9)
ax.set_title(
    "Figure 1. Reserve-simplex snapshot across five CEX venues, 2025-Q4\n"
    "(on-chain shares from DefiLlama; hatched rows lack indexed wallets, see Appendix~E)",
    fontsize=9.5, pad=8)
plt.tight_layout()
p1 = OUT / "fig1_reserve_heatmap.pdf"
plt.savefig(p1, bbox_inches="tight")
plt.close()
print(f"[OK] {p1}")

# --- Fig 3 (NEW): time-series of BTC/ETH/USD shares for the 3 indexed venues ---
# Reload full CSV and pivot
with CSV_PATH.open(encoding="utf-8") as f:
    all_rows = list(csv.DictReader(f))

import datetime as dt
def parse_q(qkey):
    y, q = qkey.split("-Q")
    return dt.date(int(y), {1:3,2:6,3:9,4:12}[int(q)], 15)

fig, axes = plt.subplots(1, 3, figsize=(11, 3.5), sharey=True)
colours = {"share_BTC": "#1f77b4", "share_ETH": "#2ca02c",
           "share_USDT_USDC": "#d62728", "share_native_token": "#9467bd",
           "share_long_tail_alts": "#8c564b"}
labels_map = {"share_BTC": "BTC", "share_ETH": "ETH",
              "share_USDT_USDC": "USDT+USDC", "share_native_token": "Native",
              "share_long_tail_alts": "Long-tail"}
for ax, vk, title in zip(axes, ["binance", "okx", "bybit"],
                          ["Binance", "OKX", "Bybit"]):
    vr = [r for r in all_rows if r["venue"] == vk]
    vr.sort(key=lambda r: r["quarter"])
    xs = [parse_q(r["quarter"]) for r in vr]
    for k in asset_keys:
        ys = [float(r[k]) for r in vr]
        ax.plot(xs, ys, marker="o", ms=3, lw=1.4,
                color=colours[k], label=labels_map[k])
    ax.set_title(title, fontsize=10)
    ax.set_ylim(0, 0.65)
    ax.grid(alpha=0.3)
    ax.tick_params(axis="x", labelsize=7, rotation=30)
    if ax is axes[0]:
        ax.set_ylabel("Reserve share", fontsize=9)
axes[-1].legend(loc="upper right", fontsize=7, framealpha=0.9)
fig.suptitle("Reserve-share trajectories 2022-Q4 to 2025-Q4 "
             "(on-chain composition, DefiLlama)", fontsize=10.5, y=1.02)
plt.tight_layout()
p3 = OUT / "fig3_share_trajectories.pdf"
plt.savefig(p3, bbox_inches="tight")
plt.close()
print(f"[OK] {p3}")

print("done.")
