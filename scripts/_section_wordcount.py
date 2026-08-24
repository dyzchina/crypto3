"""
Per-section wordcount & structure map for main_eca_v2.tex.
"""
from pathlib import Path
import re

TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex").read_text(encoding="utf-8")

def wcount(s):
    body = re.sub(r"%.*", "", s)
    body = re.sub(r"\\begin\{[^}]+\}|\\end\{[^}]+\}", " ", body)
    body = re.sub(r"\\[a-zA-Z]+\*?", " ", body)
    body = re.sub(r"[{}\[\]$]", " ", body)
    return len(re.findall(r"[A-Za-z][A-Za-z-]+", body))

# split into sections
sections = re.split(r"(\\section\*?\{[^}]+\}(?:\\label\{[^}]+\})?)", TEX)
current = None
buf = []
result = []
for chunk in sections:
    if chunk.startswith(r"\section"):
        if current:
            result.append((current, "".join(buf), wcount("".join(buf))))
        current = chunk
        buf = []
    else:
        buf.append(chunk)
if current:
    result.append((current, "".join(buf), wcount("".join(buf))))

print(f"{'section':60s}  {'words':>7s}")
print("-" * 72)
total = 0
for sec, body, wc in result:
    name = re.sub(r"\\section\*?\{([^}]+)\}.*", r"\1", sec).replace("\n", " ")[:58]
    print(f"{name:60s}  {wc:>7d}")
    total += wc
print("-" * 72)
print(f"{'TOTAL':60s}  {total:>7d}")

# also break by subsection
print()
print("=" * 72)
print("Subsection breakdown (only for large sections):")
print("=" * 72)
for sec, body, wc in result:
    if wc < 400:
        continue
    name = re.sub(r"\\section\*?\{([^}]+)\}.*", r"\1", sec).replace("\n", " ")[:50]
    print(f"\n[{name}]  total = {wc}")
    subs = re.split(r"(\\subsection\*?\{[^}]+\}(?:\\label\{[^}]+\})?)", body)
    cur_sub = None
    subbuf = []
    for c in subs:
        if c.startswith(r"\subsection"):
            if cur_sub:
                sname = re.sub(r"\\subsection\*?\{([^}]+)\}.*", r"\1", cur_sub).replace("\n", " ")[:48]
                print(f"  {sname:50s}  {wcount(''.join(subbuf)):>5d}")
            cur_sub = c
            subbuf = []
        else:
            subbuf.append(c)
    if cur_sub:
        sname = re.sub(r"\\subsection\*?\{([^}]+)\}.*", r"\1", cur_sub).replace("\n", " ")[:48]
        print(f"  {sname:50s}  {wcount(''.join(subbuf)):>5d}")
