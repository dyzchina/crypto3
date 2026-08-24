"""check_ownership.py — script → output single-owner enforcement.

Reads docs/script_output_registry.md and verifies:

  1. Every listed path is written by AT MOST ONE production script (parsed
     from the "Owned artifacts" tables).

  2. Every production script's actual write set (statically scanned from its
     source) is a subset of what the registry declares — i.e. no script
     writes an undeclared path.

  3. Every declared path physically exists on disk after a full run_all.sh
     (soft warning; may be skipped in a fresh checkout with no build yet).

Ownership violations are the root cause of v2.1-c: two scripts wrote the
same canonical PDF from different specifications, and the audit's
before/after snapshot exposed the conflict. This check fires that same
alarm at commit-time instead of replication-audit-time.

Exit codes:
  0 — clean
  1 — declared conflicts (registry lists same path under 2+ scripts)
  2 — undeclared writes (script writes a path not in registry)
  3 — both

Run:
  python scripts/check_ownership.py
"""
from __future__ import annotations
import io, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "docs" / "script_output_registry.md"
SCRIPTS_DIR = ROOT / "scripts"

# Production scripts under the ownership contract. Diagnostic helpers
# (leading underscore) and read-only utilities are exempt.
PRODUCTION_SCRIPTS = [
    "aggregate_por.py", "anticipation_did.py", "beta_estimate.py",
    "build_fig5_algorithm.py", "build_manifest.py",
    "did_controls.py", "did_regression.py", "estimator_nk.py",
    "fetch_bankruptcy_dockets.py", "fig4_v2_dual_threshold.py",
    "fig_event_timeline.py", "figure_01_v04.py",
    "pull_coinbase_10q.py", "pull_defillama_cex.py",
    "stablecoin_placebo_did.py", "wild_bootstrap.py",
]
# wordcount.py and loo_headline.py print only; they own nothing.

# --------------------------------------------------------------------
# Step 1: parse docs/script_output_registry.md
# --------------------------------------------------------------------
def parse_registry() -> dict[str, list[str]]:
    """Return {script.py: [artifact, ...]}. Deduped."""
    text = REGISTRY.read_text(encoding="utf-8")
    owned: dict[str, list[str]] = {}
    # Rows look like `| ` + backticked script + ` | ` + `<one or more backticked artifacts>`  + ` |`
    row_re = re.compile(r"^\|\s*`([^`]+\.py)`\s*\|\s*(.+?)\s*\|\s*$", re.M)
    for m in row_re.finditer(text):
        script = m.group(1)
        cell = m.group(2)
        # Pull every `...` from the cell — those are the declared artifacts.
        arts = [a for a in re.findall(r"`([^`]+)`", cell)
                if any(ext in a for ext in (".csv", ".pdf", ".txt", ".md", ".json",
                                            ".sha256", ".tex"))]
        owned.setdefault(script, []).extend(arts)
    return {k: sorted(set(v)) for k, v in owned.items()}

# --------------------------------------------------------------------
# Step 2: extract writes actually performed by each production script
# --------------------------------------------------------------------
WRITE_PATTERNS = [
    r"savefig\(\s*(?:\w+|[\"'][^\"']+[\"'])",                    # matplotlib
    r"\.to_csv\(\s*(?:\w+|[\"'][^\"']+[\"'])",                   # pandas
    r"\.write_text\(",                                            # pathlib
    r"\.write_bytes\(",                                           # pathlib
    r"open\(\s*(?:\w+|[\"'][^\"']+[\"'])[^)]*[\"'](?:w|wb|wt|a|at|ab)",  # builtin
    r"\.open\([^)]*[\"'](?:w|wb|wt|a|at|ab)",                    # pathlib .open('w')
    r"save_json\(",                                               # project-local helper
    r"json\.dump\(",                                              # stdlib json.dump(obj, f)
]
WRITE_ANY = re.compile("|".join(WRITE_PATTERNS))

def build_var_map(src: str) -> dict[str, str]:
    """Extract var = BASE/ROOT/.../"foo"/"bar" → var: "foo/bar"."""
    var_map = {}
    pat = re.compile(
        r"^\s*(\w+)\s*=\s*(?:BASE|ROOT|OUT_DIR|PROC|FIGS|DATA_OUT|PROCESSED)\s*(/\s*[\"'][^\"'\n]+[\"'](?:\s*/\s*[\"'][^\"'\n]+[\"'])*)",
        re.M,
    )
    for m in pat.finditer(src):
        parts = re.findall(r"[\"']([^\"'\n]+)[\"']", m.group(2))
        if parts:
            var_map[m.group(1)] = "/".join(parts)
    # Also handle var = Path(r"absolute/path.pdf")
    for m in re.finditer(r'^\s*(\w+)\s*=\s*Path\(\s*r?[\"\']([^\"\'\n]+)[\"\']', src, re.M):
        var_map[m.group(1)] = m.group(2)
    # And direct string literal
    for m in re.finditer(r'^\s*(\w+)\s*=\s*[\"\']([^\"\'\n]+\.(?:csv|pdf|txt|md|json|sha256|tex))[\"\']', src, re.M):
        var_map[m.group(1)] = m.group(2)
    return var_map

def normalize_path(p: str) -> str:
    """Return path relative to project root, forward slashes, no leading ./."""
    p = p.replace("\\", "/")
    # Strip absolute prefix if present
    for prefix in ("E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/",):
        if p.startswith(prefix):
            p = p[len(prefix):]
    return p.lstrip("./")

def scan_writes(script: str) -> set[str]:
    """Static scan: return set of declared write-target paths for one script."""
    src = (SCRIPTS_DIR / script).read_text(encoding="utf-8")
    var_map = build_var_map(src)
    writes: set[str] = set()

    # 1) savefig(X) / to_csv(X) — X is variable or literal string
    for verb in ("savefig", "to_csv"):
        for m in re.finditer(rf"{verb}\(\s*([^\s,)]+)", src):
            arg = m.group(1).strip()
            if arg.startswith(("'", '"')):
                writes.add(arg.strip("'\""))
            elif arg in var_map:
                writes.add(var_map[arg])

    # 2) X.write_text() / X.write_bytes() — X is variable
    for m in re.finditer(r"(\w+)\.write_text\(|\b(\w+)\.write_bytes\(", src):
        var = m.group(1) or m.group(2)
        if var in var_map:
            writes.add(var_map[var])

    # 3) open(X, "w"...)  or (P / "foo.csv").open("w"...)
    for m in re.finditer(r"open\(\s*([^\s,)]+)[^)]*[\"'](?:w|wb|wt|a|at|ab)[\"']", src):
        arg = m.group(1).strip()
        if arg.startswith(("'", '"')):
            writes.add(arg.strip("'\""))
        elif arg in var_map:
            writes.add(var_map[arg])

    # 4) (PROC / "foo.csv").open("w") — inline-constructed Path
    for m in re.finditer(
        r"\(\s*(?:BASE|ROOT|OUT_DIR|PROC|FIGS|DATA_OUT|PROCESSED)\s*/\s*[\"']([^\"'\n]+)[\"']\s*\)\.open\([^)]*[\"'](?:w|wb|wt|a|at|ab)",
        src,
    ):
        writes.add(m.group(1))

    # 5) ROOT / "path/to/file.csv" as first arg to to_csv
    for m in re.finditer(
        r"\.to_csv\(\s*(?:BASE|ROOT|OUT_DIR|PROC|FIGS)\s*/\s*[\"']([^\"'\n]+)[\"']",
        src,
    ):
        writes.add(m.group(1))

    # 6) save_json(var, ...) — project helper. First arg is the path.
    for m in re.finditer(r"save_json\(\s*([^\s,)]+)", src):
        arg = m.group(1).strip()
        if arg.startswith(("'", '"')):
            writes.add(arg.strip("'\""))
        elif arg in var_map:
            writes.add(var_map[arg])
        # dynamic f-string forms (e.g. f"{venue}_quarterly.json") are inspected but
        # not resolved — they're covered by the declared registry entry.

    return {normalize_path(p) for p in writes}

# --------------------------------------------------------------------
# Step 3: enforce
# --------------------------------------------------------------------
def main() -> int:
    print("=" * 74)
    print("  Script → Output Ownership Check  (docs/script_output_registry.md)")
    print("=" * 74)

    registry = parse_registry()

    # Invariant 1: no path declared under two scripts
    inverse: dict[str, list[str]] = {}
    for script, arts in registry.items():
        for a in arts:
            inverse.setdefault(normalize_path(a), []).append(script)
    declared_conflicts = {p: s for p, s in inverse.items() if len(s) >= 2}

    # Invariant 2: each script's static write set ⊆ its declared set
    undeclared: dict[str, list[str]] = {}
    for script in PRODUCTION_SCRIPTS:
        actual = scan_writes(script)
        declared = {normalize_path(p) for p in registry.get(script, [])}
        # Filter static-scan noise: paths that don't look like real artifact filenames
        actual = {p for p in actual if "/" in p and any(
            p.endswith(ext) for ext in (".csv", ".pdf", ".txt", ".md", ".json", ".sha256", ".tex")
        )}
        extra = actual - declared
        if extra:
            undeclared[script] = sorted(extra)

    # ---- Report ----
    if declared_conflicts:
        print("\n[FAIL] Invariant 1 — declared conflicts (registry lists path 2+ times):")
        for path, scripts in sorted(declared_conflicts.items()):
            print(f"  ✗ {path}")
            for s in scripts:
                print(f"      ← {s}")
    else:
        print("\n[PASS] Invariant 1 — every registered artifact has exactly one owner.")

    if undeclared:
        print("\n[FAIL] Invariant 2 — scripts write paths not in registry:")
        for script, extras in sorted(undeclared.items()):
            print(f"  ✗ {script}")
            for e in extras:
                print(f"      wrote {e}  (not declared)")
    else:
        print("[PASS] Invariant 2 — every script's writes are declared in registry.")

    # ---- Existence check (advisory) ----
    print("\n[INFO] Advisory disk-existence check for declared artifacts:")
    n_ok = n_missing = 0
    for script, arts in sorted(registry.items()):
        for a in arts:
            path = ROOT / normalize_path(a)
            if path.exists():
                n_ok += 1
            else:
                n_missing += 1
    print(f"  {n_ok} present · {n_missing} missing on disk "
          f"(missing may be OK on fresh checkouts)")

    # ---- Exit ----
    print("\n" + "=" * 74)
    exit_code = 0
    if declared_conflicts: exit_code |= 1
    if undeclared:         exit_code |= 2
    if exit_code == 0:
        print("VERDICT: 🟢  OWNERSHIP CLEAN  ·  single-writer contract holds")
    else:
        print(f"VERDICT: 🔴  OWNERSHIP VIOLATION  (exit code {exit_code})")
    print("=" * 74)
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
