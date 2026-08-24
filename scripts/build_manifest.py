"""
Build SHA-256 MANIFEST + data provenance mapping for cex_contagion_v2.0.

Outputs:
  - MANIFEST.sha256      · every real data file with SHA-256 + size + mtime
  - docs/data_provenance.md · figure/table → data file mapping
"""
from pathlib import Path
import hashlib
import time
import json

ROOT = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")

def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

DATA_DIRS = ["data/raw_por", "data/raw_stablecoin_placebo",
             "data/raw/controls", "data/processed"]

rows = []
for rel in DATA_DIRS:
    d = ROOT / rel
    if not d.exists(): continue
    for p in sorted(d.rglob("*")):
        if not p.is_file(): continue
        rel_p = p.relative_to(ROOT).as_posix()
        sz = p.stat().st_size
        mt = time.strftime("%Y-%m-%d", time.localtime(p.stat().st_mtime))
        try:
            sha = sha256_of(p)
        except Exception:
            sha = "ERR"
        rows.append((rel_p, sz, mt, sha))

# Write manifest
man = ROOT / "MANIFEST.sha256"
with open(man, "w", encoding="utf-8") as f:
    f.write("# SHA-256 manifest for cex_contagion_v2.0 (v2.0-g)\n")
    f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M')} local time\n")
    f.write(f"# Total files: {len(rows)}   Total bytes: {sum(r[1] for r in rows):,}\n\n")
    f.write(f"{'SHA-256':64s}  {'size(bytes)':>12s}  {'mtime':10s}  path\n")
    f.write(f"{'-'*64}  {'-'*12}  {'-'*10}  ----\n")
    for path, sz, mt, sha in rows:
        f.write(f"{sha}  {sz:>12d}  {mt}  {path}\n")

print(f"[write] {man}")
print(f"[stats] {len(rows)} files, {sum(r[1] for r in rows)/1024/1024:.1f} MB")

# --- Provenance markdown ---
prov = ROOT / "docs/data_provenance.md"
prov.parent.mkdir(parents=True, exist_ok=True)
with open(prov, "w", encoding="utf-8") as f:
    f.write("# Data Provenance · cex_contagion_v2.0 (v2.0-g)\n\n")
    f.write("Every figure and table in `Main.pdf` traces to the files below,\n")
    f.write("all archived in this repository under `data/` and hashed in\n")
    f.write("`MANIFEST.sha256`. Data-charter levels: ① REAL (script-backed, public\n")
    f.write("source), ② PROXY (labelled), ③ SIMULATED (grounded, labelled).\n\n")
    f.write("## Figures\n\n")
    f.write("| Figure | Content | Data source | Charter level | File(s) |\n")
    f.write("|---|---|---|:---:|---|\n")
    f.write("| Fig 1 | 5 CEX × 5 asset heatmap | DefiLlama daily protocol reserves (3 venues); Coinbase/Kraken hatched N/A | ① REAL (3v) | `data/raw_por/{binance,okx,bybit}/_*_raw.json`, `data/processed/cex_por_snapshots_wide.csv` |\n")
    f.write("| Fig 2 | 6-event distress timeline + FTX ±60d RDD | Chapter 11 filing dates from PACER/kroll dockets | ① REAL | (event dates hard-coded in `scripts/figure_01_v04.py`; docket PDFs TODO: `data/bankruptcy_dockets/`) |\n")
    f.write("| Fig 3 | 3-venue reserve share trajectories | Same as Fig 1 | ① REAL | `data/processed/cex_por_snapshots_wide.csv` |\n")
    f.write("| Fig 4 | dual-panel $\\hat N_k(t)$ vs polylog prior | Estimator output on Fig 1 data + theory fit | ① REAL points | `data/processed/nk_estimates.csv` |\n")
    f.write("| Fig 5 | Algorithm 1 flowchart | Conceptual (no data) | 示意 | `scripts/build_fig5_algorithm.py` |\n\n")
    f.write("## Tables\n\n")
    f.write("| Table | Content | Data source | Charter level | File(s) |\n")
    f.write("|---|---|---|:---:|---|\n")
    f.write("| Table 1 | 5 bankruptcy dates + reserve gaps (USD bn) | First-day motions / SoFA / 341 meeting reports from chapter 11 dockets | ① REAL by reference (dockets TODO to archive) | Docket case numbers in Table 1 caption; PACER retrieval scripts to be added |\n")
    f.write("| Table 2 | 8-cell DiD robustness grid | 3-venue CEX panel + Callaway-SantAnna / Sun-Abraham / Borusyak et al. estimators | ① REAL | `data/processed/{did_estimates,robustness_grid,wild_bootstrap}.csv` |\n\n")
    f.write("## §4.4 secondary results\n\n")
    f.write("| Section | Content | Data source | Charter level | File(s) |\n")
    f.write("|---|---|---|:---:|---|\n")
    f.write("| §4.4 Anticipation channel | 3 secondary DiDs (Grayscale window, pure anticipation, decomposition) | Same 3-venue panel | ① REAL | `data/processed/anticipation_did.csv`, `scripts/anticipation_did.py` |\n")
    f.write("| §4.4 Placebo cohort | 10 stablecoin issuer DiD | DefiLlama circulating-supply daily JSON, 10 issuers | ① REAL | `data/raw_stablecoin_placebo/stable_*.json`, `data/processed/{stablecoin_placebo_panel,stablecoin_placebo_did}.csv`, `scripts/stablecoin_placebo_did.py` |\n")
    f.write("| §4.5 Pooling gain / App D transversality | 3-venue reserve matrix SVs | Same 3-venue panel | ① REAL | `data/processed/{pooling_gain.csv,rank_check.txt}` |\n\n")
    f.write("## Deferred to companion release\n\n")
    f.write("- **Coinbase (SEC 10-Q Note 5)** · only EDGAR metadata `data/raw_por/coinbase/edgar_10q_index.json` archived; per-quarter asset-class shares require iXBRL Note-5 parsing.\n")
    f.write("- **Kraken (Nexia SAB\\&T semi-annual PoR)** · not yet joined.\n")
    f.write("- **Bankruptcy first-day motion PDFs** · not yet archived to `data/bankruptcy_dockets/`; case numbers documented in Table 1 caption. Public retrieval via kroll (Genesis: case23-10063.kroll.com, etc.).\n\n")
    f.write("## Compilation of the paper\n\n")
    f.write("```bash\n")
    f.write("cd manuscript && bash ../scripts/build.sh   # xelatex 3-pass + bibtex\n")
    f.write("```\n")

print(f"[write] {prov}")
