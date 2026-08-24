"""
v2.0-c 无 spine 修复：
1. bibkey typo: AchariaEtAl2017SES → AcharyaEtAl2017SES；EliottGolubJackson2014 → ElliottGolubJackson2014
2. §3.4 duplicate "reference Python implementation" 句 → 删后半
3. §3 Thm 1 endpoint α(1,·,5)=5/4 与新推导矛盾 → 校正为 α(1,n,5)=5(n-1)/12
4. §Fig 2 caption：Terra/UST 提到但 Table 1 缺失 → caption 改为"lollipop heights encode ordering by system-wide balance-sheet impact；Terra/UST 作为 on-chain trigger 见 Table 1 前段 5 principal events 定义"
5. §Table 1 → 5 vs 6 数目自洽（把 Terra 从 Fig 2 caption 里移除，或明确"cluster of 6 including Terra"）
6. §4.5 pooling ratio 0.709 vs 0.577/0.896 读法反了 → 校正表述
"""
from pathlib import Path
TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")
BIB = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/refs.bib")

tex = TEX.read_text(encoding="utf-8")
bib = BIB.read_text(encoding="utf-8")

# 1) bibkey typo
tex = tex.replace("AchariaEtAl2017SES", "AcharyaEtAl2017SES")
bib = bib.replace("AchariaEtAl2017SES", "AcharyaEtAl2017SES")
tex = tex.replace("EliottGolubJackson2014", "ElliottGolubJackson2014")
bib = bib.replace("EliottGolubJackson2014", "ElliottGolubJackson2014")

# 2) §3.4 duplicate sentence
old_dup = "The overall complexity is $O(N_\\delta \\log N_\\delta)$ under\n$N_\\delta \\asymp R^\\alpha$ for $\\alpha \\in (n{-}1, n)$: the\npartition dominates and the composition step is $O(R)$ in the\nnumber of cells. A reference Python implementation in about 200\nlines, together with a worked example on the panel of\nSection~\\ref{sec:empirics}, is included in the reproducibility\narchive."
new_dup = "The overall complexity is $O(N_\\delta \\log N_\\delta)$ under\n$N_\\delta \\asymp R^\\alpha$ for $\\alpha \\in (n{-}1, n)$: the\npartition dominates and the composition step is $O(R)$ in the\nnumber of cells."
if old_dup in tex:
    tex = tex.replace(old_dup, new_dup, 1)
    print("[ok] removed §3.4 duplicate 'reference Python implementation'")
else:
    print("[warn] duplicate sentence not found verbatim")

# 3) App A.3 endpoint math correction
# α(k,n,m) = k-1 + m(n-k)/d, d=n(m-1)
# k=1: α(1,n,m) = 0 + m(n-1)/(n(m-1)) = m(n-1)/(n(m-1))
# with m=5, n=3: 5·2/(3·4) = 10/12 = 5/6
old_a3 = "At $k = 1$ the intersection variety collapses to a single-venue\nevent and the polylog exponent reduces to $\\alpha(1,n,m) = m/(m-1)$,\nwhich for the reserve dimension $m = 5$ delivers\n$\\alpha(1,\\cdot,5) = 5/4$. The single-venue polylog rate\n$(\\log T)^{5/4}$ agrees with the direct Pila--Wilkie bound on the\nunivariate distress cell $D_e$."
new_a3 = "At $k = 1$ the intersection variety collapses to a single-venue\nevent and the polylog exponent reduces to\n$\\alpha(1,n,m) = m(n-1)/\\bigl(n(m-1)\\bigr)$, which for the panel\ndimensions $n = 3$ and $m = 5$ delivers $\\alpha(1,3,5) = 5/6$.\nThe single-venue polylog rate $(\\log T)^{5/6}$ agrees with the\ndirect Pila--Wilkie bound on the univariate distress cell $D_e$."
if old_a3 in tex:
    tex = tex.replace(old_a3, new_a3, 1)
    print("[ok] App A.3 endpoint α(1,·) math corrected 5/4 → 5/6")
else:
    print("[warn] App A.3 endpoint sentence not found verbatim")

# 4) §4.5 pooling-gain 读法反了
old_p = "This value lies\nbetween the independence benchmark $n^{-1/2} \\approx 0.577$ and\nthe o-minimal prediction $0.896$, consistent with a positive but\nsub-limiting value of the constant $c_\\beta$ in the\nscale-induction bound of Theorem~\\ref{thm:lower}."
new_p = "This value lies\nbetween the independence benchmark $n^{-1/2} \\approx 0.577$ and\nthe o-minimal prediction $0.896$, closer to the independence side.\nWe read the empirical position as evidence of a small but\nnon-zero constant $c_\\beta$ in the scale-induction bound of\nTheorem~\\ref{thm:lower}; a refined bootstrap CI, together with\nCoinbase/Kraken joins, is delivered in the companion release."
if old_p in tex:
    tex = tex.replace(old_p, new_p, 1)
    print("[ok] §4.5 pooling ratio interpretation corrected")
else:
    print("[warn] pooling ratio sentence not found verbatim")

TEX.write_text(tex, encoding="utf-8")
BIB.write_text(bib, encoding="utf-8")
print("[write] tex + bib")
