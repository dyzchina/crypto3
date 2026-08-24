"""wild_bootstrap.py -- wild-cluster bootstrap for the DiD ATT.

Cameron-Gelbach-Miller (2008) wild-cluster bootstrap-t under Rademacher weights,
adapted for our 13-cluster setting (3 CEX + 10 stablecoin placebo).

Returns bootstrap p-value and 95% CI for tau-hat.
"""
import csv, math, sys
from pathlib import Path
import numpy as np
import datetime as dt

# Reuse the panel construction from did_regression.py (Simplified inline replica)
BASE = Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root
CSV_IN = BASE / "data" / "processed" / "cex_por_snapshots_wide.csv"

with CSV_IN.open(encoding="utf-8") as f:
    cex_rows = list(csv.DictReader(f))

placebo_issuers = ["USDT", "USDC", "DAI", "FRAX", "TUSD",
                   "USDP", "PYUSD", "FDUSD", "BUSD", "LUSD"]
QUARTERS = sorted({r["quarter"] for r in cex_rows})

SHOCK_QUARTER = "2024-Q1"
def is_post(q):
    y, qn = q.split("-Q")
    return (int(y), int(qn)) >= (2024, 1)

# Outcome for CEX = native + long-tail
# Outcome for placebo = 0 (constant peg proxy)
panel = []
for r in cex_rows:
    y = float(r["share_native_token"]) + float(r["share_long_tail_alts"])
    panel.append({"entity": r["venue"], "quarter": r["quarter"],
                    "y": y, "treated": 1,
                    "post": 1 if is_post(r["quarter"]) else 0})
for iss in placebo_issuers:
    for q in QUARTERS:
        panel.append({"entity": iss, "quarter": q,
                        "y": 0.0, "treated": 0,
                        "post": 1 if is_post(q) else 0})

def twfe_tau(rows):
    """Return tau, per-cluster residuals, cluster labels."""
    entities = sorted({r["entity"] for r in rows})
    quarters = sorted({r["quarter"] for r in rows})
    E = {e: i for i, e in enumerate(entities)}
    Q = {q: j for j, q in enumerate(quarters)}
    n_e, n_q = len(entities), len(quarters)
    y_arr = np.zeros((n_e, n_q))
    d_arr = np.zeros((n_e, n_q))
    for r in rows:
        i, j = E[r["entity"]], Q[r["quarter"]]
        y_arr[i, j] = r["y"]
        d_arr[i, j] = r["treated"] * r["post"]
    ybar_i = y_arr.mean(axis=1)
    ybar_t = y_arr.mean(axis=0)
    ybar = y_arr.mean()
    dbar_i = d_arr.mean(axis=1)
    dbar_t = d_arr.mean(axis=0)
    dbar = d_arr.mean()
    y_tilde = y_arr - ybar_i[:, None] - ybar_t[None, :] + ybar
    d_tilde = d_arr - dbar_i[:, None] - dbar_t[None, :] + dbar
    num = float((d_tilde * y_tilde).sum())
    den = float((d_tilde ** 2).sum())
    tau = num / den if den > 0 else float("nan")
    resid = y_tilde - tau * d_tilde
    return tau, resid, y_arr, d_arr, entities, quarters

tau_hat, resid, y_arr, d_arr, entities, quarters = twfe_tau(panel)
print(f"[point] tau_hat = {tau_hat:+.4f}")

# Naive homoskedastic SE
n_e = len(entities); n_q = len(quarters)
dof = n_e * n_q - n_e - n_q + 1 - 1
d_var = (d_arr - d_arr.mean(axis=1, keepdims=True) - d_arr.mean(axis=0, keepdims=True) + d_arr.mean())
d_ss  = float((d_var ** 2).sum())
sigma2 = float((resid ** 2).sum()) / max(dof, 1)
se_naive = math.sqrt(sigma2 / d_ss) if d_ss > 0 else float("nan")
print(f"[naive SE] {se_naive:.4f}   t = {tau_hat/se_naive:.2f}")

# Cluster-robust SE (cluster by entity)
d_tilde_mat = d_var
u_mat = resid
XtX_inv = 1.0 / d_ss  # scalar because single regressor
sum_gk = 0.0
for i in range(n_e):
    xi = d_tilde_mat[i, :]  # length n_q
    ui = u_mat[i, :]
    gi = float((xi * ui).sum())
    sum_gk += gi * gi
G = n_e
V_cluster = (G / (G - 1)) * XtX_inv * sum_gk * XtX_inv
se_cluster = math.sqrt(V_cluster)
print(f"[cluster SE] {se_cluster:.4f}   t = {tau_hat/se_cluster:.2f}")

# ------- Wild-cluster bootstrap (Rademacher) -------
B = 9999
np.random.seed(4626)  # fixed seed for reproducibility
tau_boot = np.zeros(B)
# Compute restricted residuals (impose H0: tau = 0)
# Then y_star = X * tau_hat_restricted + w_i * u_hat_restricted, w_i in {-1, +1}
# In TWFE we impose the null on tau, so restricted residuals are y_tilde (since tau_restricted=0 => resid = y_tilde)
u_rest = y_arr - y_arr.mean(axis=1, keepdims=True) - y_arr.mean(axis=0, keepdims=True) + y_arr.mean()

for b in range(B):
    w = np.random.choice([-1.0, 1.0], size=n_e)
    y_star = y_arr.copy()
    # Replace with 0 + w_i * u_rest (imposing null)
    # Actually wild-cluster procedure: y_star = X*beta_null + w_i * u_rest_i where w_i is per-cluster
    y_star = w[:, None] * u_rest
    # Refit TWFE (only regressor is d_tilde already computed; d_tilde doesn't change)
    yb_i = y_star.mean(axis=1)
    yb_t = y_star.mean(axis=0)
    yb   = y_star.mean()
    yst_tilde = y_star - yb_i[:, None] - yb_t[None, :] + yb
    num_b = float((d_var * yst_tilde).sum())
    tau_b = num_b / d_ss
    # cluster SE under bootstrap
    resid_b = yst_tilde - tau_b * d_var
    sum_gk_b = 0.0
    for i in range(n_e):
        gi = float((d_var[i, :] * resid_b[i, :]).sum())
        sum_gk_b += gi * gi
    Vb = (G / (G - 1)) * XtX_inv * sum_gk_b * XtX_inv
    seb = math.sqrt(Vb) if Vb > 0 else float("nan")
    tau_boot[b] = tau_b / seb if seb > 0 else 0.0

t_actual = tau_hat / se_cluster
# Two-sided p-value: fraction of |t_boot| >= |t_actual|
p_boot = float((np.abs(tau_boot) >= abs(t_actual)).mean())
# 95% percentile CI (transform back through cluster-SE)
lo_t = float(np.quantile(tau_boot, 0.025))
hi_t = float(np.quantile(tau_boot, 0.975))
lo_tau = tau_hat + lo_t * se_cluster  # actually pivotal: tau_hat - hi_t * se, tau_hat - lo_t * se
hi_tau = tau_hat + hi_t * se_cluster

# Pivotal CI (more standard): [tau_hat - q_0.975 * se, tau_hat - q_0.025 * se]
lo_piv = tau_hat - hi_t * se_cluster
hi_piv = tau_hat - lo_t * se_cluster

print("\n=== Wild-cluster bootstrap ===")
print(f"  B = {B}")
print(f"  |t| actual = {abs(t_actual):.3f}")
print(f"  Two-sided p (|t_boot| >= |t|) = {p_boot:.4f}")
print(f"  95% percentile CI (t): [{lo_t:.3f}, {hi_t:.3f}]")
print(f"  95% CI on tau (pivotal): [{lo_piv:+.4f}, {hi_piv:+.4f}]")
print(f"  95% CI on tau (percentile-symmetric): [{lo_tau:+.4f}, {hi_tau:+.4f}]")

# Write CSV
import csv as _csv
with (BASE / "data" / "processed" / "wild_bootstrap.csv").open("w", encoding="utf-8", newline="") as f:
    w = _csv.writer(f)
    w.writerow(["metric", "value"])
    w.writerow(["tau_hat", f"{tau_hat:+.6f}"])
    w.writerow(["se_naive", f"{se_naive:.6f}"])
    w.writerow(["se_cluster", f"{se_cluster:.6f}"])
    w.writerow(["t_cluster", f"{t_actual:.4f}"])
    w.writerow(["B_bootstrap", B])
    w.writerow(["seed", 4626])
    w.writerow(["p_wild_bootstrap", f"{p_boot:.4f}"])
    w.writerow(["ci_95_pivotal_lo", f"{lo_piv:+.4f}"])
    w.writerow(["ci_95_pivotal_hi", f"{hi_piv:+.4f}"])
print(f"\n[csv] wrote {BASE / 'data' / 'processed' / 'wild_bootstrap.csv'}")
