"""
Audit adjacency of floating environments (figure/table) in the tex.
Reports every pair of consecutive figure/table blocks separated by only
whitespace or non-text lines (< N words of prose between them).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import re
from pathlib import Path

TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")
with open(TEX, "rb") as f:
    c = f.read().decode("utf-8", errors="replace")

# Find every figure/table environment span
env_pat = re.compile(r"\\begin\{(figure|table)\*?\}(.*?)\\end\{\1\*?\}", re.DOTALL)
blocks = []
for m in env_pat.finditer(c):
    env = m.group(1)
    body = m.group(2)
    lbl = re.search(r"\\label\{([^}]+)\}", body)
    label = lbl.group(1) if lbl else "?"
    start = m.start()
    end = m.end()
    start_line = c[:start].count("\n") + 1
    end_line = c[:end].count("\n") + 1
    blocks.append({"env": env, "label": label, "start": start, "end": end,
                   "start_line": start_line, "end_line": end_line})

blocks.sort(key=lambda b: b["start"])

print("=" * 70)
print(f"Float adjacency audit — {len(blocks)} floats")
print("=" * 70)
print()

def wordcount(s):
    # rough plain-text word count, strip commands
    s = re.sub(r"\\[a-zA-Z]+(\[[^\]]*\])?(\{[^}]*\})?", " ", s)
    s = re.sub(r"[{}%\[\]]", " ", s)
    return len(s.split())

issues = []
for i in range(len(blocks) - 1):
    a, b = blocks[i], blocks[i+1]
    between = c[a["end"]:b["start"]]
    words = wordcount(between)
    print(f"  [{a['env']:6s} {a['label']:28s} L{a['end_line']:>4d}]"
          f" -> [{b['env']:6s} {b['label']:28s} L{b['start_line']:>4d}]"
          f"  gap={words:>4d} words")
    if words < 25:
        issues.append((i, a, b, words, between))

print()
print(f"--- {len(issues)} adjacencies with <25 words between (审稿人挤在一起) ---")
for idx, a, b, words, between in issues:
    print()
    print(f"  #{idx+1}: {a['env']} {a['label']} @L{a['end_line']}  ->  {b['env']} {b['label']} @L{b['start_line']}")
    print(f"       gap = {words} words")
    print(f"       between text (raw):\n"
          f"       ---8<---\n{between.strip()[:200]}\n       ---8<---")
