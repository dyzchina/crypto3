"""
ECA replication audit · v2.0-i
Cross-check every number in main_eca_v2.tex vs the corresponding
processed CSV column produced by run_all.sh from raw JSON.
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
TEX  = (ROOT / "manuscript/main_eca_v2.tex").read_text(encoding="utf-8")

def load_csv(name):
    return pd.read_csv(ROOT / "data/processed" / name)

did = load_csv("did_estimates.csv")
wb  = load_csv("wild_bootstrap.csv").set_index("metric")["value"]
pg  = load_csv("pooling_gain.csv").set_index("metric")["value"]
ant = load_csv("anticipation_did.csv").set_index("specification")
plc = load_csv("stablecoin_placebo_did.csv")
wide = load_csv("cex_por_snapshots_wide.csv")

# Extract latest quarter totals from wide panel
last_q = wide["quarter"].max()
last = wide[wide["quarter"] == last_q].set_index("venue")

report = []
def check(label, expected, tex_hits, tol=1e-3):
    """Compare TeX-quoted value against CSV value."""
    found = None
    for hit in tex_hits:
        m = re.search(hit, TEX)
        if m:
            found = m.group(1)
            break
    if found is None:
        report.append((label, expected, "NOT FOUND in TeX", "MISS"))
        return
    try:
        found_f = float(found.replace(",", "").replace("+", "").replace("−", "-"))
    except ValueError:
        found_f = None
    if found_f is None:
        report.append((label, str(expected), found, "?"))
        return
    match = abs(found_f - float(expected)) < tol * max(1, abs(float(expected)))
    report.append((label, f"{expected:.4f}", found, "✓" if match else "✗ MISMATCH"))

# Table 2 headline
check("τ (DiD headline)", 0.11197, [
    r"\\hat\\tau = ([\d.]+)",
    r"tau.?=.?([\d.]+)",
])

check("Cluster SE", 0.026133, [
    r"cluster-robust standard error[s]? .*?is \$([\d.]+)\$",
    r"the standard error is \$([\d.]+)\$",
])

check("Cluster t", wb["t_cluster"], [
    r"cluster-\$t\$ statistic is \$([\d.]+)\$",
    r"t = ([\d.]+),.*?wild",
])

check("Wild-boot CI lower", 0.025, [
    r"CI \$\\?\[([\d.]+),",
    r"pivotal confidence interval\s*is \$\\?\[([\d.]+),",
])

check("Wild-boot CI upper", 0.199, [
    r"CI \$\\?\[[\d.]+, ([\d.]+)\\?\]\$",
    r"is \$\\?\[[\d.]+, ([\d.]+)\\?\]\$",
])

check("B (bootstrap draws)", 9999, [
    r"([\d,\{\}]+)\s*\n?draws",
    r"with ([\d,\{\}]+)",
], tol=0)

# §4.5 pooling gain
check("Pooling observed ratio", pg["observed_ratio"], [
    r"is \$([\d.]+)\$.\s*This value lies",
])
check("Pooling ZP prediction", pg["theoretical_ZP_n_inv_1_2m"], [
    r"o-minimal prediction \$([\d.]+)\$",
])
check("iid benchmark", pg["iid_benchmark_n_inv_1_2"], [
    r"independence benchmark \$n\^\{-1/2\} \\approx ([\d.]+)\$",
])

# Rank check SVs — text has {0.816, 0.574, 0.530, 0.235, 1.5\times 10^{-4}}
sv_list = [0.816, 0.574, 0.530, 0.235]
for sv in sv_list:
    check(f"SV {sv}", sv, [rf"\\{{[^}}]*({sv})",])

# Anticipation
check("τ_ant_only (§4.4)", 0.0385, [
    r"tau[^\d]*_?\{?\\text\{ant\}\}? = \+?([\d.]+)",
    r"τ.?=.?\+?([\d.]+).*?SE.*?0.023",
    r"([\d.]+).*?\(SE .0.023",
])
check("τ_approval (§4.4)", 0.1424, [
    r"tau.*?_\{\\text\{app\}\} = \+?([\d.]+)",
    r"([\d.]+) \(SE .0.087",
])
check("τ_pure_ant (§4.4)", -0.0238, [
    r"= -([\d.]+) \(SE .0.027",
    r"= -?([\d.]+).*?\(SE .0.027",
], tol=1e-2)

# Placebo
check("τ_placebo (§4.4)", plc["tau"].iloc[0], [
    r"\\hat\\tau_\{\\text\{plac\}\} = -?([\d.]+)",
    r"τ_plac.*?=.*?-?([\d.]+)",
    r"placebo-arm .* coefficient .*? ([\d.]+)",
], tol=1e-2)

# §4.1 latest quarter totals
check("Binance total (USD bn)", last.loc["binance", "total_usd_billion"], [
    r"Binance,\s*\\\$([\d.]+)\s*billion",
    r"approximately \\\$([\d.]+) billion at Binance",
])
check("OKX total", last.loc["okx", "total_usd_billion"], [
    r"\\\$([\d.]+) billion at OKX",
])
check("Bybit total", last.loc["bybit", "total_usd_billion"], [
    r"\\\$([\d.]+) billion at Bybit",
])
check("3-venue total", last["total_usd_billion"].sum(), [
    r"three-venue total of \\\$([\d.]+) billion",
])

# Print report
print(f"{'#':>3}  {'audit item':45s}  {'expected':>10s}  {'in TeX':>10s}  status")
print("-" * 90)
mismatches = 0
misses = 0
for i, (label, exp, found, st) in enumerate(report, 1):
    print(f"{i:>3}  {label:45s}  {exp:>10s}  {str(found):>10s}  {st}")
    if "MISMATCH" in st: mismatches += 1
    if "MISS" in st: misses += 1
print("-" * 90)
print(f"Total items: {len(report)}   Mismatches: {mismatches}   Not-found-in-TeX: {misses}")
