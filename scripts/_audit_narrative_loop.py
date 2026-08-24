"""_audit_narrative_loop.py -- three-way theme matrix (abstract / intro / conclusion)."""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('manuscript/Main.tex', 'r', encoding='utf-8').read()
lines = src.split('\n')

# Auto-locate section boundaries (don't hard-code line numbers)
abstract_start = next(i for i, l in enumerate(lines) if 'Five bankruptcies within seven months' in l)
abstract_end   = abstract_start + 15  # ~14 lines to include full paragraph
intro_start    = next(i for i, l in enumerate(lines) if r'\section{Introduction}' in l)
# Intro ends where the next \section{...} begins (i.e. §2 Setup)
intro_end      = next(i for i, l in enumerate(lines[intro_start+1:], start=intro_start+1)
                      if l.startswith(r'\section{'))
concl_start    = next(i for i, l in enumerate(lines) if r'\section{Conclusion}' in l)
# Conclusion ends at Acknowledgements (if present) or at \bibliographystyle
try:
    ack_start = next(i for i, l in enumerate(lines) if r'\subsection*{Acknowledgements}' in l)
except StopIteration:
    ack_start = next(i for i, l in enumerate(lines) if r'\bibliographystyle' in l)

abstract   = '\n'.join(lines[abstract_start:abstract_end])
intro      = '\n'.join(lines[intro_start:intro_end])
conclusion = '\n'.join(lines[concl_start:ack_start])

def strip_latex(t):
    t = re.sub(r'\\emph\{([^}]*)\}',   r'\1', t)
    t = re.sub(r'\\textbf\{([^}]*)\}', r'\1', t)
    t = re.sub(r'\\citet?p?\*?\{[^}]*\}', '[cite]', t)
    t = re.sub(r'\\ref\{[^}]*\}', '[ref]', t)
    t = re.sub(r'\\[a-zA-Z]+\*?', ' ', t)
    t = re.sub(r'[{}$%~^_#]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

wc = lambda t: len(strip_latex(t).split())
print(f"Abstract:     {wc(abstract):>4} words")
print(f"Introduction: {wc(intro):>4} words")
print(f"Conclusion:   {wc(conclusion):>4} words")
print()

THEMES = {
    'Five bankruptcies / 7 months':       [r'seven months', r'Five\s+bank', r'five\s+centralized'],
    'Stablecoin placebo':                 [r'stablecoin[- ]?issuer', r'stablecoin placebo', r'ten[- ]?issuer'],
    'Real-time audit line':               [r'audit line', r'real[- ]time.*audit'],
    'State-contingent capital buffer':    [r'capital buffer', r'capital multiplier'],
    'Coordinated-disclosure recipe':      [r'coordinated[- ]disclosure', r'disclosure recipe'],
    'DiD estimator':                      [r'difference[- ]in[- ]differences', r'\bDiD\b', r'\bTWFE\b'],
    'Wild-cluster bootstrap':             [r'wild[- ]cluster', r'bootstrap'],
    'BTC/VIX controls':                   [r'\bVIX\b', r'common[- ]risk[- ]factor'],
    'Persistence exponent beta':          [r'persistence exponent', r'0\.86', r'0\.858'],
    'Coinbase / Kraken limitation':       [r'Coinbase', r'Kraken', r'top[- ]five venues'],
    'MiCA extension':                     [r'MiCA'],
    'DefiLlama':                          [r'DefiLlama'],
    'Directional tube':                   [r'directional[- ]tube'],
    '$16 billion aggregate':              [r'\$16\s*billion'],
    'ETF approval (spot Bitcoin)':        [r'ETF approval', r'spot[- ]Bitcoin ETF'],
    'N_3 = 1 signal':                     [r'N_?3\s*=\s*1', r'three[- ]venue\s+full\s+intersection'],
    'Crossover k*':                       [r'crossover', r'k\^\{?\\?ast', r'k\^\*'],
    'Reserve-simplex product':            [r'reserve[- ]simplex'],
    'Pila-Wilkie':                        [r'Pila[-]{1,2}Wilkie'],
    'O-minimal':                          [r'o[- ]minimal'],
    'Polylog prior':                      [r'polylog'],
    'Wild regime / power-of-horizon':     [r'wild[- ]regime', r'power[- ]of[- ]horizon'],
    'Intersection frontier':              [r'intersection frontier'],
    'BCBS / FSB / Aldasoro':              [r'BCBS', r'FSB', r'Aldasoro'],
    'PW is by ANALOGY':                   [r'by analogy'],
    'Three-venue panel':                  [r'three[- ]venue', r'3[- ]venue'],
    '13-quarter horizon':                 [r'thirteen[- ]quarter', r'13[- ]quarter'],
}

def has(pats, txt):
    return any(re.search(p, txt, re.IGNORECASE) for p in pats)

print(f"{'theme':38s}  {'Abst':^5}  {'Intro':^5}  {'Conc':^5}  verdict")
print("-" * 90)

closed = intro_gap = conc_gap = abst_only = conc_only = intro_only = none = 0
issues = []
for theme, pats in THEMES.items():
    a = has(pats, abstract); i = has(pats, intro); c = has(pats, conclusion)
    if a and i and c: v = "✓ closed loop"; closed += 1
    elif not a and i and c: v = "☐ intro/conc (abstract space OK)"
    elif not a and not i and c: v = "🔴 CONC-ONLY"; conc_only += 1; issues.append(theme)
    elif a and not i and not c: v = "🔴 ABST-ONLY"; abst_only += 1; issues.append(theme)
    elif a and not i and c: v = "⚠ INTRO gap"; intro_gap += 1; issues.append(theme)
    elif a and i and not c: v = "⚠ CONC gap"; conc_gap += 1; issues.append(theme)
    elif not a and i and not c: v = "☐ intro only"; intro_only += 1
    else: v = "☐ none"; none += 1
    print(f"  {theme:38s}  {('●' if a else '·'):^5}  {('●' if i else '·'):^5}  {('●' if c else '·'):^5}  {v}")

print()
print(f"CLOSED LOOP (all three):       {closed}")
print(f"Intro/Conc (abstract-space):   {sum(1 for t,p in THEMES.items() if not has(p,abstract) and has(p,intro) and has(p,conclusion))}")
print(f"🔴 real gaps (loop broken):    {abst_only + conc_only + intro_gap + conc_gap}")
if issues:
    print(f"  gap themes: {', '.join(issues)}")
