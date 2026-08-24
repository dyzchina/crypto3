"""
v2.0-q comprehensive figure/table numbering & cross-ref audit.

Extends _figtab_audit.py with two new checks:
 X1. Main-text vs appendix separation: figures/tables inside \appendix
     block should have a section-prefixed number (e.g. G.1), while
     main-text ones should have a plain number.
 X2. \includegraphics vs disk basename alignment: every included pdf
     path's basename fig{N}_* should match the LaTeX caption number.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import re
from pathlib import Path
from collections import defaultdict

BASE = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0")
TEX  = BASE / "manuscript" / "main_eca_v2.tex"
AUX  = BASE / "manuscript" / "main_eca_v2.aux"

with open(TEX, "rb") as f:
    c = f.read().decode("utf-8", errors="replace")
with open(AUX, "rb") as f:
    aux = f.read().decode("utf-8", errors="replace")

# Locate \appendix marker
appendix_pos = c.find("\\appendix")
if appendix_pos < 0:
    print("[WARN] no \\appendix found")

# ---- 1. Find every figure/table env with its position
env_pat = re.compile(r"\\begin\{(figure|table)\*?\}(.*?)\\end\{\1\*?\}", re.DOTALL)
blocks = []
for m in env_pat.finditer(c):
    env = m.group(1); body = m.group(2)
    lbl = re.search(r"\\label\{([^}]+)\}", body)
    inc = re.search(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body)
    start_line = c[:m.start()].count("\n") + 1
    in_appendix = m.start() > appendix_pos >= 0
    blocks.append({
        "env": env,
        "label": lbl.group(1) if lbl else None,
        "include": inc.group(1) if inc else None,
        "start_line": start_line,
        "in_appendix": in_appendix,
    })

# ---- 2. Extract label numbers from aux (\newlabel{key}{{NUM}{PAGE}...})
label_num = {}
for m in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^}]+)\}\{[^}]*\}", aux):
    label_num[m.group(1)] = m.group(2)

# ---- 3. Cross-check
print("=" * 78)
print("v2.0-q comprehensive figure/table audit")
print("=" * 78)
print(f"[appendix starts at line ~{c[:appendix_pos].count(chr(10))+1 if appendix_pos>=0 else '?'}]")
print()

print("--- FLOAT INVENTORY ---")
main_figs = [b for b in blocks if b["env"]=="figure" and not b["in_appendix"]]
app_figs  = [b for b in blocks if b["env"]=="figure" and b["in_appendix"]]
main_tabs = [b for b in blocks if b["env"]=="table"  and not b["in_appendix"]]
app_tabs  = [b for b in blocks if b["env"]=="table"  and b["in_appendix"]]

def show(bs, kind):
    print(f"  [{kind}] {len(bs)} entries")
    for b in bs:
        num = label_num.get(b["label"], "?")
        base = Path(b["include"]).name if b["include"] else "-"
        print(f"    L{b['start_line']:4d}  {b['env']:6s}  label={b['label']:32s}  numbered={num:6s}  file={base}")

show(main_figs, "main-text figures")
show(app_figs,  "appendix figures ")
show(main_tabs, "main-text tables ")
show(app_tabs,  "appendix tables  ")
print()

# ---- 4. Consistency issues
issues = []
for b in blocks:
    num = label_num.get(b["label"], None)
    if num is None:
        issues.append((b, "no number resolved in .aux (undefined reference?)"))
        continue
    # Main-text figures should be a plain integer; appendix should be A.N / B.N / ...
    if b["in_appendix"]:
        if not re.match(r"^[A-Z]\.\d+$", num):
            issues.append((b, f"in appendix but numbered '{num}' (expected letter.digit)"))
    else:
        if not re.match(r"^\d+$", num):
            issues.append((b, f"in main text but numbered '{num}' (expected plain integer)"))
    # X2: filename basename should match caption number IF main-text and figN_*
    if b["env"] == "figure" and b["include"]:
        base = Path(b["include"]).name
        m = re.match(r"fig(\d+)_", base)
        if m and re.match(r"^\d+$", num):
            file_n = int(m.group(1))
            cap_n = int(num)
            if file_n != cap_n:
                issues.append((b, f"file '{base}' vs caption number {num} mismatch"))

print("--- CONSISTENCY ISSUES ---")
if not issues:
    print("   ✓ 0 issues")
else:
    for b, msg in issues:
        print(f"   • L{b['start_line']}  {b['label']}: {msg}")
print()

# ---- 5. \ref-side check: every \ref{fig:...} / \ref{tab:...} shows sensible number
ref_pat = re.compile(r"\\(?:ref|Cref|autoref|cref)\{((?:fig|tab):[^}]+)\}")
ref_hits = defaultdict(list)
for i, line in enumerate(c.split("\n"), 1):
    for m in ref_pat.finditer(line):
        ref_hits[m.group(1)].append(i)

print("--- REFERENCE-SITE CHECK ---")
for k in sorted(ref_hits):
    num = label_num.get(k, "?")
    print(f"  {k:40s}  ->  displays as '{num}'   ({len(ref_hits[k])} refs)")
print()

# ---- 6. Sanity: how many figures/tables in main text vs appendix
print("--- STRUCTURAL SUMMARY ---")
print(f"  Main-text : {len(main_figs)} figures + {len(main_tabs)} tables")
print(f"  Appendix  : {len(app_figs)} figures + {len(app_tabs)} tables")
print()

# ---- Verdict
n = len(issues)
print("=" * 78)
if n == 0:
    print("VERDICT: 0 numbering/reference issues — audit clean.")
else:
    print(f"VERDICT: {n} issue(s) requiring review.")
print("=" * 78)
