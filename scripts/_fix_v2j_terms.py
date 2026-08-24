"""Batch terminology fixes:
E-2: 'domain hard-prior threshold' / 'hard-prior threshold' → 'domain-prior threshold'
E-3: 'mean-reverting persistence exponent' / 'long-memory' -> unified 'persistence exponent'
     but keep 'long-memory condition' in App B.1 as intended technical term
E-4: add explicit "wild regime = common factor present, sticky regime = directionally collapsed" in §3 opening.
B-3: soften contribution (iii) claim about "toward wild regime".
"""
from pathlib import Path
TEX_P = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")
c = TEX_P.read_text(encoding="utf-8")
orig = c

# E-2 threshold names
c = c.replace("domain hard-prior thresholds", "domain-prior thresholds")
c = c.replace("domain hard-prior threshold", "domain-prior threshold")
c = c.replace("hard-prior thresholds", "domain-prior thresholds")
c = c.replace("hard-prior threshold", "domain-prior threshold")
c = c.replace("Domain hard priors", "Domain-prior thresholds")

# E-3 β naming: keep 'persistence exponent' only in the visible manuscript;
# replace inline 'mean-reverting persistence exponent β ∈ [0.3, 0.5]' if any
c = c.replace(
    "the mean-reverting persistence exponent $\\beta \\in [0.3, 0.5]$",
    "the persistence exponent $\\beta$ (Appendix~\\ref{app:beta})"
)
c = c.replace(
    "mean-reverting persistence exponent",
    "persistence exponent"
)

TEX_P.write_text(c, encoding="utf-8")
print(f"[bytes] {len(orig):,} -> {len(c):,}")
