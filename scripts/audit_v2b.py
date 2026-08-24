"""
ECA v2.0-b 机械审计：
1. 主稿所有数字 vs 已知 canonical 值 (τ=0.112, t=4.28, SE=0.026, CI=[0.025,0.199], pooling=0.709 ...)
2. \cite* / \ref / \eqref 全部键出现次数
3. refs.bib 里所有 entry vs 主稿实际用到的 → 报告 orphan / missing
4. -ise / -ised / -isation 英式残留（ECA 用美式）
5. 双空格 / 半角括号里的 emdash 用法
6. 版本号泄漏 (v0.4 / v0.5 / v0.9 / v2.0)
7. Overfull hbox 汇总
"""
from pathlib import Path
import re

ROOT = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript")
TEX  = (ROOT / "main_eca_v2.tex").read_text(encoding="utf-8")
BIB  = (ROOT / "refs.bib").read_text(encoding="utf-8")
LOG  = (ROOT / "main_eca_v2.log").read_text(encoding="utf-8", errors="replace")

print("="*70)
print("PART A · 数字一致性")
print("="*70)
# find every real-number-looking token
canon = {
    "0.112": "τ (DiD ATT)",
    "0.026": "cluster SE",
    "0.011": "homoskedastic SE",
    "4.28": "cluster-t",
    "10.06": "homoskedastic-t",
    "0.025": "wild-boot CI lower",
    "0.199": "wild-boot CI upper",
    "0.709": "pooling gain empirical",
    "0.896": "pooling gain theory n^{-1/(2m)}",
    "0.577": "independence benchmark n^{-1/2}",
    "0.816": "SV1",
    "0.574": "SV2",
    "0.530": "SV3",
    "0.235": "SV4",
    "9999": "wild-boot draws",
    "9{,}999": "wild-boot draws typeset",
    "168.9": "Binance reserve USD bn",
    "22.1": "OKX reserve USD bn",
    "18.4": "Bybit reserve USD bn",
    "209.4": "3-venue total USD bn",
    "1.2": "Celsius gap",
    "1.3": "Voyager/BlockFi gap",
    "8.7": "FTX gap",
    "3.4": "Genesis gap",
    "16": "aggregate shortfall USD bn",
    "1,374": "Binance daily obs",
    "1,335": "OKX daily obs",
    "1,370": "Bybit daily obs",
    "170": "archive size MB",
    "145": "raw JSON MB uncompressed",
}
for tok, label in canon.items():
    hits = TEX.count(tok)
    tag = "✓" if hits > 0 else "✗"
    print(f"  {tag} {tok:>10}  ×{hits:2d}   ({label})")

print()
print("="*70)
print("PART B · Cite key: 主稿引用 vs refs.bib 定义")
print("="*70)
tex_cites = set()
for m in re.finditer(r"\\cite[a-z]*\{([^}]+)\}", TEX):
    for k in m.group(1).split(","):
        tex_cites.add(k.strip())
bib_keys = set(re.findall(r"@\w+\{([^,]+),", BIB))
missing  = tex_cites - bib_keys
orphan   = bib_keys - tex_cites
print(f"主稿引用键数: {len(tex_cites)}")
print(f"refs.bib 定义键数: {len(bib_keys)}")
print(f"主稿引用但 bib 缺失（bibtex 会报 undef cite）: {len(missing)}")
for k in sorted(missing):
    print(f"  ✗ MISSING: {k}")
print(f"bib 定义但主稿未用（orphan，不影响编译）: {len(orphan)}")
for k in sorted(orphan)[:12]:
    print(f"  · orphan: {k}")

print()
print("="*70)
print("PART C · 交叉引用 label vs \\ref")
print("="*70)
labels = set(re.findall(r"\\label\{([^}]+)\}", TEX))
refs   = set()
for m in re.finditer(r"\\(?:ref|eqref|autoref)\{([^}]+)\}", TEX):
    refs.add(m.group(1))
ref_missing = refs - labels
ref_orphan  = labels - refs
print(f"labels: {len(labels)} / refs: {len(refs)}")
print(f"ref 用了但 label 未定义: {len(ref_missing)}")
for k in sorted(ref_missing):
    print(f"  ✗ MISSING LABEL: {k}")
print(f"label 定义但 ref 未用: {len(ref_orphan)}")
for k in sorted(ref_orphan):
    print(f"  · unused label: {k}")

print()
print("="*70)
print("PART D · 英式拼写残留（ECA 用美式）")
print("="*70)
brit_pats = [
    (r"\bharmonis[ea]d?\b", "harmonize"),
    (r"\banalys[ei]s?d?\b", "analyze"),
    (r"\bnormalis[ea]d?\b", "normalize"),
    (r"\brealis[ea]d?\b", "realize"),
    (r"\borganis[ea]d?\b", "organize"),
    (r"\bcolour\b", "color"),
    (r"\bcentralised\b", "centralized"),
    (r"\bcentralise\b", "centralize"),
    (r"\bbehaviour\b", "behavior"),
    (r"\bcharacteris[ea]d?\b", "characterize"),
    (r"\bmodell(?:ing|ed)\b", "modeling"),
    (r"\blabell(?:ing|ed)\b", "labeling"),
]
for pat, us in brit_pats:
    ms = re.findall(pat, TEX, flags=re.I)
    if ms:
        print(f"  ⚠ {pat}  → 应用 {us}  出现 {len(ms)} 次: {list(set(ms))[:5]}")

print()
print("="*70)
print("PART E · 版本号 / 内部代号 泄漏")
print("="*70)
leak_pats = [r"\bv0\.[0-9]+", r"\bv2\.[0-9]+", r"\bv1\.[0-9]+",
             r"\bv0\.9-[a-z]\b", r"cex_contagion_v"]
for pat in leak_pats:
    ms = re.findall(pat, TEX)
    if ms:
        print(f"  ⚠ {pat}: {len(ms)} 次 —— {ms[:5]}")

print()
print("="*70)
print("PART F · 排版红旗")
print("="*70)
# double space
dblsp = TEX.count("  ")  # naive; may include indentation
# em-dash usage
em = TEX.count("---")
en = len(re.findall(r"(?<!-)--(?!-)", TEX))
print(f"  '---' em-dash 出现: {em}")
print(f"  '--' en-dash 出现: {en}  (数字区间可用；文本流不建议)")
# footnote in abstract
abs_start = TEX.find("Abstract")
abs_end   = TEX.find(r"\vspace{1em}", abs_start)
if abs_start >= 0 and abs_end > abs_start:
    abstract = TEX[abs_start:abs_end]
    has_fn = "\\footnote" in abstract
    print(f"  Abstract footnote 检查: {'⚠ 有 footnote' if has_fn else '✓ 无 footnote'}")
    print(f"  Abstract 字符数: {len(abstract)}   词数(估): {len(re.findall(r'[A-Za-z]+', abstract))}")

# lineno 检查（ECA 不加）
if r"\linenumbers" in TEX and not TEX.count("% \\linenumbers"):
    print(f"  ⚠ \\linenumbers 打开了 —— ECA 不加行号")
else:
    print(f"  ✓ lineno 未启用")

# Overfull ≥ 30pt
over = re.findall(r"Overfull \\hbox \(([0-9.]+)pt", LOG)
big = [float(x) for x in over if float(x) >= 30]
print(f"  Overfull hbox ≥ 30pt: {len(big)} 处")
for x in sorted(big, reverse=True):
    print(f"    - {x:.2f}pt")

# 段落末尾双句点、句号后无空格
d_dot = len(re.findall(r"\.\.[^\.]", TEX))
print(f"  双句点 '..' 疑似: {d_dot}")

# 出现在正文的 fabricated 危险词（未替换到位）
risky = ["TBD", "FIXME", "XXX", "TODO", "placeholder"]
for r in risky:
    c = TEX.count(r)
    if c:
        print(f"  ⚠ '{r}': {c} 次")

print()
print("="*70)
print("PART G · 章节大纲")
print("="*70)
for line in TEX.splitlines():
    if line.startswith(r"\section"):
        print("  §  " + line.strip())
    elif line.startswith(r"\subsection"):
        print("     " + line.strip())
