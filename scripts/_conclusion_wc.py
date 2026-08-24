import re
from pathlib import Path
c = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex").read_text(encoding="utf-8")
m = re.search(r"section\{Conclusion\}(.*?)subsection\*\{Acknowledgements\}", c, re.DOTALL)
txt = m.group(1)
# strip latex commands
body = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", txt)
body = re.sub(r"[{}%$]", " ", body)
body = re.sub(r"\s+", " ", body).strip()
print(f"Conclusion body ≈ {len(body.split())} words total")
paras = re.split(r"\n\s*\n", txt)
for i, p in enumerate(paras):
    s = p.strip()
    if not s: continue
    head = s[:80].replace("\n"," ").replace("  "," ")
    w = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", p)
    w = re.sub(r"[{}%$]", " ", w)
    n = len(w.split())
    print(f"  para {i+1}: {n:3d} words   [{head}]")
