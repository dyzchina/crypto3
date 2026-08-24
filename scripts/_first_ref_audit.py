"""
v2.0-r deep audit: does every figure/table appear immediately AFTER its
FIRST textual reference site? Reviewer expectation:

  ... paragraph mentions Figure N for the first time ...
  \begin{figure}[H] ... Figure N ... \end{figure}

Reports for every label:
  - first ref line
  - float line
  - float BEFORE first ref (BAD)
  - float FAR AFTER first ref (BAD if > K lines with no intervening \ref)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import re
from pathlib import Path

TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")
with open(TEX, "rb") as f:
    c = f.read().decode("utf-8", errors="replace")

lines = c.split("\n")

# ---- 1. Find every figure/table env with its label
env_pat = re.compile(r"\\begin\{(figure|table)\*?\}(.*?)\\end\{\1\*?\}", re.DOTALL)
float_line = {}     # label -> start_line of float
float_env  = {}     # label -> env kind
for m in env_pat.finditer(c):
    env = m.group(1); body = m.group(2)
    lbl = re.search(r"\\label\{([^}]+)\}", body)
    if lbl:
        sL = c[:m.start()].count("\n") + 1
        float_line[lbl.group(1)] = sL
        float_env[lbl.group(1)] = env

# ---- 2. Find every \ref{fig:|tab:} in the body (NOT inside a caption)
# Strategy: strip all figure/table env bodies, then scan remaining prose.
# Build a mask of line ranges that are INSIDE float bodies.
float_ranges = []
for m in env_pat.finditer(c):
    sL = c[:m.start()].count("\n") + 1
    eL = c[:m.end()].count("\n") + 1
    float_ranges.append((sL, eL))

def in_float(line_no):
    return any(a <= line_no <= b for a, b in float_ranges)

ref_hits = {}  # label -> list of (line_no)
for i, line in enumerate(lines, 1):
    if in_float(i):
        continue  # skip refs inside caption
    for m in re.finditer(r"\\(?:ref|Cref|autoref|cref)\{((?:fig|tab):[^}]+)\}", line):
        ref_hits.setdefault(m.group(1), []).append(i)

# ---- 3. Diagnose each label
print("=" * 80)
print("v2.0-r first-ref-vs-float position audit")
print("=" * 80)
print()
print(f"{'label':40s} {'env':6s} {'firstRef':>9s} {'floatLine':>10s} {'gap':>6s}  status")
print("-" * 80)

bad = []
for label in sorted(float_line, key=lambda l: float_line[l]):
    prose_refs = ref_hits.get(label, [])
    fL = float_line[label]
    if not prose_refs:
        status = "NO prose ref (caption-only)"
        bad.append((label, "no prose ref", -1, fL))
        first_ref = -1
        gap = None
    else:
        first_ref = prose_refs[0]
        gap = fL - first_ref
        # Check for explicit forward-ref hint on the first-ref line
        # ("below", "later", "in Appendix", "in Section~N", ...)
        ref_line_text = lines[first_ref - 1] if first_ref > 0 else ""
        # Also check neighbouring lines (LaTeX often wraps)
        window = "\n".join(lines[max(0, first_ref-1):min(len(lines), first_ref+2)])
        fwd_hint = bool(re.search(
            r"\b(below|later|in Appendix|Appendix~\\ref|in Section~\\ref|in the appendix|hereafter)\b",
            window, re.IGNORECASE))
        if gap < 0:
            status = "!! FLOAT BEFORE first ref (审稿人先看到图，后读到引用)"
            bad.append((label, "float before ref", first_ref, fL))
        elif gap == 0:
            status = "same-line (unusual)"
        elif gap > 60:
            if fwd_hint:
                status = f"forward-ref OK ({gap} lines away, marked with hint)"
            else:
                status = f"!! float {gap} lines AFTER first ref (no forward-ref hint)"
                bad.append((label, f"gap={gap} lines, no hint", first_ref, fL))
        else:
            status = f"OK ({gap} lines after)"
    fr_str = f"{first_ref}" if first_ref > 0 else "—"
    gap_str = f"{gap}" if gap is not None else "—"
    print(f"{label:40s} {float_env[label]:6s} L{fr_str:>7s} L{fL:>8d} {gap_str:>7s}  {status}")

print()
print(f"[all refs per label]")
for label in sorted(float_line, key=lambda l: float_line[l]):
    refs = ref_hits.get(label, [])
    fL = float_line[label]
    tag = "❌" if not refs or (refs and refs[0] > fL) else "✓"
    print(f"  {tag} {label:40s}  float=L{fL}  refs={refs}")

print()
if not bad:
    print("VERDICT: every float appears AFTER its first prose reference.")
else:
    print(f"VERDICT: {len(bad)} issue(s):")
    for lbl, msg, r, fl in bad:
        print(f"  • {lbl}: {msg}  (first ref L{r}, float L{fl})")
