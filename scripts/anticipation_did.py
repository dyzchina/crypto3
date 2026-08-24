"""
C5 · Grayscale-vs-SEC ruling (2023-08-29) as anticipation shock.
Secondary DiD compares the 'anticipation-window' effect vs 'approval-window' effect.

Logic:
- Baseline (approval): treat_post = 1 if quarter >= 2024-Q1
- Anticipation:        treat_ant  = 1 if quarter >= 2023-Q3 (Grayscale ruling 2023-08-29)
- Placebo (pure ant):  treat_ant_only = 1 if quarter in {2023-Q3, 2023-Q4} (2 quarters before approval)

Outcome: risky share = native + long_tail_alts.
If the ETF-approval effect is driven purely by anticipation, treat_ant_only
should already carry a τ close to 0.112. If it doesn't, the approval itself
provides identifying variation beyond anticipation.

Panel: 3 venues (binance/okx/bybit) × 13 quarters = 39 obs.
Estimator: TWFE with venue and quarter fixed effects, cluster-robust SE by venue.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
CSV = ROOT / "data/processed/cex_por_snapshots_wide.csv"
df = pd.read_csv(CSV)
df = df.sort_values(["venue", "quarter"]).reset_index(drop=True)

# Outcome: risky share = native + long_tail_alts
df["risky_share"] = df["share_native_token"] + df["share_long_tail_alts"]

# quarter ordering to compute treatments
def qkey(q):
    y, qq = q.split("-Q")
    return int(y) * 4 + int(qq)

df["qkey"] = df["quarter"].apply(qkey)
Q_APPROVAL      = qkey("2024-Q1")   # Jan 2024 spot-BTC ETF
Q_GRAYSCALE     = qkey("2023-Q3")   # Aug 29 2023 ruling
Q_PURE_ANT_END  = qkey("2023-Q4")

df["post_approval"]     = (df["qkey"] >= Q_APPROVAL).astype(int)
df["post_grayscale"]    = (df["qkey"] >= Q_GRAYSCALE).astype(int)
df["pure_anticipation"] = ((df["qkey"] >= Q_GRAYSCALE) & (df["qkey"] < Q_APPROVAL)).astype(int)

# TWFE with venue + quarter FE, single-treatment coefficient
# Since all 3 venues are treated post-shock, the identification is time-series only;
# to give referee-legible DiD we need placebo units (stablecoin cohort). But the
# question here is *comparing* two treatment definitions on the same panel.
# We do a within-panel demeaning + OLS via numpy.

def twfe_ols(df, treat_col):
    """Venue FE + linear time trend + treatment dummy (quarter FE would absorb
    treatment since all venues are treated simultaneously)."""
    y = df["risky_share"].values.astype(float)
    T = df[treat_col].values.astype(float)
    # venue FE dummies
    venues = pd.get_dummies(df["venue"], drop_first=True, dtype=float).values
    # linear time trend (qkey normalized)
    trend = (df["qkey"].values - df["qkey"].min()).astype(float)
    trend = trend / trend.max() if trend.max() > 0 else trend
    X = np.column_stack([np.ones(len(df)), T, venues, trend.reshape(-1, 1)])
    XtX = X.T @ X
    coef = np.linalg.solve(XtX, X.T @ y)
    resid = y - X @ coef
    # cluster-robust SE by venue
    venues_ids = df["venue"].values
    S = np.zeros_like(XtX)
    for v in np.unique(venues_ids):
        idx = venues_ids == v
        Xv = X[idx]
        rv = resid[idx].reshape(-1, 1)
        S += Xv.T @ (rv @ rv.T) @ Xv
    XtX_inv = np.linalg.inv(XtX)
    G = len(np.unique(venues_ids))
    n = len(df)
    k = X.shape[1]
    dof_adj = (G / (G - 1)) * ((n - 1) / (n - k))
    Vcov = dof_adj * XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.abs(np.diag(Vcov)))  # abs guards against tiny negatives
    tau = coef[1]
    se_tau = se[1]
    t_stat = tau / se_tau if se_tau > 0 else np.nan
    return tau, se_tau, t_stat

print("=" * 68)
print("Anticipation-vs-approval DiD (3-venue panel, TWFE, cluster-SE by venue)")
print("=" * 68)
for treat, label in [
    ("post_approval",     "post_approval  (baseline: >= 2024-Q1)"),
    ("post_grayscale",    "post_grayscale (>= 2023-Q3)"),
    ("pure_anticipation", "pure_ant       ({2023-Q3, 2023-Q4} only, dropped after approval)"),
]:
    tau, se, t = twfe_ols(df, treat)
    print(f"  {label}")
    print(f"    tau = {tau:+.4f}   SE(cluster) = {se:.4f}   t = {t:+.2f}")
    print()

# Additional: decomposition with BOTH treatment dummies + venue FE + linear trend
y = df["risky_share"].values.astype(float)
D_ant = df["pure_anticipation"].values.astype(float)
D_app = df["post_approval"].values.astype(float)
venues = pd.get_dummies(df["venue"], drop_first=True, dtype=float).values
trend = (df["qkey"].values - df["qkey"].min()).astype(float)
trend = trend / trend.max()
X = np.column_stack([np.ones(len(df)), D_ant, D_app, venues, trend.reshape(-1, 1)])
XtX = X.T @ X
coef = np.linalg.solve(XtX, X.T @ y)
resid = y - X @ coef
S = np.zeros_like(XtX)
for v in np.unique(df["venue"].values):
    idx = df["venue"].values == v
    Xv = X[idx]
    rv = resid[idx].reshape(-1, 1)
    S += Xv.T @ (rv @ rv.T) @ Xv
XtX_inv = np.linalg.inv(XtX)
G = df["venue"].nunique()
n = len(df); k = X.shape[1]
dof_adj = (G / (G - 1)) * ((n - 1) / (n - k))
Vcov = dof_adj * XtX_inv @ S @ XtX_inv
se = np.sqrt(np.abs(np.diag(Vcov)))
print("Decomposition: venue FE + linear trend + BOTH treatment dummies")
print(f"  tau_ant_only    = {coef[1]:+.4f}   SE = {se[1]:.4f}   t = {coef[1]/se[1]:+.2f}")
print(f"  tau_approval    = {coef[2]:+.4f}   SE = {se[2]:.4f}   t = {coef[2]/se[2]:+.2f}")

# Save results
out = ROOT / "data/processed/anticipation_did.csv"
rows = []
for treat, label in [
    ("post_approval",     "post_approval"),
    ("post_grayscale",    "post_grayscale"),
    ("pure_anticipation", "pure_anticipation"),
]:
    tau, se_, t = twfe_ols(df, treat)
    rows.append({"specification": label, "tau": tau, "SE_cluster": se_, "t_stat": t})
rows.append({"specification": "decomp_ant_only", "tau": coef[1], "SE_cluster": se[1], "t_stat": coef[1]/se[1]})
rows.append({"specification": "decomp_approval", "tau": coef[2], "SE_cluster": se[2], "t_stat": coef[2]/se[2]})
pd.DataFrame(rows).to_csv(out, index=False, float_format="%.6f")
print(f"\n[write] {out}")
