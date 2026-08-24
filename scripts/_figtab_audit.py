"""
v2.0-p figure/table numbering & cross-reference audit.

Checks:
 F1. Every figure/table has a \label and a \caption.
 F2. Every \label{fig:...} / \label{tab:...} is referenced ≥ 1 times.
 F3. Every \ref{fig:...} / \ref{tab:...} resolves to a defined label.
 F4. Every \includegraphics file exists on disk.
 F5. Prefix consistency: figure→fig:, table→tab:.
 F6. Numbering order matches appearance order (Fig 1..N by position).
 F7. All Figure/Table Roman numerals in prose (Figure 1, Table 3) actually
     match their label references (no "Figure~1" typed literally instead of
     using \ref{fig:foo}).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import re
from pathlib import Path
from collections import defaultdict

BASE = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
TEX  = BASE / "manuscript" / "main_eca_v2.tex"
with open(TEX, "rb") as f:
    c = f.read().decode("utf-8", errors="replace")

lines = c.split("\n")

# ---- 1. Find every figure/table environment
env_blocks = []  # list of (env, start_line, end_line, body)
env_pat = re.compile(
    r"\\begin\{(figure|table)\*?\}(.*?)\\end\{\1\*?\}",
    re.DOTALL,
)
for m in env_pat.finditer(c):
    env = m.group(1)
    body = m.group(2)
    start_line = c[:m.start()].count("\n") + 1
    end_line = c[:m.end()].count("\n") + 1
    env_blocks.append((env, start_line, end_line, body))

# ---- 2. For each block, extract label + caption + includegraphics
fig_records = []
tab_records = []
for env, sL, eL, body in env_blocks:
    lbl = re.search(r"\\label\{([^}]+)\}", body)
    cap = re.search(r"\\caption(?:\[[^\]]*\])?\{", body)
    figs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body)
    rec = {
        "env": env,
        "start": sL,
        "end": eL,
        "label": lbl.group(1) if lbl else None,
        "has_caption": bool(cap),
        "includes": figs,
    }
    (fig_records if env == "figure" else tab_records).append(rec)

# ---- 3. All labels of fig:/tab: prefix
all_labels = {}
for i, line in enumerate(lines, 1):
    for m in re.finditer(r"\\label\{(fig:[^}]+|tab:[^}]+)\}", line):
        all_labels[m.group(1)] = i

# ---- 4. All references to fig:/tab:
refs = defaultdict(list)  # key -> [(line_no, kind)]
for i, line in enumerate(lines, 1):
    for m in re.finditer(r"\\(ref|Cref|autoref|cref)\{([^}]+)\}", line):
        kind = m.group(1)
        for k in m.group(2).split(","):
            k = k.strip()
            if k.startswith(("fig:", "tab:")):
                refs[k].append((i, kind))

# ---- 5. Literal "Figure N" / "Table N" in prose (potentially wrong style)
literal_hits = []
for i, line in enumerate(lines, 1):
    # Match "Figure~1", "Figure 1", "Fig. 1", "Table 3", "Table~2"
    # but skip lines that also contain a \ref or \Cref
    if "\\ref{" in line or "\\Cref{" in line or "\\autoref{" in line:
        continue
    if "\\caption" in line or "\\includegraphics" in line:
        continue
    for m in re.finditer(r"\b(Figure|Fig\.|Table)~?(\d+)\b", line):
        literal_hits.append((i, m.group(0)))

# ---- 6. Includegraphics files existence on disk
FIGURES_DIR = BASE / "manuscript" / "figures"
missing_files = []
included_files = set()
for r in fig_records:
    for inc in r["includes"]:
        included_files.add(inc)
        # Try several suffixes
        p = FIGURES_DIR / inc
        candidates = [p, p.with_suffix(".pdf"), p.with_suffix(".eps"),
                      p.with_suffix(".png"), p.with_suffix(".jpg")]
        # Also relative to manuscript folder
        candidates += [
            BASE / "manuscript" / inc,
            (BASE / "manuscript" / inc).with_suffix(".pdf"),
        ]
        if not any(cc.exists() for cc in candidates):
            missing_files.append((r["start"], inc))

# ---- 7. Missing refs (referenced but no label)
missing_refs = sorted(set(refs.keys()) - set(all_labels.keys()))
orphan_labels = sorted(set(all_labels.keys()) - set(refs.keys()))

# ---- 8. Prefix consistency
prefix_mismatch = []
for r in fig_records:
    if r["label"] and not r["label"].startswith("fig:"):
        prefix_mismatch.append((r["start"], "figure", r["label"]))
for r in tab_records:
    if r["label"] and not r["label"].startswith("tab:"):
        prefix_mismatch.append((r["start"], "table", r["label"]))

# ---- 9. Missing caption or label
missing_label = []
missing_caption = []
for r in fig_records + tab_records:
    if not r["label"]:
        missing_label.append((r["start"], r["env"]))
    if not r["has_caption"]:
        missing_caption.append((r["start"], r["env"]))

# ---- 10. Ordering: figure labels should appear in numerical order fig1, fig2, ...
def order_key(rec):
    return rec["start"]

def sort_and_check_order(records, prefix):
    sorted_by_pos = sorted(records, key=order_key)
    order_issues = []
    for expected_idx, rec in enumerate(sorted_by_pos, 1):
        if rec["label"] is None:
            continue
        # Extract trailing digit if the label follows fig:N_* or fig:figN_* pattern
        m = re.match(rf"{prefix}(\d+)", rec["label"])
        if m:
            actual = int(m.group(1))
            if actual != expected_idx:
                order_issues.append((rec["start"], rec["label"],
                                     f"appears as #{expected_idx} but labelled {actual}"))
    return order_issues

fig_order_issues = sort_and_check_order(fig_records, r"fig:fig")
if not fig_order_issues:
    fig_order_issues = sort_and_check_order(fig_records, r"fig:")

# ---- Report
def section(title, items, formatter=str):
    print(f"--- {title} ({len(items)}) ---")
    if not items:
        print("   ✓ clean")
    else:
        for x in items[:30]:
            print(f"   • {formatter(x)}")
        if len(items) > 30:
            print(f"   ... (+{len(items)-30} more)")
    print()

print("=" * 70)
print("v2.0-p Figure/Table numbering & cross-reference audit")
print("=" * 70)
print()
print(f"[FIGURES] {len(fig_records)} \\begin{{figure}} blocks")
print(f"[TABLES]  {len(tab_records)} \\begin{{table}} blocks")
print(f"[LABELS]  {len(all_labels)} fig:/tab: labels total")
print(f"[REFS]    {len(refs)} unique keys referenced "
      f"({sum(len(v) for v in refs.values())} total ref sites)")
print(f"[FILES]   {len(included_files)} unique \\includegraphics targets")
print()

section("Missing label", missing_label,
        lambda t: f"L{t[0]}  \\begin{{{t[1]}}} has no \\label")

section("Missing caption", missing_caption,
        lambda t: f"L{t[0]}  \\begin{{{t[1]}}} has no \\caption")

section("Missing references (referenced but not defined)", missing_refs)

section("Orphan labels (defined but not referenced)", orphan_labels)

section("Prefix mismatch (figure→fig:, table→tab:)", prefix_mismatch,
        lambda t: f"L{t[0]}  <{t[1]}>  \\label{{{t[2]}}}")

section("\\includegraphics file missing on disk", missing_files,
        lambda t: f"L{t[0]}  {t[1]}")

section("Figure numbering out of order (fig1, fig2, ... vs position)",
        fig_order_issues,
        lambda t: f"L{t[0]}  \\label{{{t[1]}}}  {t[2]}")

section("Literal 'Figure N' / 'Table N' in prose (should be \\ref)",
        literal_hits,
        lambda t: f"L{t[0]}  '{t[1]}'")

# ---- Inventory table
print("--- FIGURE inventory (position order) ---")
for r in sorted(fig_records, key=order_key):
    lbl = r["label"] or "<no label>"
    n_refs = len(refs.get(r["label"] or "", []))
    files = ", ".join(r["includes"])
    print(f"  L{r['start']:4d}  \\label{{{lbl}}}  refs={n_refs}  files=[{files}]")
print()

print("--- TABLE inventory (position order) ---")
for r in sorted(tab_records, key=order_key):
    lbl = r["label"] or "<no label>"
    n_refs = len(refs.get(r["label"] or "", []))
    print(f"  L{r['start']:4d}  \\label{{{lbl}}}  refs={n_refs}")
print()

# ---- Verdict
n_bad = (len(missing_label) + len(missing_caption) + len(missing_refs)
         + len(orphan_labels) + len(prefix_mismatch) + len(missing_files)
         + len(fig_order_issues) + len(literal_hits))
print("=" * 70)
if n_bad == 0:
    print("VERDICT: 0 bugs — figure/table numbering & cross-refs are clean.")
else:
    print(f"VERDICT: {n_bad} issue(s) requiring review.")
print("=" * 70)
