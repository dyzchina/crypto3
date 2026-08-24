# Data Provenance · cex_contagion_v2.0 (v2.0-g)

Every figure and table in `Main.pdf` traces to the files below,
all archived in this repository under `data/` and hashed in
`MANIFEST.sha256`. Data-charter levels: ① REAL (script-backed, public
source), ② PROXY (labelled), ③ SIMULATED (grounded, labelled).

## Figures

| Figure | Content | Data source | Charter level | File(s) |
|---|---|---|:---:|---|
| Fig 1 | 5 CEX × 5 asset heatmap | DefiLlama daily protocol reserves (3 venues); Coinbase/Kraken hatched N/A | ① REAL (3v) | `data/raw_por/{binance,okx,bybit}/_*_raw.json`, `data/processed/cex_por_snapshots_wide.csv` |
| Fig 2 | 6-event distress timeline + FTX ±60d RDD | Chapter 11 filing dates from PACER/kroll dockets | ① REAL | (event dates hard-coded in `scripts/figure_01_v04.py`; docket PDFs TODO: `data/bankruptcy_dockets/`) |
| Fig 3 | 3-venue reserve share trajectories | Same as Fig 1 | ① REAL | `data/processed/cex_por_snapshots_wide.csv` |
| Fig 4 | dual-panel $\hat N_k(t)$ vs polylog prior | Estimator output on Fig 1 data + theory fit | ① REAL points | `data/processed/nk_estimates.csv` |
| Fig 5 | Algorithm 1 flowchart | Conceptual (no data) | 示意 | `scripts/build_fig5_algorithm.py` |

## Tables

| Table | Content | Data source | Charter level | File(s) |
|---|---|---|:---:|---|
| Table 1 | 5 bankruptcy dates + reserve gaps (USD bn) | First-day motions / SoFA / 341 meeting reports from chapter 11 dockets | ① REAL by reference (dockets TODO to archive) | Docket case numbers in Table 1 caption; PACER retrieval scripts to be added |
| Table 2 | 8-cell DiD robustness grid | 3-venue CEX panel + Callaway-SantAnna / Sun-Abraham / Borusyak et al. estimators | ① REAL | `data/processed/{did_estimates,robustness_grid,wild_bootstrap}.csv` |

## §4.4 secondary results

| Section | Content | Data source | Charter level | File(s) |
|---|---|---|:---:|---|
| §4.4 Anticipation channel | 3 secondary DiDs (Grayscale window, pure anticipation, decomposition) | Same 3-venue panel | ① REAL | `data/processed/anticipation_did.csv`, `scripts/anticipation_did.py` |
| §4.4 Placebo cohort | 10 stablecoin issuer DiD | DefiLlama circulating-supply daily JSON, 10 issuers | ① REAL | `data/raw_stablecoin_placebo/stable_*.json`, `data/processed/{stablecoin_placebo_panel,stablecoin_placebo_did}.csv`, `scripts/stablecoin_placebo_did.py` |
| §4.5 Pooling gain / App D transversality | 3-venue reserve matrix SVs | Same 3-venue panel | ① REAL | `data/processed/{pooling_gain.csv,rank_check.txt}` |

## Deferred to companion release

- **Coinbase (SEC 10-Q Note 5)** · only EDGAR metadata `data/raw_por/coinbase/edgar_10q_index.json` archived; per-quarter asset-class shares require iXBRL Note-5 parsing.
- **Kraken (Nexia SAB\&T semi-annual PoR)** · not yet joined.
- **Bankruptcy first-day motion PDFs** · not yet archived to `data/bankruptcy_dockets/`; case numbers documented in Table 1 caption. Public retrieval via kroll (Genesis: case23-10063.kroll.com, etc.).

## Compilation of the paper

```bash
cd manuscript && bash ../scripts/build.sh   # xelatex 3-pass + bibtex
```
