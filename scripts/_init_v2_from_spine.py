from pathlib import Path

SPINE = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2_spine.tex")
DST = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")

c = SPINE.read_text(encoding="utf-8")

new_header = (
    "%%========================================================================\n"
    "%%  File   : cex_contagion_v2.0/manuscript/main_eca_v2.tex\n"
    "%%  Title  : Unlikely Intersections in Crypto Exchange Reserves\n"
    "%%           An O-Minimal Test for Systemic Risk\n"
    "%%  Target : Econometrica initial submission (single-blind)\n"
    "%%  Version: v2.0 (2026-08-18)\n"
    "%%  Author : Hongjun Gou -- ICBC Beijing\n"
    "%%  Note   : Spine (title + abstract + section 1) frozen from v0.9-m; \n"
    "%%           other sections regenerated per data_charter.md three-tier principle.\n"
    "%%========================================================================\n\n"
)

lines = c.split("\n")
body_start = 0
for i, line in enumerate(lines):
    if line.strip().startswith(r"\documentclass"):
        body_start = i
        break
body = "\n".join(lines[body_start:])

# Add algorithm2e after titlesec
old_tl = r"\usepackage{titlesec}"
new_tl = r"\usepackage{titlesec}" + "\n" + r"\usepackage[ruled,vlined,linesnumbered]{algorithm2e}"
if old_tl in body:
    body = body.replace(old_tl, new_tl, 1)
    print("[ok] algorithm2e added to preamble")
else:
    print("[warn] titlesec not found in body")

DST.write_text(new_header + body, encoding="utf-8")
print(f"[write] {DST}")
print(f"[size] {DST.stat().st_size:,} bytes")
