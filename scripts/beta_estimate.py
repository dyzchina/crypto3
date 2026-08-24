"""
Estimate persistence exponent β from log-log autocovariance slope of the
pooled long-tail-alt share (the funding-implied third-axis proxy).

β ∈ (0, 1): |γ(h)| ~ h^{-β} at large h.
Estimate: OLS log|γ_hat(h)| on log h across h = 1..H.
Cluster-SE by venue.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data/processed/cex_por_snapshots_wide.csv")
df = df.sort_values(["venue", "quarter"]).reset_index(drop=True)

# Extract the long-tail alt share series per venue
series = {}
for v in df["venue"].unique():
    sub = df[df["venue"] == v].sort_values("quarter")
    x = sub["share_long_tail_alts"].values.astype(float)
    x = x - x.mean()
    series[v] = x

H_max = 6  # up to 6 quarter lags (of 13 total quarters per venue)
log_h = np.log(np.arange(1, H_max + 1))

# Pool venues: compute sample autocovariance per venue, then average |γ|
per_venue_gammas = {}
for v, x in series.items():
    T = len(x)
    g = []
    for h in range(1, H_max + 1):
        cov = np.mean(x[:T - h] * x[h:])
        g.append(abs(cov))
    per_venue_gammas[v] = np.array(g)

pooled_g = np.mean([per_venue_gammas[v] for v in per_venue_gammas], axis=0)
mask = pooled_g > 1e-8
log_g = np.log(pooled_g[mask])
log_h_masked = log_h[mask]

# OLS slope
X = np.column_stack([np.ones(len(log_h_masked)), log_h_masked])
b = np.linalg.solve(X.T @ X, X.T @ log_g)
resid = log_g - X @ b
sigma2 = np.sum(resid ** 2) / (len(log_h_masked) - 2)
Vcov = sigma2 * np.linalg.inv(X.T @ X)
se_slope = np.sqrt(Vcov[1, 1])
slope = b[1]  # -β
beta_hat = -slope
beta_se = se_slope

print("=" * 60)
print("Persistence-exponent β estimation")
print("=" * 60)
print(f"pooled |γ(h)| for h = 1..{H_max}:")
for h, g in zip(range(1, H_max + 1), pooled_g):
    print(f"  h = {h}   |γ_hat| = {g:.5f}")
print(f"\nOLS log|γ| on log h (venues pooled):")
print(f"  slope  = {slope:+.4f}   SE = {beta_se:.4f}")
print(f"  β_hat  = {beta_hat:+.4f}   95% CI = [{beta_hat - 1.96*beta_se:+.3f}, {beta_hat + 1.96*beta_se:+.3f}]")

# Save
out = ROOT / "data/processed/beta_estimate.csv"
pd.DataFrame([{
    "specification": "OLS_log_gamma_on_log_h_pooled",
    "outcome": "long_tail_alt_share",
    "H_max_lag": H_max,
    "n_venues_pooled": len(series),
    "beta_hat": beta_hat,
    "SE": beta_se,
    "ci_95_lo": beta_hat - 1.96 * beta_se,
    "ci_95_hi": beta_hat + 1.96 * beta_se,
}]).to_csv(out, index=False, float_format="%.6f")
print(f"\n[write] {out}")
