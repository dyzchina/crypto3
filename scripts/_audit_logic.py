"""
Fast mechanical scan for logic-drift symptoms in the manuscript.
Complements the semantic reviewer agent — this catches surface-level drift.
"""
from pathlib import Path
import re

TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex").read_text(encoding="utf-8")

def report(cat, findings):
    if not findings:
        print(f"\n=== {cat} ===\n  NONE")
        return
    print(f"\n=== {cat} ===")
    for f in findings:
        print(f"  - {f}")

# ------------------------------------------------------------------
# G1 · terminology drift — key concepts that MUST be spelled the same
# ------------------------------------------------------------------
terms = {
    "intersection frontier": r"intersection frontier",
    "counting frontier":     r"counting frontier",
    "empirical frontier":    r"empirical frontier",
    "domain-prior":          r"domain[- ]prior",
    "hard-prior":            r"hard[- ]prior",
    "ex-ante supervisory":   r"ex-ante supervisory",
    "persistence exponent":  r"persistence exponent",
    "long-memory":           r"long[- ]memory",
    "wild regime":           r"wild[- ]regime",
    "wild-regime lower":     r"wild[- ]regime lower",
    "common-factor":         r"common[- ]factor",
    "reserve-simplex":       r"reserve[- ]simplex",
    "reserve simplex":       r"reserve simplex",
    "on-chain-indexed":      r"on[- ]chain[- ]indexed",
    "top-ten":               r"top[- ]ten",
    "top-five":              r"top[- ]five",
    "top ten":               r"top ten",
    "top five":              r"top five",
    "5 CEX":                 r"\bfive CEX\b|\b5 CEX\b",
    "chapter 11":            r"chapter\s*11",
    "Chapter 11":            r"Chapter\s*11",
    "Chapter~11":            r"Chapter~11",
    "chapter~11":            r"chapter~11",
}
freq = {}
for label, pat in terms.items():
    hits = re.findall(pat, TEX, flags=re.I if label != "5 CEX" else 0)
    freq[label] = len(hits)

for label, n in sorted(freq.items()):
    print(f"  {label:35s}  ×{n}")

# ------------------------------------------------------------------
# G2 · promises: "the paper closes"/"delivers"/"we show" — pointer check
# ------------------------------------------------------------------
promises = []
for m in re.finditer(r"(?:the paper|we|the framework)\s+(closes?|delivers?|shows?|proves?|constructs?|reads?|takes?|reports?|adds?|carries?|extends?)\s+([^.]{20,120}\.)", TEX):
    promises.append((m.start(), m.group(0)[:150]))
report("PROMISES (verbs) — 每条都要在正文/附录有对应交付", [f"line~{TEX[:s].count(chr(10))+1}: {t}" for s, t in promises[:25]])

# ------------------------------------------------------------------
# G3 · every Def/Thm/Prop/Cor referenced?  every ref has a target?
# ------------------------------------------------------------------
labels = set(re.findall(r"\\label\{([^}]+)\}", TEX))
refs   = set()
for m in re.finditer(r"\\(?:ref|eqref|autoref)\{([^}]+)\}", TEX):
    refs.add(m.group(1))
undefined_refs = refs - labels
never_used     = labels - refs
report("交叉引用完整", [f"undefined ref: {r}" for r in sorted(undefined_refs)])
report("定义/引理/命题从未被引用（可能是死代码）", [f"unused label: {l}" for l in sorted(never_used)])

# ------------------------------------------------------------------
# G4 · numbers that MUST match between different parts
# ------------------------------------------------------------------
num_positions = {}
for m in re.finditer(r"(0\.112\b|0\.026\b|0\.011\b|4\.28\b|9,?999\b|0\.025\b|0\.199\b|0\.709\b|0\.896\b|0\.577\b|168\.9\b|22\.1\b|18\.4\b|209\.4\b|-?0\.024\b|-?0\.39\b|-?0\.038?5?\b|-?0\.142\b|16 billion\b|8\\%|\+?9\.6|\+?9\.7|\+?5\.7|13 clusters|39 snapshots|1,\?374|1,\?335|1,\?370|145~MB|170~MB|55%|30%|13-quarter|13.quarter|thirteen[- ]quarter)", TEX):
    tok = m.group(1)
    num_positions.setdefault(tok, []).append(TEX[:m.start()].count("\n") + 1)

for tok in sorted(num_positions):
    print(f"  {tok:20s}  appears at lines: {num_positions[tok]}")

# ------------------------------------------------------------------
# G5 · "companion release" — how many, all consistent?
# ------------------------------------------------------------------
comp = [(m.start(), TEX[m.start():m.start()+200]) for m in re.finditer(r"companion release", TEX)]
report("companion release 提及数", [f"line~{TEX[:s].count(chr(10))+1}: {t[:120]}" for s, t in comp])

# ------------------------------------------------------------------
# G6 · "deferred" / "TODO" / "future" — anything that should be resolved
# ------------------------------------------------------------------
deferred = [(m.start(), TEX[m.start():m.start()+200]) for m in re.finditer(r"deferred|to be added|future release|is delivered in", TEX)]
report("延期承诺", [f"line~{TEX[:s].count(chr(10))+1}: {t[:120]}" for s, t in deferred])

# ------------------------------------------------------------------
# G7 · Table numbering / labels
# ------------------------------------------------------------------
tab_labels = re.findall(r"\\label\{tab:([^}]+)\}", TEX)
tab_refs   = re.findall(r"Table~\\ref\{tab:([^}]+)\}", TEX)
report("Table label vs ref", [f"defined but never referenced: tab:{l}" for l in set(tab_labels) - set(tab_refs)])
report("Table ref but no label", [f"referenced but not defined: tab:{r}" for r in set(tab_refs) - set(tab_labels)])
