# crypto3 — Reproducibility archive for CEX Contagion (v2.1-t)

**Paper:** *Unlikely Intersections in Crypto Exchange Reserves: An O-Minimal Test for Systemic Risk*  
**Author:** Hongjun Gou (ICBC, Beijing 100140, China · `gouhongjun_bs@cq.icbc.com.cn`)  
**Status:** Under review (v2.1-t · Main.pdf 37 pages · 9-test replication audit 🟢 FULL PASS)

## What is here

| Directory / File | Purpose |
|---|---|
| `manuscript/Main.tex` | Main manuscript (LaTeX source) |
| `manuscript/Main.pdf` | Compiled PDF (37 pages, xelatex + bibtex) |
| `manuscript/refs.bib` | 34 references, DOI-verified |
| `manuscript/figures/fig{1..5}_*.pdf` | 5 canonical figures |
| `data/raw_por/` | DefiLlama on-chain reserve data (3 CEX × 1300+ days) |
| `data/raw_stablecoin_placebo/` | 10-issuer stablecoin panel |
| `data/raw/controls/btc_daily.csv` · `vix_daily.csv` | Yahoo Finance BTC-USD + VIX cache (SHA-256 pinned) |
| `data/bankruptcy_dockets/` | Chapter-11 docket references (Celsius/Voyager/FTX/BlockFi/Genesis) |
| `data/processed/` | 12 derived CSVs (all deterministic under `SOURCE_DATE_EPOCH=1755216000`) |
| `scripts/` | 18 production scripts + audit suite |
| `docs/` | Data charter, provenance, script-output registry |
| `run_all.sh` | Master pipeline (Stage 0 pull → Stage 10 compile) |
| `MANIFEST.sha256` | SHA-256 hashes of every artifact (33 files) |

## Reproduce every number in the paper

```bash
bash run_all.sh                    # full pipeline (~2 min on i7 + 16GB)
python scripts/_replication_final.py    # 9-test replication audit
```

Every number in `Main.pdf` is tied to a public Python script and a hash-locked raw data extract.  
Reproduction is **bit-identical** under `SOURCE_DATE_EPOCH=1755216000` (all figure PDFs + main PDF have deterministic SHA-256).

## Data provenance

All raw data are public:

- **DefiLlama** on-chain protocol data (`/protocol/binance-cex`, `/okx`, `/bybit`)
- **Yahoo Finance** BTC-USD daily close and VIX daily close (equivalent to FRED `VIXCLS`)
- **U.S. bankruptcy court dockets** (Kroll / Stretto)

No proprietary or confidential data are used. See `docs/data_provenance.md` for full source lineage.

## Prerequisites

- Python 3.9+ with `pandas 2.3.3`, `numpy 1.26.1`, `matplotlib 3.8.0`, `seaborn 0.13.2`
- MiKTeX or TeX Live with `xelatex` + `bibtex` (tested MiKTeX 25.12)
- Bash (Git Bash on Windows works)

## License

Code: MIT · Manuscript text: © 2026 Hongjun Gou (all rights reserved for publication)
