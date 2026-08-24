"""estimator_nk.py -- empirical k-fold intersection counts on the three-venue panel.

Design (matches Algorithm 1 of the paper, adapted to the 3-venue snapshot data):

1. Load quarterly share panels for Binance / OKX / Bybit (5 asset classes each,
   row-normalised) from data/processed/cex_por_snapshots_wide.csv.

2. Define venue-e distress cell D_e as a threshold-neighbourhood in the
   (r, q, phi) triple. For the paper's Data-Charter-compliant configuration
   with only public on-chain shares, we use:
     - r_e   := log(BTC + ETH + USDT+USDC share)  -- log "safe-asset" share
     - q_e   := native_token share
     - phi_e := long_tail_alts share
   and mark venue e in distress at time t if EITHER
     (a) r_e(t) < r_e_bar - c * sigma(r_e)   (safe-asset flight)
     (b) q_e(t) > q_e_ceil                    (native concentration spike)
     (c) phi_e(t) > phi_e_ceil                (long-tail bloat)
   Any of {a,b,c} triggers -- so D_e is a union of three half-spaces.

3. For each candidate k in {1,2,3} and each quarter t, form
     N_k(t) = sum over |S|=k of prod_{e in S} 1{ e in D_e at t }.
   This is the finite-sample intersection count.

4. Compare with the T1 polylog prior at H=1 (constant), giving a
   dimension-agreement diagnostic:
     R_k(t) := hat N_k(t) / [ c_{k,eps} * (log T)^{alpha(k,n,m)} ]
   with alpha(k,n,m) = k - 1 + m*(n-k)/d, d = n*(m-1), n=3 venues,
   m=5 asset classes, and c_{k,eps} normalised so R_k(pre-June-2022)=1.

Since the panel starts 2022-Q4 (i.e. no pre-June-2022 window on-chain),
we normalise instead by the 2022-Q4 quarter itself (first quarter available),
following the convention documented in Appendix E.

Outputs:
  - manuscript/figures/fig4_empirical_frontier.pdf
  - data/processed/nk_estimates.csv
"""
from __future__ import annotations
import csv, math, sys
from pathlib import Path
from itertools import combinations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime as dt

BASE = Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root
CSV_IN = BASE / "data" / "processed" / "cex_por_snapshots_wide.csv"
# NOTE: Fig 4 rendering is delegated to fig4_v2_dual_threshold.py (v2.0
# dual-threshold 2x3 panel). The legacy single-threshold 1x3 plot below
# is retained for archival diagnostics but written to a *_legacy.pdf
# so it does not clobber the canonical manuscript figure.
OUT_FIG = BASE / "manuscript" / "figures" / "fig4_empirical_frontier_legacy.pdf"
OUT_CSV = BASE / "data" / "processed" / "nk_estimates.csv"

VENUES = ["binance", "okx", "bybit"]  # n=3
N = len(VENUES)
M = 5  # asset classes

# ---------- Load panel ----------
rows_by_venue_quarter = {}
with CSV_IN.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows_by_venue_quarter[(r["venue"], r["quarter"])] = r

quarters = sorted({q for (_, q) in rows_by_venue_quarter.keys()})
print(f"[panel] {len(VENUES)} venues x {len(quarters)} quarters = "
      f"{len(VENUES)*len(quarters)} snapshots")

# ---------- Build (r, q, phi) triple + distress signal ----------
def to_triple(row):
    """row is a wide-CSV dict; return (r, q, phi)."""
    safe = float(row["share_BTC"]) + float(row["share_ETH"]) + float(row["share_USDT_USDC"])
    native = float(row["share_native_token"])
    tail = float(row["share_long_tail_alts"])
    # r = log(safe) with a floor to avoid log(0)
    r = math.log(max(safe, 1e-6))
    return r, native, tail

triples = {}  # (venue, quarter) -> (r, q, phi)
for (v, q), row in rows_by_venue_quarter.items():
    triples[(v, q)] = to_triple(row)

# per-venue robust stats for thresholds
per_venue_series = {v: [] for v in VENUES}
for (v, q), t in triples.items():
    per_venue_series[v].append((q, t))
for v in VENUES:
    per_venue_series[v].sort(key=lambda x: x[0])

# thresholds: c=1.0 std for safe-asset flight; native q>q_ceil where
# q_ceil = venue's own 75th percentile; long-tail similarly
def median_iqr(xs):
    a = np.array(xs)
    return float(np.median(a)), float(np.quantile(a, 0.75) - np.quantile(a, 0.25))

thresh = {}
for v in VENUES:
    rs   = [t[0] for (_, t) in per_venue_series[v]]
    qs   = [t[1] for (_, t) in per_venue_series[v]]
    phis = [t[2] for (_, t) in per_venue_series[v]]
    r_med, r_iqr = median_iqr(rs)
    q_p75 = float(np.quantile(np.array(qs), 0.75))
    phi_p75 = float(np.quantile(np.array(phis), 0.75))
    thresh[v] = {"r_bar": r_med, "r_iqr": r_iqr,
                 "q_ceil": q_p75, "phi_ceil": phi_p75}
    print(f"  {v}: r_bar={r_med:+.3f}  r_iqr={r_iqr:.3f}  "
          f"q_ceil={q_p75:.3f}  phi_ceil={phi_p75:.3f}")

def in_distress(v, r, q, phi):
    t = thresh[v]
    # union of three half-spaces
    a = (r < t["r_bar"] - 1.0 * t["r_iqr"])
    b = (q > t["q_ceil"] + 1e-9)
    c = (phi > t["phi_ceil"] + 1e-9)
    return a or b or c, dict(a=a, b=b, c=c)

# ---------- Count N_k(t) for k=1,2,3 ----------
nk_by_quarter = {q: {1: 0, 2: 0, 3: 0} for q in quarters}
distress_flags = {}
for q in quarters:
    flags = {}
    for v in VENUES:
        r, native, tail = triples[(v, q)]
        d, _ = in_distress(v, r, native, tail)
        flags[v] = 1 if d else 0
    distress_flags[q] = flags
    total_distressed = sum(flags.values())
    # N_1: number of single-venue distress signals
    nk_by_quarter[q][1] = total_distressed
    # N_2, N_3: joint intersections
    for k in [2, 3]:
        cnt = 0
        for S in combinations(VENUES, k):
            if all(flags[v] == 1 for v in S):
                cnt += 1
        nk_by_quarter[q][k] = cnt

# ---------- T1 polylog prior ----------
# alpha(k,n,m) = k-1 + m*(n-k)/d ; d = n*(m-1)
d = N * (M - 1)  # 12
def alpha(k):
    return (k - 1) + M * (N - k) / d
# T is the quarter ordinal (1..13); constant c_{k,eps} normalises to R_k=1 at
# some reference quarter (choose first quarter 2022-Q4 as the null baseline).
def prior(k, T):
    return (math.log(T + 1)) ** alpha(k)

quarter_idx = {q: i + 1 for i, q in enumerate(quarters)}

rows_out = []
for q in quarters:
    for k in [1, 2, 3]:
        nk = nk_by_quarter[q][k]
        pr = prior(k, quarter_idx[q])
        rows_out.append({
            "quarter": q,
            "T": quarter_idx[q],
            "k": k,
            "Nk_hat": nk,
            "alpha_knm": round(alpha(k), 4),
            "prior_polylog": round(pr, 4),
        })

with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows_out[0].keys())
    w.writeheader()
    w.writerows(rows_out)
print(f"[csv] wrote {OUT_CSV}")

# ---------- Plot Fig 4 ----------
def parse_q(qkey):
    y, qn = qkey.split("-Q")
    return dt.date(int(y), {1:3,2:6,3:9,4:12}[int(qn)], 15)

xs = [parse_q(q) for q in quarters]

fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6), sharex=True)
for ax, k in zip(axes, [1, 2, 3]):
    ys_emp   = [nk_by_quarter[q][k] for q in quarters]
    ys_prior = [prior(k, quarter_idx[q]) for q in quarters]
    # Normalise prior so it equals the first-quarter empirical value (a rough
    # constant fit; the paper's App E documents this normalisation)
    y0_emp = max(ys_emp[0], 1)
    y0_prior = ys_prior[0] if ys_prior[0] > 0 else 1
    scale = y0_emp / y0_prior
    ys_prior_scaled = [y * scale for y in ys_prior]
    ax.plot(xs, ys_emp, marker="o", ms=6, lw=1.8,
            color="firebrick", label=r"$\hat N_" + str(k) + "(t)$ empirical")
    ax.plot(xs, ys_prior_scaled, ls="--", lw=1.4,
            color="steelblue",
            label=r"Polylog prior "
                  r"$c(\log T)^{{{:.2f}}}$".format(alpha(k)))
    # Mark FTX quarter (2022-Q4)
    ftx = dt.date(2022, 11, 15)
    ax.axvline(ftx, color="orange", ls=":", lw=1.0, alpha=0.7)
    ax.set_title(f"$k = {k}$", fontsize=11)
    ax.set_xlabel("Quarter", fontsize=9)
    if ax is axes[0]:
        ax.set_ylabel(r"$k$-fold intersection count", fontsize=9)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=7, framealpha=0.9)
    ax.tick_params(axis="x", labelsize=7, rotation=30)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
fig.suptitle("Empirical $k$-fold intersection counts vs.\\ "
             "polylog prior, 3-venue panel 2022-Q4 to 2025-Q4",
             fontsize=10.5, y=1.02)
plt.tight_layout()
plt.savefig(OUT_FIG, bbox_inches="tight")
plt.close()
print(f"[fig] wrote {OUT_FIG}")

# ---------- Quick numeric summary ----------
print("\n=== Numeric summary (chronological) ===")
print(f"{'Quarter':10s} {'N1':>4} {'N2':>4} {'N3':>4}   distress: BIN OKX BYB")
for q in quarters:
    flg = distress_flags[q]
    print(f"{q:10s} {nk_by_quarter[q][1]:>4} {nk_by_quarter[q][2]:>4} "
          f"{nk_by_quarter[q][3]:>4}   {flg['binance']} {flg['okx']} {flg['bybit']}")

# ---------- Empirical k*: first k where empirical exceeds prior ----------
print("\n=== Empirical crossover k^* ===")
crossings = []
for q in quarters:
    kstar = None
    for k in [1, 2, 3]:
        nk = nk_by_quarter[q][k]
        pr = prior(k, quarter_idx[q])
        if nk > pr:
            kstar = k
            break
    crossings.append((q, kstar))
for q, k in crossings:
    print(f"  {q}: crossover k^* = {k}")

print("\ndone.")
