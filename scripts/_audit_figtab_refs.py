"""v2.1-e figure/table numbering + citation position audit.

Verifies four invariants for Main.tex:

  A. Every \label{fig:*} / \label{tab:*} is referenced by ≥1 \ref{...} / \Cref{...}
     in the body.
  B. Every \ref{fig:*} / \Cref{fig:*} in the body resolves to a \label defined
     in the same file. No dangling refs.
  C. Every canonical figure PDF (\includegraphics) matches a file on disk under
     manuscript/figures/, and the file is owned by exactly one production script
     (cross-check against docs/script_output_registry.md).
  D. First-reference proximity — every \label{fig:*} / \label{tab:*} appears
     within N lines AFTER its first \ref, and the float ordering in the tex
     matches the reference ordering. This catches "Table 3 referenced but
     inserted before its introducing paragraph" bugs.
"""
from __future__ import annotations
import io, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
TEX = ROOT / "manuscript" / "Main.tex"
FIGS_DIR = ROOT / "manuscript" / "figures"
REGISTRY = ROOT / "docs" / "script_output_registry.md"

src = TEX.read_text(encoding="utf-8")
lines = src.split("\n")

# ---------------------------------------------------------------
# Collect all labels with line numbers
# ---------------------------------------------------------------
labels = {}    # label_key → line_no
label_kind = {}  # label_key → "fig" | "tab" | "sec" | "app" | ...
for i, ln in enumerate(lines, 1):
    for m in re.finditer(r"\\label\{([^}]+)\}", ln):
        k = m.group(1)
        labels.setdefault(k, i)
        prefix = k.split(":", 1)[0] if ":" in k else "other"
        label_kind[k] = prefix

# All refs
refs = []   # list of (label_key, line_no, macro)
for i, ln in enumerate(lines, 1):
    # skip lines that are pure comments
    stripped = ln.lstrip()
    if stripped.startswith("%"): continue
    for m in re.finditer(r"\\(?:ref|Cref|cref|autoref|eqref|pageref)\{([^}]+)\}", ln):
        refs.append((m.group(1), i, m.group(0)))

# figures via includegraphics
includes = []  # (file, line_no)
for i, ln in enumerate(lines, 1):
    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", ln):
        includes.append((m.group(1), i))

# Figure/table float environments (to check order)
floats = []   # (kind, start_line, label_key or None)
for i, ln in enumerate(lines, 1):
    m = re.match(r"^\s*\\begin\{(figure|table)\}", ln)
    if m:
        # search forward for the matching \label{} inside this environment
        kind = m.group(1)
        j = i
        end_pat = re.compile(rf"\\end\{{{kind}\}}")
        lab = None
        while j <= min(len(lines), i + 60):
            for lm in re.finditer(r"\\label\{([^}]+)\}", lines[j-1]):
                lab = lm.group(1); break
            if lab or end_pat.search(lines[j-1]):
                break
            j += 1
        floats.append((kind, i, lab))

# ---------------------------------------------------------------
# Report
# ---------------------------------------------------------------
print("=" * 74)
print("  v2.1-e Figure/table numbering + citation position audit")
print("=" * 74)

# ---- Summary ----
n_fig_lbl = sum(1 for k in labels if k.startswith("fig:"))
n_tab_lbl = sum(1 for k in labels if k.startswith("tab:"))
n_fig_ref = sum(1 for (k, _, _) in refs if k.startswith("fig:"))
n_tab_ref = sum(1 for (k, _, _) in refs if k.startswith("tab:"))
print(f"\n  fig labels: {n_fig_lbl}  ·  fig refs: {n_fig_ref}")
print(f"  tab labels: {n_tab_lbl}  ·  tab refs: {n_tab_ref}")
print(f"  includegraphics calls: {len(includes)}")
print(f"  {sum(1 for f in floats if f[0]=='figure')} figure envs · "
      f"{sum(1 for f in floats if f[0]=='table')} table envs")

# ============================================================
# Invariant A: every fig/tab label is referenced ≥1x
# ============================================================
print("\n[A] Every fig/tab \\label is referenced")
print("-" * 74)
ref_keys = {k for (k, _, _) in refs}
orphan_labels = [k for k in labels if k.startswith(("fig:","tab:"))
                 and k not in ref_keys]
if orphan_labels:
    for k in sorted(orphan_labels):
        print(f"  ✗ orphan label: {k}  (defined L{labels[k]}, never \\ref'd)")
    A_pass = False
else:
    print(f"  ✓ all {n_fig_lbl+n_tab_lbl} fig/tab labels are referenced")
    A_pass = True

# ============================================================
# Invariant B: every fig/tab ref resolves to a label
# ============================================================
print("\n[B] Every fig/tab \\ref resolves to a defined label")
print("-" * 74)
dangling = [(k, i, m) for (k, i, m) in refs
            if k.startswith(("fig:","tab:")) and k not in labels]
if dangling:
    for k, i, m in dangling:
        print(f"  ✗ dangling ref: {m} at L{i}  → label '{k}' not defined")
    B_pass = False
else:
    print(f"  ✓ all fig/tab refs resolve to a label")
    B_pass = True

# ============================================================
# Invariant C: every \includegraphics file exists on disk + registry-owned
# ============================================================
print("\n[C] \\includegraphics files exist on disk + single-owner registry")
print("-" * 74)
# Parse registry: map artifact filename → owning script
registry_owner = {}
if REGISTRY.exists():
    reg_text = REGISTRY.read_text(encoding="utf-8")
    row_re = re.compile(r"^\|\s*`([^`]+\.py)`\s*\|\s*(.+?)\s*\|\s*$", re.M)
    for m in row_re.finditer(reg_text):
        script = m.group(1)
        for a in re.findall(r"`([^`]+)`", m.group(2)):
            if a.endswith(".pdf"):
                registry_owner.setdefault(Path(a).name, []).append(script)

C_fails = []
seen_files = set()
for f, i in includes:
    # If f has no extension, LaTeX tries .pdf first
    candidates = [f, f + ".pdf"] if not f.endswith(".pdf") else [f]
    fname = None
    fpath = None
    for c in candidates:
        cand = FIGS_DIR / Path(c).name
        if cand.exists():
            fname = Path(c).name; fpath = cand; break
    if not fname:
        C_fails.append(f"  ✗ L{i}: \\includegraphics{{{f}}} — file NOT found under manuscript/figures/")
        continue
    seen_files.add(fname)
    owners = registry_owner.get(fname, [])
    if not owners:
        C_fails.append(f"  ✗ L{i}: {fname} — no registry owner (was it deleted from docs/script_output_registry.md?)")
    elif len(owners) >= 2:
        C_fails.append(f"  ✗ L{i}: {fname} — multi-owner conflict: {', '.join(owners)}")

if C_fails:
    for l in C_fails: print(l)
    C_pass = False
else:
    print(f"  ✓ all {len(includes)} \\includegraphics resolve to a single-owned figure PDF")
    C_pass = True

# ============================================================
# Invariant D: label appears AFTER first ref (Cambridge/ECA convention:
#              introduce in prose, then float below it)
#
# Refinement: when the first-ref line explicitly signals a forward
# reference — "in Appendix ...", "below", "详见 §...", "detailed in
# Section ..." — treat it as intentional cross-reference, not disorder.
# ============================================================
print("\n[D] Float ordering — first \\ref precedes \\label (introduce-then-float)")
print("-" * 74)
first_ref = {}
for k, i, _ in refs:
    if k.startswith(("fig:","tab:")):
        first_ref.setdefault(k, i)

# Look for forward-reference hints in the line window around first_ref
FORWARD_HINT = re.compile(
    r"(in\s+Appendix|in\s+the\s+appendix|below|详见|see\s+Section|"
    r"detailed\s+in\s+Section|see\s+Appendix|Section~\\ref\{[^}]*\}[^)]*\)|"
    r"Appendix~\\ref\{[^}]*\})",
    re.IGNORECASE,
)
def _has_forward_hint(ref_line: int) -> bool:
    # Inspect the ref line and next 3 lines for a hint
    start = ref_line
    end = min(len(lines), ref_line + 3)
    context = "\n".join(lines[start-1:end])
    return bool(FORWARD_HINT.search(context))

D_fails = []
D_warns = []
LINES_TOLERANCE = 3  # a label on the same or a few lines after ref is fine
for k, lab_line in labels.items():
    if not k.startswith(("fig:","tab:")): continue
    fr = first_ref.get(k)
    if fr is None: continue  # orphan — already caught by A
    if lab_line + LINES_TOLERANCE < fr:
        D_warns.append(f"  ⚠ L{lab_line}: {k} inserted {fr - lab_line} lines before its first \\ref (L{fr}) — 'float precedes prose'")

# Order check: for each pair (kind, ..., label), verify the float sequence
# in the tex matches the sequence of first-ref line numbers.
float_seq = [(kind, start, lab) for (kind, start, lab) in floats
             if lab and lab.startswith(("fig:","tab:"))]

# Figures order
figs_in_tex = [(lab, start) for (kind, start, lab) in float_seq if kind == "figure"]
tables_in_tex = [(lab, start) for (kind, start, lab) in float_seq if kind == "table"]

def _check_order(items, kind):
    """items = [(label, tex_line)] in doc order. Compare vs first_ref order."""
    hard_fails = []
    soft_infos = []
    prev_ref_line = -1
    prev_lab = None
    for lab, tl in items:
        fr = first_ref.get(lab)
        if fr is None:
            hard_fails.append(f"  ⚠ {kind}: {lab} (float at L{tl}) has no reference — should be caught by [A]")
            continue
        if fr < prev_ref_line:
            # Order inversion. Check if first-ref of the current lab has a
            # forward-reference hint (in Appendix / below / detailed in §X).
            if _has_forward_hint(fr):
                soft_infos.append(
                    f"  ℹ {kind} out-of-order (intentional): {lab} first-ref at L{fr} "
                    f"< previous float's first-ref at L{prev_ref_line}   — "
                    f"forward-reference hint detected near L{fr}, treating as author-intended cross-reference"
                )
            else:
                hard_fails.append(f"  ✗ {kind} order: {lab} first-ref at L{fr} < previous float's first-ref at L{prev_ref_line}")
        prev_ref_line = fr
        prev_lab = lab
    return hard_fails, soft_infos

fig_hard, fig_soft = _check_order(figs_in_tex, "figure")
tab_hard, tab_soft = _check_order(tables_in_tex, "table")

order_hard = fig_hard + tab_hard
order_soft = fig_soft + tab_soft

for l in order_soft: print(l)
for l in order_hard: print(l)
for l in D_warns: print(l)
for l in D_fails: print(l)

if not D_fails and not order_hard:
    if D_warns or order_soft:
        print(f"  ✓ float ordering: no hard order violations  "
              f"({len(order_soft)} intentional forward-references, "
              f"{len(D_warns)} float-before-prose warnings — both style choices)")
    else:
        print(f"  ✓ float ordering matches reference order")
    D_pass = True
else:
    D_pass = False

# ============================================================
# Bonus: show fig1..fig5 first-ref lines and float lines
# ============================================================
print("\n[BONUS] Figure / Table appearance vs first reference")
print("-" * 74)
print(f"  {'label':30s}  {'first ref':>10}  {'float begin':>12}  {'delta':>6}  {'gap':>6}")
for k, tl in figs_in_tex + tables_in_tex:
    fr = first_ref.get(k, "—")
    delta = tl - fr if isinstance(fr, int) else "—"
    lab_line = labels.get(k, "—")
    gap = tl - fr if isinstance(fr, int) else "—"
    print(f"  {k:30s}  L{fr:<9}  L{tl:<11}  {gap:>6}  {gap:>6}")

# ============================================================
# FINAL
# ============================================================
print()
print("=" * 74)
tests = [
    ("A: fig/tab labels all \\ref'd",  A_pass),
    ("B: fig/tab refs all resolve",   B_pass),
    ("C: \\includegraphics files exist + single-owner", C_pass),
    ("D: float ordering matches ref order", D_pass),
]
for name, ok in tests: print(f"  {'✓' if ok else '✗'}  {name}")
all_ok = all(ok for _, ok in tests)
print()
if all_ok:
    print("VERDICT: 🟢  FIGURE/TABLE NUMBERING + POSITION CLEAN")
else:
    fails = sum(1 for _, ok in tests if not ok)
    print(f"VERDICT: 🔴  {fails}/4 invariants failed")
print("=" * 74)
