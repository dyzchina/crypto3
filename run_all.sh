#!/usr/bin/env bash
# =========================================================================
# run_all.sh — Master replication script for cex_contagion_v2.0
# =========================================================================
# Reproduces every table, figure, and reported number in Main.pdf
# from the raw JSON data archived under data/raw_por/ and
# data/raw_stablecoin_placebo/.
#
# Prerequisites (see requirements.txt and README.md):
#   - Python 3.9+ with pandas 2.3.3, numpy 1.26.1, matplotlib 3.8.0, seaborn 0.13.2
#   - MiKTeX / TeX Live with xelatex + bibtex (tested MiKTeX 25.12)
#
# Usage:
#   bash run_all.sh                # full pipeline
#   bash run_all.sh --skip-figs    # skip figure regeneration
#   bash run_all.sh --skip-pdf     # skip LaTeX compile
#
# Expected runtime on Windows 11 / Intel i7 / 16 GB RAM: ~2 minutes total.
# =========================================================================

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

SKIP_FIGS=0
SKIP_PDF=0
for arg in "$@"; do
  case "$arg" in
    --skip-figs) SKIP_FIGS=1 ;;
    --skip-pdf)  SKIP_PDF=1 ;;
    *) echo "unknown arg: $arg"; exit 2 ;;
  esac
done

log() { printf "\n\033[1;34m[run_all]\033[0m %s\n" "$*"; }

export PYTHONIOENCODING=utf-8

# ------------------------------------------------------------------------
# Reproducible-builds: pin timestamp used inside matplotlib PDF metadata
# and inside xelatex-generated PDF /CreationDate + /ID.  This makes
# figures/ and manuscript/Main.pdf byte-identical across
# runs (SHA-256 stable).  The date is fixed to 2026-08-15, the domain-
# prior threshold pre-commit date recorded in docs/data_charter.md.
# ------------------------------------------------------------------------
export SOURCE_DATE_EPOCH=1755216000    # 2026-08-15 00:00:00 UTC

# -------------------------------------------------------------------------
# Stage 1 · Aggregate raw JSON → processed CSV
# -------------------------------------------------------------------------
log "Stage 1 · aggregating raw CEX JSON → cex_por_snapshots_wide.csv"
python scripts/aggregate_por.py

log "Stage 2 · estimator_nk.py → nk_estimates.csv"
python scripts/estimator_nk.py

log "Stage 3 · did_regression.py → did_estimates.csv + robustness_grid.csv + pooling_gain.csv + rank_check.txt"
python scripts/did_regression.py

log "Stage 3b · did_controls.py → did_controls.csv (v2.0-u BTC+VIX additive controls)"
python scripts/did_controls.py

log "Stage 4 · wild_bootstrap.py → wild_bootstrap.csv (B=9999 Rademacher)"
python scripts/wild_bootstrap.py

log "Stage 5 · loo_headline.py → LOO robustness readout"
python scripts/loo_headline.py

log "Stage 6 · anticipation_did.py → anticipation_did.csv (Grayscale 2023-08 secondary)"
python scripts/anticipation_did.py

log "Stage 7 · stablecoin_placebo_did.py → 10-issuer placebo panel + DiD"
python scripts/stablecoin_placebo_did.py

log "Stage 7b · beta_estimate.py → persistence-exponent β̂ from log-log ACF"
python scripts/beta_estimate.py

# -------------------------------------------------------------------------
# Stage 8 · Figures
# -------------------------------------------------------------------------
if [ "$SKIP_FIGS" -eq 0 ]; then
  log "Stage 8a · figure_01_v04.py → Fig 1 heatmap + Fig 3 share trajectories"
  python scripts/figure_01_v04.py

  log "Stage 8b · fig_event_timeline.py → Fig 2 event timeline"
  python scripts/fig_event_timeline.py

  log "Stage 8c · fig4_v2_dual_threshold.py → Fig 4 dual-panel Nk vs prior"
  python scripts/fig4_v2_dual_threshold.py

  log "Stage 8d · build_fig5_algorithm.py → Fig A.1 Algorithm flowchart"
  python scripts/build_fig5_algorithm.py
else
  log "Stage 8 skipped (--skip-figs)"
fi

# -------------------------------------------------------------------------
# Stage 9 · Manifest
# -------------------------------------------------------------------------
log "Stage 9 · build_manifest.py → MANIFEST.sha256 + docs/data_provenance.md"
python scripts/build_manifest.py

# -------------------------------------------------------------------------
# Stage 10 · LaTeX compile (xelatex 3-pass + bibtex)
# -------------------------------------------------------------------------
if [ "$SKIP_PDF" -eq 0 ]; then
  log "Stage 10 · xelatex pass 1"
  ( cd manuscript && xelatex -interaction=nonstopmode -halt-on-error Main.tex >/dev/null )
  log "Stage 10 · bibtex"
  ( cd manuscript && bibtex Main >/dev/null )
  log "Stage 10 · xelatex pass 2"
  ( cd manuscript && xelatex -interaction=nonstopmode -halt-on-error Main.tex >/dev/null )
  log "Stage 10 · xelatex pass 3"
  ( cd manuscript && xelatex -interaction=nonstopmode -halt-on-error Main.tex >/dev/null )

  # Health check
  n_undef=$(grep -c "undefined" manuscript/Main.log || true)
  n_err=$(grep -c "^! " manuscript/Main.log || true)
  pages=$(grep -oE "([0-9]+) pages" manuscript/Main.log | tail -1 | awk '{print $1}')
  log "PDF built: manuscript/Main.pdf  · $pages pages  · undef=$n_undef  · errors=$n_err"
else
  log "Stage 10 skipped (--skip-pdf)"
fi

log "All stages complete. Sanity: compare manuscript/Main.pdf against docs/data_provenance.md."
