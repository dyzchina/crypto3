"""
v2.0-n citation fixes based on referee audit Top-10:

1) Rename PS2009 -> PS2008 (bib key change) everywhere in tex
2) App B.2 misattribution: remove PS2008 as source of scale-induction inequality
   (Prop 2.2 doesn't exist there); reframe as heuristic derivation
3) App B.2 self-similarity claim: remove PS2008 citation (crypto-time-series unrelated)
4) App B.3 endpoint claim: remove PS2008 citation
5) PW2006 "Theorem 3.6" -> "Theorem 1.8" (three sites: §3.3, App A, App C)
6) §4.4 line 920 GKM for Grayscale: remove citation (unrelated to Grayscale ruling)
7) §2 line 330 PW2006 for R_an,exp: remove PW2006 (it's counting theorem, not
   o-minimality attribution)
8) Griffin-Kruger-Mei 主要用于 §1 footnote (cluster documented), keep with
   updated bib entry ("What is Forensic Finance" 2023 SSRN with FTX case study)
"""
from pathlib import Path
import re

TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")
c = TEX.read_text(encoding="utf-8")
orig = c

# 1) PS2009 -> PS2008
c = c.replace("PeterzilStarchenko2009", "PeterzilStarchenko2008")

# 5) PW2006 "Theorem 3.6" -> "Theorem 1.8"
c = c.replace(
    "Theorem~3.6 of \\citet{PilaWilkie2006}",
    "Theorem~1.8 of \\citet{PilaWilkie2006}",
)
c = c.replace(
    "Theorem 3.6 of \\citet{PilaWilkie2006}",
    "Theorem 1.8 of \\citet{PilaWilkie2006}",
)

# 6) Line 920 area: remove Grayscale citation of GKM
c = c.replace(
    "spot-BTC ETF approval and may have moved reserve compositions\nbefore 2024-Q1~\\citep{Griffin-Kruger-Mei2023}.",
    "spot-BTC ETF approval and may have moved reserve compositions\nbefore 2024-Q1.",
)

# 7) §2 line 330: remove PW2006 from o-minimality structure attribution
c = c.replace(
    "in the o-minimal structure $\\R_{\\mathrm{an},\\exp}$\n\\citep{vandenDries1998Tame, PilaWilkie2006}",
    "in the o-minimal structure $\\R_{\\mathrm{an},\\exp}$\n\\citep{vandenDries1998Tame}",
)

# 2-4) App B.2 & B.3: remove PS2008 as source (keep as heuristic)
# Find and reframe the specific claims
c = c.replace(
    "Adapting the definable-family bound of\n\\citet[Prop.~2.2 and subsequent remarks]{PeterzilStarchenko2008}\nto the reserve-composition tangent space, a definable family in an\no-minimal structure of ambient dimension $d$ heuristically admits",
    "By a heuristic adaptation of the o-minimal counting machinery of\n\\citet{PilaWilkie2006} to definable families, a definable family in an\no-minimal structure of ambient dimension $d$ admits",
)

c = c.replace(
    "Under the definition of $\\beta$ in \\S B.1 the persistence exponent\nis self-similar in the horizon (\\citealp{PeterzilStarchenko2008}),\nso",
    "Under the definition of $\\beta$ in \\S B.1 the persistence exponent\nis self-similar in the horizon, so",
)

c = c.replace(
    "at $k=1$ it recovers the single-venue o-minimal rate $T^{\\beta}/n$ of\n\\citet{PeterzilStarchenko2008}; at $k=n$",
    "at $k=1$ it recovers the single-venue rate $T^{\\beta/n}$; at $k=n$",
)
# Alt spacing
c = c.replace(
    "at $k = 1$ it recovers the single-venue o-minimal rate $T^\\beta/n$ of\n\\citet{PeterzilStarchenko2008}; at $k = n$",
    "at $k = 1$ it recovers the single-venue rate $T^{\\beta/n}$; at $k = n$",
)

# 8) App A vdD1998 attribution -- soften from "is due to vdD1998" to "is documented in vdD1998"
c = c.replace(
    "The o-minimality of the ambient structure $\\R_{\\mathrm{an},\\exp}$ is due to\n\\citet{vandenDries1998Tame}.",
    "The o-minimality of the ambient structure $\\R_{\\mathrm{an},\\exp}$ is a\nstandard fact of the o-minimality literature; see \\citet{vandenDries1998Tame}.",
)

# Save
TEX.write_text(c, encoding="utf-8")
diff = len(orig) - len(c)
print(f"[bytes] {len(orig):,} -> {len(c):,} (diff {diff:+d})")

# Verify PS2008 renaming
n_ps2009 = c.count("PeterzilStarchenko2009")
n_ps2008 = c.count("PeterzilStarchenko2008")
print(f"[remaining PS2009] {n_ps2009}   [now PS2008] {n_ps2008}")
n_thm36 = c.count("Theorem 3.6") + c.count("Theorem~3.6")
n_thm18 = c.count("Theorem 1.8") + c.count("Theorem~1.8")
print(f"[remaining Theorem 3.6] {n_thm36}   [now Theorem 1.8] {n_thm18}")
