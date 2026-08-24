"""List all cite keys used in tex, and their occurrence line numbers."""
import re
from pathlib import Path
TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex").read_text(encoding="utf-8")
BIB = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/refs.bib").read_text(encoding="utf-8")

# In tex
lines = TEX.split("\n")
used = {}
for i, line in enumerate(lines, 1):
    for m in re.finditer(r"\\cite[a-z]*\*?(?:\[[^\]]*\])?\{([^}]+)\}", line):
        for k in m.group(1).split(","):
            k = k.strip()
            used.setdefault(k, []).append(i)

# In bib
bib_keys = set(re.findall(r"@\w+\{([^,]+),", BIB))

print(f"[bib] {len(bib_keys)} entries")
print(f"[tex] {len(used)} unique keys cited")
print()
print("=== Bib keys used in tex (with line #) ===")
for k in sorted(used):
    exists = "✓" if k in bib_keys else "✗ MISSING"
    print(f"  {exists} {k:45s} @ lines {used[k][:5]}")

print()
print("=== Orphan bib keys (in bib but NOT cited) ===")
for k in sorted(bib_keys - set(used)):
    print(f"  · {k}")
