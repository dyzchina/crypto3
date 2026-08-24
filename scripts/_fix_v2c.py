"""
ECA v2.0-c 修复：
- centralised → centralized × 3
- labelled → labeled × 3
- normalised → normalized × 1
- App E.5 长路径再切分（消 58 / 51 pt overfull）
"""
from pathlib import Path
import re

TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")
c = TEX.read_text(encoding="utf-8")
orig = c

# Only touch text lines, not comment header
def sub_non_comment(pattern, repl, text):
    # process line-by-line, skip lines starting with %%
    out = []
    for line in text.split("\n"):
        if line.lstrip().startswith("%%") or line.lstrip().startswith("% "):
            out.append(line)
        else:
            out.append(re.sub(pattern, repl, line))
    return "\n".join(out)

c = sub_non_comment(r"\bcentralised\b", "centralized", c)
c = sub_non_comment(r"\bcentralise\b", "centralize", c)
c = sub_non_comment(r"\blabelled\b", "labeled", c)
c = sub_non_comment(r"\blabelling\b", "labeling", c)
c = sub_non_comment(r"\bnormalised\b", "normalized", c)
c = sub_non_comment(r"\bnormalisation\b", "normalization", c)

# App E.5 long-string overfull
c = c.replace(
    r"pull_defillama_cex.py",
    r"pull\_defillama\_\allowbreak cex.py"
).replace(
    r"pull\_defillama\_cex.py",
    r"pull\_defillama\_\allowbreak cex.py"
)
c = c.replace(
    r"aggregate_por.py",
    r"aggregate\_\allowbreak por.py"
).replace(
    r"aggregate\_por.py",
    r"aggregate\_\allowbreak por.py"
)
c = c.replace(
    r"did_regression.py",
    r"did\_\allowbreak regression.py"
).replace(
    r"did\_regression.py",
    r"did\_\allowbreak regression.py"
)
c = c.replace(
    r"wild_bootstrap.py",
    r"wild\_\allowbreak bootstrap.py"
).replace(
    r"wild\_bootstrap.py",
    r"wild\_\allowbreak bootstrap.py"
)
c = c.replace(
    r"estimator_nk.py",
    r"estimator\_\allowbreak nk.py"
).replace(
    r"estimator\_nk.py",
    r"estimator\_\allowbreak nk.py"
)

TEX.write_text(c, encoding="utf-8")
print("[fix] centralised/labelled/normalised → US spelling")
print("[fix] script filenames tokenized with \\allowbreak")
print(f"[bytes] {len(orig):,} → {len(c):,}")
