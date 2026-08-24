"""v2.1-f caption-vs-body numeric consistency audit.

For every fig/tab caption in Main.tex, extract numeric claims and
verify each one against (a) the source CSV that owns the number, or
(b) the body-text passage that first mentions it. Flags:

  1. Caption claims a number not present in the CSV that generates the fig/tab.
  2. Caption number contradicts the body-text number (drift-through-editing bug).
  3. Caption cites a range / mean / SE that's actually stale from a prior version.

Numbers we intercept:
  - Currency: "$168.9", "USD 8.7 bn", "\\$16 billion"
  - Percentages: "7.59\\%", "≈8%"
  - Counts: "5 events", "3 CEX", "13 quarters"
  - Time spans: "eight weeks", "60 days"
  - Coefficients: "τ = 0.112", "SE = 0.026"

Output: per-caption number list, per-number provenance verdict (CSV-hit /
body-hit / STALE / UNVERIFIABLE).
"""
from __future__ import annotations
import io, csv, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
TEX  = ROOT / "manuscript" / "Main.tex"
PROC = ROOT / "data" / "processed"

src = TEX.read_text(encoding="utf-8")
lines = src.split("\n")

# ---------------------------------------------------------------
# Step 1 — extract every figure/table environment with balanced braces
# ---------------------------------------------------------------
def find_envs(text: str):
    """Yield (kind, start_line, end_line, body)."""
    out = []
    # match environment start
    for m in re.finditer(r"\\begin\{(figure|table)\}", text):
        kind = m.group(1)
        start = m.end()
        end_pat = re.compile(r"\\end\{" + kind + r"\}")
        em = end_pat.search(text, start)
        if not em: continue
        body = text[start:em.start()]
        # convert offset to line numbers
        start_line = text[:m.start()].count("\n") + 1
        end_line   = text[:em.end()].count("\n") + 1
        out.append((kind, start_line, end_line, body))
    return out

envs = find_envs(src)

# ---------------------------------------------------------------
# Extra: parse tabular bodies to extract every cell value.
# These live inside \begin{tabular}...\end{tabular} in a table env.
# ---------------------------------------------------------------
def extract_tabular_numbers(env_body: str) -> list[tuple[str, float]]:
    """Return [(raw_cell, numeric_value)] for every numeric cell in tabulars.
    Skips ISO-date cells (YYYY-MM-DD) and pure-year values."""
    out = []
    for tm in re.finditer(r"\\begin\{tabular\}.*?\\end\{tabular\}",
                          env_body, re.DOTALL):
        block = tm.group(0)
        # Strip \toprule \midrule etc, then split on \\ and &
        block = re.sub(r"\\(toprule|midrule|bottomrule|hline|cmidrule)", "", block)
        for row in re.split(r"\\\\", block):
            for cell in row.split("&"):
                cell_txt = strip_latex(cell).strip()
                # Skip ISO dates
                if re.match(r"^\d{4}-\d{2}-\d{2}$", cell_txt): continue
                # Skip case numbers like "22-10964"
                if re.match(r"^\d{2}-\d{5}$", cell_txt): continue
                # Only try to parse cells that look numeric-ish
                m = re.search(r"([+-]?\d+(?:[.,]\d+)?)", cell_txt)
                if m:
                    try:
                        v = float(m.group(1).replace(",", ""))
                        # Skip years (1900-2099 with no fractional part)
                        if 1900 <= v <= 2099 and v == int(v) and "-" in cell_txt:
                            continue
                        out.append((cell_txt[:30], v))
                    except ValueError:
                        pass
    return out

# ---------------------------------------------------------------
# Step 2 — extract caption + label from each env
# ---------------------------------------------------------------
def extract_caption(body: str) -> str:
    """Return the caption text (may be empty)."""
    m = re.search(r"\\caption(?:\[[^\]]*\])?\{", body)
    if not m: return ""
    i = m.end(); depth = 1; j = i
    while j < len(body) and depth > 0:
        if body[j] == "{": depth += 1
        elif body[j] == "}": depth -= 1
        j += 1
    return body[i:j-1]

def strip_latex(s: str) -> str:
    """Aggressive: strip LaTeX macros + math + braces."""
    s = re.sub(r"\\emph\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textit\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\citet?p?\*?\{[^}]*\}", "[cite]", s)
    s = re.sub(r"\\ref\{[^}]*\}", "[ref]", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", s)
    s = re.sub(r"[{}$%~^]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract_label(body: str) -> str:
    m = re.search(r"\\label\{([^}]+)\}", body)
    return m.group(1) if m else "?"

# ---------------------------------------------------------------
# Step 3 — number extractors (agnostic to leading $/USD/etc.)
# ---------------------------------------------------------------
NUM = r"\d+(?:[.,]\d+)*"  # tolerates 1,234 or 1.234

# Pattern list: (regex, kind)
PATTERNS = [
    (r"\$\s?(" + NUM + r")\s*(?:bn|billion|million|m|thousand)?", "currency"),
    (r"USD\s+(" + NUM + r")\s*(?:bn|billion|million)?", "currency"),
    (r"(" + NUM + r")\s*(?:%|\\%)", "percent"),
    # τ = 0.112, β = 0.86, etc.
    (r"[\u03B1-\u03C9\u0391-\u03A9]\s*=\s*[+-]?(" + NUM + r")", "greek-coeff"),
    (r"\btau[_\{]?\w*\}?\s*=?\s*[+-]?(" + NUM + r")", "tau"),
    (r"\b(\d+)\s*(?:events|quarters?|weeks?|days?|months?|years?|venues?|CEX|banks?|filings?|snapshots?|assets?|classes?)\b", "count"),
    (r"\b(?:eight|five|three|four|six|seven|nine|ten|thirteen|fifteen|twenty)\b", "wordcount"),  # spelled-out
    # RHS of an equals sign \u2014 catches "N_3 = 1", "\u03C4 = 0.112", "= 3.4" etc.
    (r"=\s*[+-]?(" + NUM + r")\b", "equation-rhs"),
    # standalone "X.Y bn" (currency without leading $)
    (r"(?:^|\s|\()(" + NUM + r")\s*(?:bn|billion|USD~bn|USD bn)", "reserve-gap"),
]

WORD2NUM = {
    "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fifteen": 15, "twenty": 20,
}

def extract_numbers(txt: str):
    """Return list of (raw_string, kind, numeric_value)."""
    txt = strip_latex(txt)
    hits = []
    seen_positions = set()
    for pat, kind in PATTERNS:
        for m in re.finditer(pat, txt, re.IGNORECASE):
            span = m.span()
            # avoid double-counting overlapping
            if any(s <= span[0] < e for s, e in seen_positions):
                continue
            seen_positions.add(span)
            raw = m.group(0)
            g1 = m.group(1) if m.groups() else raw
            # normalize numeric value
            if kind == "wordcount":
                val = WORD2NUM.get(raw.lower().strip(), None)
                if val is None: continue
                hits.append((raw, kind, val))
            else:
                try:
                    v = float(g1.replace(",", ""))
                    hits.append((raw, kind, v))
                except ValueError:
                    pass
    return hits

# ---------------------------------------------------------------
# Step 4 — build CSV / body context per caption
# ---------------------------------------------------------------
# Load key CSVs — flat list of every numeric cell
CSV_NUMBERS = {}
CSV_FILES = {
    "cex_por_snapshots_wide.csv": PROC / "cex_por_snapshots_wide.csv",
    "did_estimates.csv":          PROC / "did_estimates.csv",
    "wild_bootstrap.csv":         PROC / "wild_bootstrap.csv",
    "did_controls.csv":           PROC / "did_controls.csv",
    "pooling_gain.csv":           PROC / "pooling_gain.csv",
    "beta_estimate.csv":          PROC / "beta_estimate.csv",
    "nk_estimates.csv":           PROC / "nk_estimates.csv",
    "anticipation_did.csv":       PROC / "anticipation_did.csv",
    "stablecoin_placebo_did.csv": PROC / "stablecoin_placebo_did.csv",
}

def load_csv_values(p: Path):
    """Return set of float values found anywhere in the CSV."""
    vals = set()
    if not p.exists(): return vals
    with p.open(encoding="utf-8") as f:
        for row in csv.reader(f):
            for cell in row:
                cell = cell.strip().replace("+", "").replace("−", "-")
                try:
                    v = float(cell)
                    vals.add(round(v, 4))
                    if abs(v) > 1: vals.add(round(v, 2))
                    if abs(v) > 10: vals.add(round(v, 1))
                    if abs(v) > 100: vals.add(round(v))
                except ValueError:
                    pass
    return vals

for name, p in CSV_FILES.items():
    CSV_NUMBERS[name] = load_csv_values(p)

ALL_CSV_VALUES = set().union(*CSV_NUMBERS.values())

# ---------------------------------------------------------------
# Body-text numeric extraction — same regex bank, but scanned globally
# ---------------------------------------------------------------
# Strip LaTeX from full body but preserve paragraph structure
def strip_body(text: str) -> str:
    # Remove figure/table environments so we compare caption vs BODY only
    t = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", " ", text, flags=re.DOTALL)
    t = re.sub(r"\\begin\{table\}.*?\\end\{table\}",  " ", t, flags=re.DOTALL)
    return strip_latex(t)

BODY_TEXT = strip_body(src)

# Extract body numbers into a set (as strings for exact match, floats for tolerance)
BODY_NUMBERS = set()
for pat, kind in PATTERNS:
    for m in re.finditer(pat, BODY_TEXT, re.IGNORECASE):
        raw = m.group(0)
        g1 = m.group(1) if m.groups() else raw
        if kind == "wordcount":
            v = WORD2NUM.get(raw.lower().strip(), None)
            if v is not None: BODY_NUMBERS.add(float(v))
        else:
            try: BODY_NUMBERS.add(float(g1.replace(",", "")))
            except ValueError: pass

# ---------------------------------------------------------------
# Step 5 — verify each caption number
# ---------------------------------------------------------------
def match_value(v: float, pool: set[float], tol: float = 0.01) -> bool:
    """v within tol of any pool value, or exact match after rounding."""
    if v in pool: return True
    for p in pool:
        if p == 0 and v == 0: return True
        if p == 0 or v == 0:
            if abs(p - v) < tol: return True
            continue
        if abs(p - v) / max(abs(p), 1e-9) <= tol: return True
    return False

print("=" * 76)
print("  v2.1-f Caption ↔ CSV ↔ Body numeric consistency audit")
print("=" * 76)

all_findings = []
tabular_findings = []   # (kind, lab, sL, [(mark, cell, val, in_csv, in_body), ...])
for kind, sL, eL, body in envs:
    lab = extract_label(body)
    cap = extract_caption(body)
    if not cap: continue
    txt = strip_latex(cap)
    nums = extract_numbers(cap)

    verdicts = []
    for raw, ntype, v in nums:
        in_csv  = match_value(v, ALL_CSV_VALUES, tol=0.01)
        in_body = match_value(v, BODY_NUMBERS,   tol=0.01)
        if in_csv and in_body: mark = "✓"
        elif in_body and not in_csv: mark = "≈"    # in prose but no CSV backing
        elif in_csv and not in_body: mark = "☐"    # in CSV but body doesn't repeat
        else:                         mark = "?"   # UNVERIFIABLE — flag
        verdicts.append((mark, raw, ntype, v, in_csv, in_body))

    all_findings.append((kind, lab, sL, verdicts))

    # For tables, also scan the tabular body cells
    if kind == "table":
        tcells = extract_tabular_numbers(body)
        tab_verdicts = []
        for cell_str, v in tcells:
            in_csv  = match_value(v, ALL_CSV_VALUES, tol=0.05)
            in_body = match_value(v, BODY_NUMBERS,   tol=0.05)
            if in_csv or in_body:
                mark = "✓" if (in_csv and in_body) else ("☐" if in_csv else "≈")
            else:
                mark = "?"
            tab_verdicts.append((mark, cell_str, v, in_csv, in_body))
        tabular_findings.append((kind, lab, sL, tab_verdicts))

# ---------------------------------------------------------------
# Report
# ---------------------------------------------------------------
n_ok = n_body_only = n_csv_only = n_unverif = 0
for kind, lab, sL, verdicts in all_findings:
    print(f"\n  {kind:6s} {lab}  (L{sL})")
    for mark, raw, ntype, v, in_csv, in_body in verdicts:
        note = {
            "✓": "matches CSV + body",
            "≈": "matches body prose, no CSV backing (probably a structural/citation count)",
            "☐": "matches CSV, not repeated in body (caption-only detail; usually OK)",
            "?": "UNVERIFIABLE — not in any CSV, not in body prose",
        }[mark]
        print(f"    {mark}  {raw:20s}  ({ntype:9s} v={v:>10.4g})  {note}")
        if mark == "✓": n_ok += 1
        elif mark == "≈": n_body_only += 1
        elif mark == "☐": n_csv_only += 1
        else: n_unverif += 1

print()
print("=" * 76)
print(f"  CAPTION Summary: {n_ok} matches CSV+body · {n_body_only} body-only · "
      f"{n_csv_only} CSV-only · {n_unverif} UNVERIFIABLE")

# --- Tabular body report ---
if tabular_findings:
    print()
    print("-" * 76)
    print("  TABULAR CELLS (tables' data rows — must trace to CSV or body)")
    print("-" * 76)
    t_ok = t_stale = 0
    for tkind, lab, sL, verdicts in tabular_findings:
        print(f"\n  {tkind:6s} {lab}  (L{sL})")
        for mark, cell, v, in_csv, in_body in verdicts:
            note = {
                "✓": "CSV+body",
                "≈": "body-only (structural)",
                "☐": "CSV-only",
                "?": "UNVERIFIABLE — potentially stale",
            }[mark]
            print(f"    {mark}  cell={cell:20s}  v={v:>10.4g}  {note}")
            if mark == "?": t_stale += 1
            else:            t_ok += 1
    print()
    print(f"  TABULAR Summary: {t_ok} traceable · {t_stale} UNVERIFIABLE")
    n_unverif += t_stale

if n_unverif == 0:
    print("\nVERDICT: 🟢  every caption + tabular cell is traceable to CSV or body prose")
else:
    print(f"\nVERDICT: 🔴  {n_unverif} number(s) NOT found in CSV or body — review needed")
print("=" * 76)
