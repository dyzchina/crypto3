"""
Fig 5 · Algorithm flowchart — v2 layout (readable).
Fixes: super-title + step subtitles overlap. Widen canvas,
push super-title up, drop subtitles down, shrink to fit.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

OUT = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/figures/fig5_algorithm_flowchart.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

STEEL = "#4682B4"
FIRE  = "#B22222"
GREY  = "#606060"
LIGHT = "#F2F2F2"

# Taller canvas + explicit gridspec so title has vertical breathing room.
fig = plt.figure(figsize=(13.5, 5.6))
gs  = fig.add_gridspec(nrows=1, ncols=3,
                       left=0.03, right=0.98,
                       bottom=0.08, top=0.80,   # top pushed down → suptitle room
                       wspace=0.22)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])

TITLE_FS  = 12.5    # step subtitle
BODY_FS   = 11
SMALL_FS  = 10

# ---------- Step 1: dyadic partition ----------
ax = ax1
ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
ax.set_aspect("equal"); ax.axis("off")
ax.text(0.5, 1.10, "Step 1", ha="center", va="bottom",
        fontsize=TITLE_FS, fontweight="bold")
ax.text(0.5, 1.02, "Dyadic partition of reserve-simplex product",
        ha="center", va="bottom", fontsize=BODY_FS, color=GREY)

ax.add_patch(Rectangle((0.05, 0.05), 0.9, 0.85, fill=False,
                       ec="black", lw=1.6))
ax.text(0.5, 0.955, r"$\mathcal{X}_H \subset \mathbb{R}^{3n}$",
        ha="center", va="top", fontsize=BODY_FS)
n = 6
for i in range(1, n):
    x = 0.05 + 0.9 * i / n
    ax.plot([x, x], [0.05, 0.9], color=GREY, lw=0.6, alpha=0.5)
    y = 0.05 + 0.85 * i / n
    ax.plot([0.05, 0.95], [y, y], color=GREY, lw=0.6, alpha=0.5)
xh = 0.05 + 0.9 * 2 / n; yh = 0.05 + 0.85 * 3 / n
ax.add_patch(Rectangle((xh, yh), 0.9 / n, 0.85 / n,
                       facecolor=STEEL, alpha=0.4,
                       edgecolor=STEEL, lw=1.5))
ax.text(xh + 0.9/n/2, yh + 0.85/n/2, r"$\tau_c$",
        ha="center", va="center", fontsize=BODY_FS)
ax.text(0.5, -0.05, r"cell width $\sim R^{-1/2}$",
        ha="center", va="top", fontsize=SMALL_FS, color=GREY)

# ---------- Step 2: cell-wise Pila-Wilkie count ----------
ax = ax2
ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
ax.set_aspect("equal"); ax.axis("off")
ax.text(0.5, 1.10, "Step 2", ha="center", va="bottom",
        fontsize=TITLE_FS, fontweight="bold")
ax.text(0.5, 1.02, r"Cell-wise Pila--Wilkie count on $\tau_c$",
        ha="center", va="bottom", fontsize=BODY_FS, color=GREY)

ax.add_patch(Rectangle((0.15, 0.20), 0.70, 0.60,
                       facecolor=LIGHT, edgecolor=STEEL, lw=2))
ax.text(0.5, 0.83, r"$\tau_c$ (enlarged)",
        ha="center", va="bottom", fontsize=BODY_FS)

rng = np.random.default_rng(7)
xs = rng.uniform(0.20, 0.80, 10)
ys = 0.35 + 0.30 * np.sin(6 * xs) * 0.6 + rng.normal(0, 0.02, 10)
ax.plot(xs, ys, "o", color=FIRE, ms=6, zorder=5)
xc = np.linspace(0.18, 0.82, 200)
yc = 0.35 + 0.30 * np.sin(6 * xc) * 0.6
ax.plot(xc, yc, "-", color=STEEL, lw=1.3, alpha=0.75, zorder=4)

ax.text(0.5, 0.08,
        r"$\hat C_c = \mathrm{PW}_{\tau_c}(\mathcal{P}_c)"
        r"\ \lesssim\ c_\varepsilon\, H^\varepsilon$",
        ha="center", va="center", fontsize=BODY_FS + 0.5, color=FIRE)

# ---------- Step 3: l^p composition ----------
ax = ax3
ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
ax.set_aspect("equal"); ax.axis("off")
ax.text(0.5, 1.10, "Step 3", ha="center", va="bottom",
        fontsize=TITLE_FS, fontweight="bold")
ax.text(0.5, 1.02, r"$\ell^{p}$ composition via counting inequality",
        ha="center", va="bottom", fontsize=BODY_FS, color=GREY)

for i, y in enumerate([0.82, 0.62, 0.42]):
    ax.add_patch(FancyBboxPatch((0.05, y - 0.06), 0.28, 0.12,
                                boxstyle="round,pad=0.02",
                                facecolor=STEEL, alpha=0.25,
                                edgecolor=STEEL, lw=1.2))
    ax.text(0.19, y, rf"$\hat C_{i+1}$", ha="center", va="center",
            fontsize=BODY_FS + 1)
    arr = FancyArrowPatch((0.34, y), (0.60, 0.62),
                          arrowstyle="->", lw=1.3, color=GREY,
                          mutation_scale=13)
    ax.add_patch(arr)

ax.add_patch(FancyBboxPatch((0.60, 0.48), 0.35, 0.28,
                            boxstyle="round,pad=0.02",
                            facecolor=FIRE, alpha=0.28,
                            edgecolor=FIRE, lw=1.6))
ax.text(0.775, 0.62, r"$\hat N_k$",
        ha="center", va="center", fontsize=15, fontweight="bold")

ax.text(0.5, 0.22,
        r"$\hat N_k = \left(\sum_c \|\hat\sigma_c\|_{L^p}^p\right)^{1/p}"
        r"\!\cdot D(R, p, \varepsilon)$",
        ha="center", va="center", fontsize=BODY_FS + 0.5)
ax.text(0.5, 0.09, r"$D = O(R^{\varepsilon})$",
        ha="center", va="center", fontsize=SMALL_FS + 0.5, color=GREY)

# ---------- overall super-title, single line, well above panels ----------
fig.suptitle(
    r"Count estimator of $k$-fold intersections on the reserve-simplex product",
    fontsize=14, fontweight="bold", y=0.965)

plt.savefig(OUT, format="pdf", dpi=300, bbox_inches="tight")
plt.close()
print(f"[write] {OUT}")
print(f"[size] {OUT.stat().st_size:,} bytes")
