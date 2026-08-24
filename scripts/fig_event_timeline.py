"""fig_event_timeline.py -- Fig 4 (Distress-cluster timeline) for v2.0.

Standalone rebuilds `figures/fig4_event_timeline.pdf` without any hardcoded
'Figure N' prefix; the LaTeX caption is the single source of truth for
figure numbering.

Copied and de-duplicated from v0.1 figure_01_02.py; only the timeline
portion is retained.
"""
import os
import datetime as dt
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch

BASE = Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root
OUT = BASE / "manuscript" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

events = [
    ("Terra/UST collapse",   "2022-05-09"),
    ("Celsius freeze",       "2022-06-13"),
    ("Voyager Chapter 11",   "2022-07-05"),
    ("FTX collapse (RDD)",   "2022-11-11"),
    ("BlockFi Chapter 11",   "2022-11-28"),
    ("Genesis Chapter 11",   "2023-01-19"),
]

def parse(s):
    return dt.datetime.strptime(s, "%Y-%m-%d")

dates = [parse(d) for _, d in events]
labels = [e for e, _ in events]

x_start = parse("2022-04-01")
x_end   = parse("2023-04-01")

fig, ax = plt.subplots(figsize=(7.6, 3.4))

# Shaded RDD window around FTX +/- 60 days
ftx = parse("2022-11-11")
w_lo = ftx - dt.timedelta(days=60)
w_hi = ftx + dt.timedelta(days=60)
ax.axvspan(w_lo, w_hi, ymin=0.05, ymax=0.95, color="orange", alpha=0.15,
           label="FTX RDD window ($\\pm 60$ d)")

# Event lollipops
levels = [1.0, 0.6, 1.0, 1.4, 0.7, 1.0]
for d, lab, y in zip(dates, labels, levels):
    ax.vlines(d, 0, y, color="darkred", lw=1.2)
    ax.plot([d], [y], marker="o", color="darkred", markersize=6)
    ax.annotate(lab, xy=(d, y),
                xytext=(0, 8), textcoords="offset points",
                ha="center", fontsize=8, rotation=25)

# Baseline + axes
ax.axhline(0, color="gray", lw=0.6)
ax.set_ylim(-0.2, 2.0)
ax.set_xlim(x_start, x_end)
ax.set_yticks([])
ax.set_xlabel("Date", fontsize=9)
# NB: no suptitle / no "Figure N" text; LaTeX caption owns the numbering.

# Legend for the shaded RDD strip
handles = [Patch(facecolor="orange", alpha=0.15,
                 label="FTX RDD window ($\\pm 60$ d)")]
ax.legend(handles=handles, loc="upper left", fontsize=8, framealpha=0.9)

# Month ticks
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)

plt.tight_layout()
p = OUT / "fig2_event_timeline.pdf"
plt.savefig(p, bbox_inches="tight")
plt.close()
print(f"[OK] {p}")
