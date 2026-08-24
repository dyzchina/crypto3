"""
Stablecoin placebo DiD (真数据版本).

Panel: 10 stablecoin issuers × 13 quarters (2022-Q4..2025-Q4).
Outcome: log circulating supply. Compare TWFE DiD on the placebo cohort
with the 3-venue CEX headline τ = 0.112. If stablecoin cohort shows no
comparable post-ETF-approval jump, this is a valid placebo.

Source: DefiLlama stable_<SYMBOL>_id*.json (150 MB, in data/raw_stablecoin_placebo).
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from datetime import datetime, timezone

ROOT = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
RAW  = ROOT / "data/raw_stablecoin_placebo"

# Quarter-end target dates matching the CEX panel (2022-Q4..2025-Q4)
QUARTERS = [
    ("2022-Q4", "2022-12-31"), ("2023-Q1", "2023-03-31"),
    ("2023-Q2", "2023-06-30"), ("2023-Q3", "2023-09-30"),
    ("2023-Q4", "2023-12-31"), ("2024-Q1", "2024-03-31"),
    ("2024-Q2", "2024-06-30"), ("2024-Q3", "2024-09-30"),
    ("2024-Q4", "2024-12-31"), ("2025-Q1", "2025-03-31"),
    ("2025-Q2", "2025-06-30"), ("2025-Q3", "2025-09-30"),
    ("2025-Q4", "2025-12-31"),
]

def load_issuer(path):
    d = json.load(open(path, encoding="utf-8"))
    sym = d["symbol"].upper()
    rows = []
    for t in d.get("tokens", []):
        date = datetime.fromtimestamp(t["date"], tz=timezone.utc).date()
        c = t.get("circulating") or {}
        v = c.get("peggedUSD") if isinstance(c, dict) else None
        if v is not None and v > 0:
            rows.append((date, v))
    return sym, pd.DataFrame(rows, columns=["date", "circulating_usd"])

issuers = {}
for p in sorted(RAW.glob("stable_*.json")):
    sym, df = load_issuer(p)
    issuers[sym] = df

print(f"[loaded] {len(issuers)} issuers: {list(issuers.keys())}")

# Build panel: quarter-end snapshot (nearest date within ±3 days)
panel = []
for sym, df in issuers.items():
    df = df.sort_values("date")
    df["date_dt"] = pd.to_datetime(df["date"])
    for q, qend in QUARTERS:
        target = pd.Timestamp(qend)
        # nearest date within ±30d window
        diff = (df["date_dt"] - target).abs()
        j = diff.idxmin() if len(diff) > 0 else None
        if j is None or diff[j].days > 30:
            continue
        v = df.loc[j, "circulating_usd"]
        panel.append({
            "issuer": sym, "quarter": q, "snapshot_date": df.loc[j, "date_dt"].date().isoformat(),
            "circulating_usd": v,
        })

panel = pd.DataFrame(panel)
print(f"[panel] {len(panel)} rows across {panel['issuer'].nunique()} issuers × {panel['quarter'].nunique()} quarters")
panel.to_csv(ROOT / "data/processed/stablecoin_placebo_panel.csv", index=False, float_format="%.2f")

# TWFE DiD on log outcome
panel["log_supply"] = np.log(panel["circulating_usd"].astype(float))

def qkey(q):
    y, qq = q.split("-Q")
    return int(y) * 4 + int(qq)
panel["qkey"] = panel["quarter"].apply(qkey)
Q_APP = qkey("2024-Q1")
panel["post_approval"] = (panel["qkey"] >= Q_APP).astype(int)

y = panel["log_supply"].values.astype(float)
T = panel["post_approval"].values.astype(float)
issuers_d = pd.get_dummies(panel["issuer"], drop_first=True, dtype=float).values
trend = (panel["qkey"].values - panel["qkey"].min()).astype(float)
trend = trend / trend.max() if trend.max() > 0 else trend
X = np.column_stack([np.ones(len(panel)), T, issuers_d, trend.reshape(-1, 1)])
coef = np.linalg.solve(X.T @ X, X.T @ y)
resid = y - X @ coef
S = np.zeros((X.shape[1], X.shape[1]))
for iss in panel["issuer"].unique():
    idx = panel["issuer"].values == iss
    Xv = X[idx]; rv = resid[idx].reshape(-1, 1)
    S += Xv.T @ (rv @ rv.T) @ Xv
XtX_inv = np.linalg.inv(X.T @ X)
G = panel["issuer"].nunique(); n = len(panel); k = X.shape[1]
dof = (G / (G - 1)) * ((n - 1) / (n - k))
Vcov = dof * XtX_inv @ S @ XtX_inv
se = np.sqrt(np.abs(np.diag(Vcov)))

print()
print("=" * 68)
print("Stablecoin placebo DiD · issuer FE + linear trend · cluster-SE by issuer")
print("=" * 68)
print(f"  τ_placebo (log-supply) = {coef[1]:+.4f}   SE = {se[1]:.4f}   t = {coef[1]/se[1]:+.2f}")
print()
print("Compare with CEX headline: τ_CEX (risky share) = +0.1125, t = +1.51")
print("Note: outcome scales differ (log-supply vs share level), so what matters")
print("      is the sign / stat-significance rather than magnitude directly.")

out = ROOT / "data/processed/stablecoin_placebo_did.csv"
pd.DataFrame([{
    "specification": "stablecoin_placebo_TWFE_trend",
    "outcome": "log_circulating_supply",
    "tau": coef[1], "SE_cluster": se[1], "t_stat": coef[1] / se[1],
    "n_issuers": G, "n_obs": n,
}]).to_csv(out, index=False, float_format="%.6f")
print(f"\n[write] {out}")
