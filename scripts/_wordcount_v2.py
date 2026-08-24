"""Quick stats for v2.0 main manuscript."""
from pathlib import Path
import re

p = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex").read_text(encoding="utf-8")
raw = p
body = re.sub(r"%.*", "", p)
body = re.sub(r"\\begin\{[^}]+\}|\\end\{[^}]+\}", " ", body)
body = re.sub(r"\\[a-zA-Z]+\*?", " ", body)
body = re.sub(r"[{}\[\]]", " ", body)
words = re.findall(r"[A-Za-z][A-Za-z-]+", body)
cite_keys = set()
for m in re.finditer(r"\\cite[a-z]*\{([^}]+)\}", raw):
    for k in m.group(1).split(","):
        cite_keys.add(k.strip())
sections = re.findall(r"\\section\{([^}]+)\}", raw)
subs = re.findall(r"\\subsection[*]?\{([^}]+)\}", raw)
print(f"[tex bytes] {len(raw):,}")
print(f"[body word count (rough, incl. Appendix)] {len(words):,}")
print(f"[unique cite keys] {len(cite_keys)}")
print(f"[sections] {len(sections)}   [subsections] {len(subs)}")
