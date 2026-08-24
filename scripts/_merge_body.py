from pathlib import Path

MAIN = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")
BODY = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/_body_append.tex")

main = MAIN.read_text(encoding="utf-8")
body = BODY.read_text(encoding="utf-8")

# Strip trailing \end{document} from main if it accidentally has one
end_tok = r"\end{document}"
if end_tok in main:
    main = main.rsplit(end_tok, 1)[0].rstrip() + "\n\n"

# Strip leading duplicate separator/spacing from body but keep the section
body = body.lstrip()

merged = main + body

if not merged.rstrip().endswith(end_tok):
    if end_tok not in merged:
        merged = merged.rstrip() + "\n\n" + end_tok + "\n"

MAIN.write_text(merged, encoding="utf-8")
print(f"[ok] merged: {MAIN}")
print(f"[size] {MAIN.stat().st_size:,} bytes")

# quick sanity report
import re
sections = re.findall(r"\\section\{([^}]+)\}", merged)
print("[sections]")
for s in sections:
    print("  -", s)
n_thm = len(re.findall(r"\\begin\{theorem\}", merged))
n_def = len(re.findall(r"\\begin\{definition\}", merged))
n_alg = len(re.findall(r"\\begin\{algorithm\}", merged))
n_fig = len(re.findall(r"\\begin\{figure\}", merged))
n_tab = len(re.findall(r"\\begin\{table\}", merged))
print(f"[theorems] {n_thm}")
print(f"[definitions] {n_def}")
print(f"[algorithms] {n_alg}")
print(f"[figures] {n_fig}")
print(f"[tables] {n_tab}")
