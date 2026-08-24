"""wordcount.py — count words in abstract and each section."""
import re
from pathlib import Path

TEX = Path(__file__).resolve().parent.parent / "manuscript" / "main_eca_v01.tex"
content = TEX.read_text(encoding="utf-8")

# Strip % comments preserving \%
lines = []
for line in content.splitlines():
    out, in_esc = "", False
    for c in line:
        if in_esc:
            out += c; in_esc = False
        elif c == "\\":
            out += c; in_esc = True
        elif c == "%":
            break
        else:
            out += c
    lines.append(out)
clean = "\n".join(lines)

def wc(text):
    text = re.sub(r"\\[A-Za-z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?", " ", text)
    text = re.sub(r"[{}]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split())

m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", clean, re.DOTALL)
if m:
    print(f"Abstract:  {wc(m.group(1)):4d} words  (ECA hard limit 150)")

secs = list(re.finditer(r"\\section\{([^}]+)\}", clean))
for i, s in enumerate(secs):
    end = secs[i+1].start() if i+1 < len(secs) else clean.find("\\bibliography")
    if end == -1: end = len(clean)
    body = clean[s.end():end]
    body = body.replace("\\appendix", "")
    print(f"section  {s.group(1)[:50]:50s}  {wc(body):5d} words")

body_all = re.search(r"\\maketitle(.*?)\\bibliography", clean, re.DOTALL)
if body_all:
    print(f"\nTotal main body: {wc(body_all.group(1)):5d} words")
