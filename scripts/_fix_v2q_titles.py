"""
v2.0-q figure titling cleanup + regeneration.

Problem:
  Three figure-generating scripts hardcode 'Figure N. ...' in
  fig.suptitle(). After the v2.0-p rename (fig2<->fig3<->fig4 disk names),
  those hardcoded numbers now MISMATCH the LaTeX caption numbers:
    fig2_share_trajectories.pdf     : shows "Figure 3." in title
    fig3_empirical_frontier.pdf     : shows "Figure 4." in title
    fig4_event_timeline.pdf         : shows "Figure 2." in title

Fix: drop the "Figure N. " prefix from every suptitle (the title text
kept as a short descriptor, no number), so the LaTeX caption is the
single source of truth for the figure number.

Then regenerate the three PDFs.
"""
import subprocess, sys
from pathlib import Path

BASE = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
SCRIPTS = BASE / "scripts"

PATCHES = [
    # (script, old_snippet, new_snippet)
    (
        SCRIPTS / "figure_01_v04.py",
        'fig.suptitle("Figure 3. Reserve-share trajectories 2022-Q4 to 2025-Q4 "\n'
        '             "(on-chain composition, DefiLlama)", fontsize=10.5, y=1.02)',
        'fig.suptitle("Reserve-share trajectories 2022-Q4 to 2025-Q4 "\n'
        '             "(on-chain composition, DefiLlama)", fontsize=10.5, y=1.02)',
    ),
    (
        SCRIPTS / "fig4_v2_dual_threshold.py",
        'fig.suptitle(r"Figure 4. Empirical $k$-fold intersection counts vs.\\ "\n'
        '             r"polylog prior under two threshold specifications",\n'
        '             fontsize=11, y=1.00)',
        'fig.suptitle(r"Empirical $k$-fold intersection counts vs.\\ "\n'
        '             r"polylog prior under two threshold specifications",\n'
        '             fontsize=11, y=1.00)',
    ),
    (
        SCRIPTS / "estimator_nk.py",
        'fig.suptitle("Figure 4. Empirical $k$-fold intersection counts vs.\\\\ "\n'
        '             "polylog prior, 3-venue panel 2022-Q4 to 2025-Q4",\n'
        '             fontsize=10.5, y=1.02)',
        'fig.suptitle("Empirical $k$-fold intersection counts vs.\\\\ "\n'
        '             "polylog prior, 3-venue panel 2022-Q4 to 2025-Q4",\n'
        '             fontsize=10.5, y=1.02)',
    ),
]

def patch(path: Path, old: str, new: str) -> bool:
    txt = path.read_text(encoding="utf-8")
    if old not in txt:
        print(f"[SKIP] {path.name}: pattern not found (already patched?)")
        return False
    path.write_text(txt.replace(old, new), encoding="utf-8")
    print(f"[PATCH] {path.name}: title stripped of 'Figure N. ' prefix")
    return True

for path, old, new in PATCHES:
    patch(path, old, new)
