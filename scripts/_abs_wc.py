import re
# ≤100 词 · 保留 5 spine 承诺:
# 1) hook (5 bankruptcies)
# 2) product-of-simplices + unlikely intersection
# 3) PW upper + heuristic lower + crossover
# 4) ETF approval + stablecoin placebo
# 5) real-time diagnostic + illustrative buffer

draft = """Five bankruptcies within seven months across the centralized-crypto perimeter exposed a gap in systemic risk measurement: most venues lack liquid equity, so equity-based indices cannot detect joint distress. This paper builds a supervisory diagnostic from public reserve compositions. Embedded in a product of simplices, simultaneous distress becomes an unlikely intersection in the o-minimality programme. A Pila-Wilkie polylog upper bound and a heuristic power-of-horizon lower rate yield a horizon-dependent crossover, an empirically testable prediction. Under a domain-prior threshold, the full three-venue intersection peaks in the spot-Bitcoin ETF approval quarter; a stablecoin placebo does not. The diagnostic is real-time computable and yields an illustrative capital buffer."""
words = re.findall(r"\b[A-Za-z][A-Za-z-]+\b", draft)
print(f"word count: {len(words)}")
print()
print(draft)
