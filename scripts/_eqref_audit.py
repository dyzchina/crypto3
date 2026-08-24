"""
v2.0-p equation-numbering & cross-reference audit.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import re
from pathlib import Path
from collections import defaultdict

TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")
with open(TEX, "rb") as f:
    c = f.read().decode("utf-8", errors="replace")

# ---- 1. Collect every \label{...} with line number
labels = {}          # key -> line
label_dupes = []
lines = c.split("\n")
for i, line in enumerate(lines, 1):
    for m in re.finditer(r"\\label\{([^}]+)\}", line):
        k = m.group(1)
        if k in labels:
            label_dupes.append((k, labels[k], i))
        labels[k] = i

# ---- 2. Collect every reference
refs = defaultdict(list)  # key -> [(line, kind), ...]
for i, line in enumerate(lines, 1):
    for m in re.finditer(r"\\(eqref|ref|pageref|Cref|autoref|cref)\{([^}]+)\}", line):
        kind = m.group(1)
        for k in m.group(2).split(","):
            k = k.strip()
            if k:
                refs[k].append((i, kind))

# ---- 3. Missing references (referenced but no label defined)
missing = sorted(set(refs.keys()) - set(labels.keys()))

# ---- 4. Orphan labels (defined but never referenced)
# eq: labels missing refs are a strong smell (numbered but unused)
# sec: labels are often navigational, less strict
orphans = sorted(set(labels.keys()) - set(refs.keys()))

# ---- 5. Environment-label prefix consistency
# Find every \begin{env}[...]\label{key} pattern
env_pat = re.compile(
    r"\\begin\{(theorem|proposition|definition|corollary|assumption|lemma)\}"
    r"(?:\[[^\]]*\])?\s*\\label\{([^}]+)\}"
)
env_expected_prefix = {
    "theorem": "thm:",
    "proposition": ["thm:", "prop:"],  # sometimes lower-bound proposition uses thm:
    "definition": "def:",
    "corollary": "cor:",
    "assumption": "ass:",
    "lemma": "lem:",
}
env_mismatch = []
env_hits = []
for m in env_pat.finditer(c):
    env, key = m.group(1), m.group(2)
    line_no = c[:m.start()].count("\n") + 1
    env_hits.append((line_no, env, key))
    expected = env_expected_prefix[env]
    if isinstance(expected, list):
        ok = any(key.startswith(p) for p in expected)
    else:
        ok = key.startswith(expected)
    if not ok:
        env_mismatch.append((line_no, env, key, expected))

# ---- 6. \eqref vs \ref for equations
# eq: labels should be referenced via \eqref, not \ref
eq_via_ref = []
for k in refs:
    if k.startswith("eq:"):
        for line_no, kind in refs[k]:
            if kind == "ref":
                eq_via_ref.append((line_no, k))
# thm:/prop:/def:/... labels should NOT use \eqref
nonhard = ("eq:",)
noneq_via_eqref = []
for k in refs:
    if not k.startswith(nonhard):
        for line_no, kind in refs[k]:
            if kind == "eqref":
                noneq_via_eqref.append((line_no, k))

# ---- 7. Count equations that carry a label vs that don't
# Rough: scan equation/align/gather/multline/subequations
labeled_eq_envs = 0
unlabeled_eq_envs = 0
eq_env_pat = re.compile(
    r"\\begin\{(equation|align|gather|multline|subequations)\*?\}(.*?)\\end\{\1\*?\}",
    re.DOTALL,
)
for m in eq_env_pat.finditer(c):
    body = m.group(2)
    if "\\label{" in body:
        labeled_eq_envs += 1
    else:
        # equation* / align* are deliberately unnumbered
        if m.group(1).endswith("*") or "*" in m.group(0)[:30]:
            continue
        unlabeled_eq_envs += 1

# ---- 8. numprint eq labels: count how many equations are numbered but unused
eq_labels = [k for k in labels if k.startswith("eq:")]
eq_unused = [k for k in eq_labels if k not in refs]

# ---- Report
print("=" * 70)
print("v2.0-p Equation numbering & cross-reference audit")
print("=" * 70)
print()
print(f"[LABELS]  {len(labels)} unique labels defined")
print(f"[REFS]    {len(refs)} unique keys referenced "
      f"({sum(len(v) for v in refs.values())} total \\ref/\\eqref sites)")
print(f"[ENV]     {len(env_hits)} thm/prop/def/cor/ass/lem environments with labels")
print(f"[EQ ENV]  {labeled_eq_envs} labeled equation envs, "
      f"{unlabeled_eq_envs} numbered but unlabeled")
print()

def section(title, items, formatter=str):
    print(f"--- {title} ({len(items)}) ---")
    if not items:
        print("   ✓ clean")
    else:
        for x in items[:30]:
            print(f"   • {formatter(x)}")
        if len(items) > 30:
            print(f"   ... (+{len(items)-30} more)")
    print()

section("C1. Duplicate labels", label_dupes,
        lambda t: f"{t[0]}  (defined @{t[1]}, redefined @{t[2]})")

section("C2. Missing references (referenced but not defined)", missing)

section("C3. Orphan labels — eq: only (defined but not referenced)", eq_unused)

section("C4. All orphan labels (any prefix)", orphans)

section("C5. Environment-label prefix mismatch", env_mismatch,
        lambda t: f"L{t[0]}  \\begin{{{t[1]}}}\\label{{{t[2]}}}  (expected prefix {t[3]})")

section("C7a. eq: labels referenced via \\ref (should use \\eqref)", eq_via_ref,
        lambda t: f"L{t[0]}  \\ref{{{t[1]}}}")

section("C7b. non-eq labels referenced via \\eqref (should use \\ref/\\Cref)",
        noneq_via_eqref,
        lambda t: f"L{t[0]}  \\eqref{{{t[1]}}}")

# ---- Environment inventory
print("--- Theorem/Prop/Def/... environment inventory ---")
by_env = defaultdict(list)
for line_no, env, key in env_hits:
    by_env[env].append((line_no, key))
for env in sorted(by_env):
    print(f"  [{env}]")
    for line_no, key in by_env[env]:
        n_refs = len(refs.get(key, []))
        mark = "✓" if n_refs else "✗ ORPHAN"
        print(f"    L{line_no:4d}  \\label{{{key}}}  refs={n_refs}  {mark}")
print()

# ---- Equation-label inventory
print("--- eq: label inventory (with reference count) ---")
for k in sorted(eq_labels, key=lambda x: labels[x]):
    n_refs = len(refs.get(k, []))
    mark = "✓" if n_refs else "✗ ORPHAN"
    print(f"  L{labels[k]:4d}  \\label{{{k}}}  refs={n_refs}  {mark}")
print()

# ---- Summary verdict
n_bad = (
    len(label_dupes) + len(missing) + len(eq_unused) + len(env_mismatch)
    + len(eq_via_ref) + len(noneq_via_eqref)
)
if n_bad == 0:
    print("=" * 70)
    print("VERDICT: 0 bugs — equation numbering & cross-refs are clean.")
    print("=" * 70)
else:
    print("=" * 70)
    print(f"VERDICT: {n_bad} issue(s) requiring fix.")
    print("=" * 70)
