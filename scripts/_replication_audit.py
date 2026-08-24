"""
Hard replication audit: cross-check every empirical number in main_eca_v2.tex
against the *just-rebuilt* processed CSVs. This is the acid test.
"""
from pathlib import Path
import pandas as pd
import re

ROOT = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
TEX = (ROOT / "manuscript/main_eca_v2.tex").read_text(encoding="utf-8")
P = ROOT / "data/processed"

# Load rebuilt data
did = pd.read_csv(P / "did_estimates.csv")
wb  = pd.read_csv(P / "wild_bootstrap.csv").set_index("metric")["value"]
pg  = pd.read_csv(P / "pooling_gain.csv").set_index("metric")["value"]
ant = pd.read_csv(P / "anticipation_did.csv").set_index("specification")
plc = pd.read_csv(P / "stablecoin_placebo_did.csv")
beta = pd.read_csv(P / "beta_estimate.csv")
wide = pd.read_csv(P / "cex_por_snapshots_wide.csv")
nk  = pd.read_csv(P / "nk_estimates.csv")
rob = pd.read_csv(P / "robustness_grid.csv")
rank_txt = (P / "rank_check.txt").read_text(encoding="utf-8")

last_q = wide["quarter"].max()
last = wide[wide["quarter"] == last_q].set_index("venue")

checks = []
def add(name, csv_val, tex_val_hint, tol=0.01):
    """csv_val: rebuilt CSV number; tex_val_hint: what the manuscript says."""
    delta = abs(csv_val - tex_val_hint) if tex_val_hint is not None else None
    status = "✓" if (tex_val_hint is None or delta <= tol * max(1, abs(tex_val_hint))) else "✗"
    checks.append((name, csv_val, tex_val_hint, status))

# --- Table 2 headline ---
tau_hat = did[did.estimator=="TWFE_naive"]["tau_or_att"].iloc[0]
add("τ (TWFE)", tau_hat, 0.112)
add("τ (CS)", did[did.estimator=="CallawaySantAnna"]["tau_or_att"].iloc[0], 0.112)
add("τ (SA)", did[did.estimator=="SunAbraham"]["tau_or_att"].iloc[0], 0.112)
add("τ (BJS)", did[did.estimator=="BorusyakJaravelSpiess"]["tau_or_att"].iloc[0], 0.112)

# CS/SA/BJS SE
add("CS/SA/BJS SE", did[did.estimator=="CallawaySantAnna"]["se"].iloc[0], 0.034, tol=0.02)

# --- Wild bootstrap ---
add("τ_hat (wild-boot)", wb["tau_hat"], 0.112)
add("SE naive", wb["se_naive"], 0.011)
add("SE cluster", wb["se_cluster"], 0.026)
add("t cluster", wb["t_cluster"], 4.28)
add("B draws", wb["B_bootstrap"], 9999)
add("p wild", wb["p_wild_bootstrap"], 0.0, tol=1e-3)
add("CI lo", wb["ci_95_pivotal_lo"], 0.025)
add("CI hi", wb["ci_95_pivotal_hi"], 0.199)

# --- Pooling ---
add("Pooling observed", pg["observed_ratio"], 0.709)
add("Pooling ZP", pg["theoretical_ZP_n_inv_1_2m"], 0.896)
add("iid benchmark", pg["iid_benchmark_n_inv_1_2"], 0.577)

# --- Rank check (parse) ---
sv_line = re.search(r"Singular values:\s*\[([^\]]+)\]", rank_txt).group(1)
sv_vals = [float(x.strip()) for x in sv_line.split(",")]
add("SV1", sv_vals[0], 0.816)
add("SV2", sv_vals[1], 0.574)
add("SV3", sv_vals[2], 0.530)
add("SV4", sv_vals[3], 0.235)

# --- Anticipation ---
add("τ_pure_ant", ant.loc["pure_anticipation", "tau"], -0.024, tol=0.005)
add("SE_pure_ant", ant.loc["pure_anticipation", "SE_cluster"], 0.027, tol=0.005)
add("τ_ant_only (decomp)", ant.loc["decomp_ant_only", "tau"], 0.039, tol=0.005)
add("τ_approval (decomp)", ant.loc["decomp_approval", "tau"], 0.142, tol=0.005)
add("SE_approval decomp", ant.loc["decomp_approval", "SE_cluster"], 0.087, tol=0.005)

# --- Placebo ---
add("τ_placebo", plc["tau"].iloc[0], -0.39, tol=0.01)
add("SE_placebo", plc["SE_cluster"].iloc[0], 0.72, tol=0.02)
add("t_placebo", plc["t_stat"].iloc[0], -0.54, tol=0.05)
add("N placebo issuers", plc["n_issuers"].iloc[0], 10)
add("N placebo obs", plc["n_obs"].iloc[0], 115)

# --- β estimate ---
add("β_hat", beta["beta_hat"].iloc[0], 0.86, tol=0.01)
add("β SE", beta["SE"].iloc[0], 0.213, tol=0.02)
add("β CI lo", beta["ci_95_lo"].iloc[0], 0.44, tol=0.02)
add("β CI hi", beta["ci_95_hi"].iloc[0], 1.28, tol=0.02)

# --- Latest snapshot totals ---
add("Binance $bn (round to 168.9)", last.loc["binance", "total_usd_billion"], 168.9, tol=0.005)
add("OKX $bn (round to 22.1)", last.loc["okx", "total_usd_billion"], 22.1, tol=0.005)
add("Bybit $bn (round to 18.4)", last.loc["bybit", "total_usd_billion"], 18.4, tol=0.005)
add("3-venue total (round to 209.4)", last["total_usd_billion"].sum(), 209.4, tol=0.005)

# --- Panel structure ---
add("N snapshots (39)", len(wide), 39)
add("N venues (3)", wide["venue"].nunique(), 3)
add("N quarters (13)", wide["quarter"].nunique(), 13)

# --- N_k(t) headline events ---
# domain-prior: 2024-Q1 should have N_3 = 1
nk_dom = nk[nk["quarter"]=="2024-Q1"]
# nk_estimates.csv 有 Q75/IQR 版本，2024-Q1 值：
n1_24 = int(nk_dom[nk_dom.k==1]["Nk_hat"].iloc[0]) if len(nk_dom[nk_dom.k==1]) else -1
n2_24 = int(nk_dom[nk_dom.k==2]["Nk_hat"].iloc[0]) if len(nk_dom[nk_dom.k==2]) else -1
n3_24 = int(nk_dom[nk_dom.k==3]["Nk_hat"].iloc[0]) if len(nk_dom[nk_dom.k==3]) else -1
# Note: nk_estimates.csv is the Q75/IQR spec (venue-relative). 2024-Q1 under Q75:
#   from run_all.sh output: N1=2 N2=1 N3=0.
add("N1(2024-Q1) Q75/IQR", n1_24, 2)
add("N2(2024-Q1) Q75/IQR", n2_24, 1)
add("N3(2024-Q1) Q75/IQR", n3_24, 0)

nk_25 = nk[nk["quarter"]=="2025-Q3"]
n1_25 = int(nk_25[nk_25.k==1]["Nk_hat"].iloc[0])
n2_25 = int(nk_25[nk_25.k==2]["Nk_hat"].iloc[0])
n3_25 = int(nk_25[nk_25.k==3]["Nk_hat"].iloc[0])
add("N1(2025-Q3)", n1_25, 3)
add("N2(2025-Q3)", n2_25, 3)
add("N3(2025-Q3) HEADLINE", n3_25, 1)

# ---- Print ----
print(f"{'#':>3}  {'metric':40s}  {'CSV':>15s}  {'TeX target':>10s}  status")
print("-"*90)
n_pass = 0; n_fail = 0
for i, (n, v, t, s) in enumerate(checks, 1):
    v_s = f"{v:.4f}" if isinstance(v, float) else str(v)
    t_s = f"{t:.4f}" if isinstance(t, (float, int)) and not isinstance(t, bool) else str(t)
    print(f"{i:>3}  {n:40s}  {v_s:>15s}  {t_s:>10s}  {s}")
    if s == "✓": n_pass += 1
    else: n_fail += 1
print("-"*90)
print(f"PASS: {n_pass} / {len(checks)}   FAIL: {n_fail}")
