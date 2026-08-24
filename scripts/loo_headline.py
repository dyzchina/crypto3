"""loo_headline.py -- test if 2025-Q3 hat N_3 = 1 is a threshold artifact."""
import csv, math, sys
from pathlib import Path
from itertools import combinations
import numpy as np

BASE = Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root
CSV = BASE / "data" / "processed" / "cex_por_snapshots_wide.csv"

with CSV.open(encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

VENUES = ["binance", "okx", "bybit"]
QUARTERS = sorted({r["quarter"] for r in rows})

def get_row(v, q):
    for r in rows:
        if r["venue"] == v and r["quarter"] == q:
            return r
    return None

def triple(row):
    safe = float(row["share_BTC"]) + float(row["share_ETH"]) + float(row["share_USDT_USDC"])
    r_log = math.log(max(safe, 1e-6))
    native = float(row["share_native_token"])
    tail = float(row["share_long_tail_alts"])
    return r_log, native, tail, safe

def make_thr(quarters_in):
    thr = {}
    for v in VENUES:
        vseries = [triple(get_row(v, q)) for q in quarters_in]
        rs = [t[0] for t in vseries]
        qs = [t[1] for t in vseries]
        phis = [t[2] for t in vseries]
        thr[v] = {
            "r_med": float(np.median(rs)),
            "r_iqr": float(np.percentile(rs, 75) - np.percentile(rs, 25)),
            "q75_native": float(np.percentile(qs, 75)),
            "q75_tail":   float(np.percentile(phis, 75)),
        }
    return thr

def distress(v, r, native, tail, thr):
    t = thr[v]
    a = r < t["r_med"] - 1.0 * t["r_iqr"]
    b = native > t["q75_native"] + 1e-9
    c = tail   > t["q75_tail"]   + 1e-9
    return int(a or b or c)

def hard_prior(v, r, native, tail, safe):
    a = native > 0.15 + 1e-9
    b = safe   < 0.60 - 1e-9
    c = tail   > 0.25 + 1e-9
    return int(a or b or c)

def count_nk(flags, k):
    cnt = 0
    for S in combinations(VENUES, k):
        if all(flags[v] == 1 for v in S):
            cnt += 1
    return cnt

print("=" * 75)
print("LEAVE-ONE-OUT ROBUSTNESS TEST for 2025-Q3 headline N_3 = 1")
print("=" * 75)

orig = make_thr(QUARTERS)

print("\n--- Original panel-wide thresholds (full 13 quarters) ---")
for q in QUARTERS:
    fl = {}
    for v in VENUES:
        r_log, nat, tail, safe = triple(get_row(v, q))
        fl[v] = distress(v, r_log, nat, tail, orig)
    n1, n2, n3 = count_nk(fl, 1), count_nk(fl, 2), count_nk(fl, 3)
    mark = "  <== HEADLINE" if q == "2025-Q3" else ""
    print(f"  {q}  N1={n1} N2={n2} N3={n3}  flags[BIN,OKX,BYB]={fl['binance']}{fl['okx']}{fl['bybit']}{mark}")

print("\n--- Leave-one-out (drop t from threshold estimation) ---")
for q in QUARTERS:
    thr_loo = make_thr([qq for qq in QUARTERS if qq != q])
    fl = {}
    for v in VENUES:
        r_log, nat, tail, safe = triple(get_row(v, q))
        fl[v] = distress(v, r_log, nat, tail, thr_loo)
    n1, n2, n3 = count_nk(fl, 1), count_nk(fl, 2), count_nk(fl, 3)
    mark = "  <== HEADLINE" if q == "2025-Q3" else ""
    print(f"  {q}  N1={n1} N2={n2} N3={n3}  flags={fl['binance']}{fl['okx']}{fl['bybit']}{mark}")

print("\n--- Domain hard priors (native>0.15 OR safe<0.60 OR tail>0.25) ---")
for q in QUARTERS:
    fl = {}
    for v in VENUES:
        r_log, nat, tail, safe = triple(get_row(v, q))
        fl[v] = hard_prior(v, r_log, nat, tail, safe)
    n1, n2, n3 = count_nk(fl, 1), count_nk(fl, 2), count_nk(fl, 3)
    mark = "  <== HEADLINE" if q == "2025-Q3" else ""
    print(f"  {q}  N1={n1} N2={n2} N3={n3}  flags={fl['binance']}{fl['okx']}{fl['bybit']}{mark}")

print("\n" + "=" * 75)
print("SUMMARY: 2025-Q3 headline (N_3) survival")
print("=" * 75)
q = "2025-Q3"
thr_loo = make_thr([qq for qq in QUARTERS if qq != q])
fl_orig = {}; fl_loo_ = {}; fl_hard = {}
for v in VENUES:
    r_log, nat, tail, safe = triple(get_row(v, q))
    fl_orig[v] = distress(v, r_log, nat, tail, orig)
    fl_loo_[v] = distress(v, r_log, nat, tail, thr_loo)
    fl_hard[v] = hard_prior(v, r_log, nat, tail, safe)
print(f"  Q75/IQR panel-wide      -> N1={count_nk(fl_orig,1)} N2={count_nk(fl_orig,2)} N3={count_nk(fl_orig,3)}")
print(f"  Q75/IQR leave-one-out   -> N1={count_nk(fl_loo_,1)} N2={count_nk(fl_loo_,2)} N3={count_nk(fl_loo_,3)}")
print(f"  Domain hard priors      -> N1={count_nk(fl_hard,1)} N2={count_nk(fl_hard,2)} N3={count_nk(fl_hard,3)}")
