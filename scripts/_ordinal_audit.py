"""
v2.0-s Deep human-eye audit: ordinal consistency check.

For each float, check that its LaTeX-assigned NUMBER matches the position
in the FIRST-REF sequence. E.g. the float that is referenced first in the
manuscript should be Figure/Table 1, the second first-ref should be
Figure/Table 2, etc.

Also check that the CAPTION text on each figure/table doesn't accidentally
reference a stale number (e.g. "as shown in Figure 3" inside Figure 2's
caption).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import re
from pathlib import Path

BASE = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
TEX  = BASE / "manuscript" / "main_eca_v2.tex"
AUX  = BASE / "manuscript" / "main_eca_v2.aux"

with open(TEX, "rb") as f:
    c = f.read().decode("utf-8", errors="replace")
with open(AUX, "rb") as f:
    aux = f.read().decode("utf-8", errors="replace")

lines = c.split("\n")

# ---- Extract label numbers
label_num = {}
for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{[^}]*\}", aux):
    label_num[m.group(1)] = m.group(2)

# ---- Extract every float with its label
env_pat = re.compile(r"\\begin\{(figure|table)\*?\}(.*?)\\end\{\1\*?\}", re.DOTALL)
float_ranges = []
label_env = {}
for m in env_pat.finditer(c):
    body = m.group(2)
    env = m.group(1)
    lbl = re.search(r"\\label\{([^}]+)\}", body)
    if lbl:
        label_env[lbl.group(1)] = env
        float_ranges.append((c[:m.start()].count("\n") + 1,
                             c[:m.end()].count("\n") + 1,
                             lbl.group(1)))

def in_float(i):
    return any(a <= i <= b for a, b, _ in float_ranges)

# ---- First prose ref per label
first_ref = {}
for i, line in enumerate(lines, 1):
    if in_float(i):
        continue
    for m in re.finditer(r"\\(?:ref|Cref|autoref|cref)\{((?:fig|tab):[^}]+)\}", line):
        k = m.group(1)
        if k not in first_ref:
            first_ref[k] = i

# ---- Ordinal check: sort labels by first-ref line, expected number = index+1
figs = [k for k in first_ref if k.startswith("fig:") and not label_num.get(k,"").startswith("A")]
tabs = [k for k in first_ref if k.startswith("tab:") and not label_num.get(k,"").startswith("A")]

figs.sort(key=lambda k: first_ref[k])
tabs.sort(key=lambda k: first_ref[k])

print("=" * 80)
print("v2.0-s ordinal-consistency audit (first-ref order == assigned number)")
print("=" * 80)
print()
issues = []

def check(items, kind):
    print(f"[{kind}]")
    for idx, k in enumerate(items, 1):
        n = label_num.get(k, "?")
        ok = n == str(idx)
        mark = "✓" if ok else "❌"
        print(f"  {mark}  first-ref L{first_ref[k]:>4d}  {k:38s}  numbered={n}  expected={idx}")
        if not ok:
            issues.append((k, n, idx))

check(figs, "Main-text figures")
check(tabs, "Main-text tables")

# Appendix figs
appfigs = [k for k in first_ref if k.startswith("fig:") and label_num.get(k,"").startswith("A")]
appfigs.sort(key=lambda k: first_ref[k])
print("[Appendix figures]")
for idx, k in enumerate(appfigs, 1):
    n = label_num.get(k, "?")
    exp = f"A.{idx}"
    ok = n == exp
    mark = "✓" if ok else "❌"
    print(f"  {mark}  first-ref L{first_ref[k]:>4d}  {k:38s}  numbered={n}  expected={exp}")
    if not ok:
        issues.append((k, n, exp))

print()

# ---- Caption stale-number scan
print("--- Caption stale-number scan ---")
stale = []
for a, b, lbl in float_ranges:
    body = "\n".join(lines[a-1:b])
    for m in re.finditer(r"\b(Figure|Fig\.|Table|Tab\.)\s*(\d+)\b", body):
        # This is a hardcoded Figure/Table NUMBER inside a caption body!
        stale.append((lbl, m.group(0), a))
if not stale:
    print("  ✓ no hardcoded 'Figure N' or 'Table N' inside any caption body")
else:
    for lbl, txt, ln in stale:
        print(f"  ❌  {lbl} caption (start L{ln}) contains literal '{txt}' — should use \\ref")

print()

# ---- Verdict
n_issues = len(issues) + len(stale)
print("=" * 80)
if n_issues == 0:
    print("VERDICT: ordinal + caption audit CLEAN.")
else:
    print(f"VERDICT: {n_issues} issue(s).")
print("=" * 80)
