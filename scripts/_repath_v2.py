"""Rewrite all hard-coded v0.1 paths to relative-to-script-parent."""
from pathlib import Path
import re

SCRIPTS = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/scripts")

# For each script:
# - locate the hard-coded absolute Path("E:/... /cex_contagion_v0.1/...")
# - rewrite to use Path(__file__).resolve().parent.parent -- the v2.0 root -- appended with the same tail

# Patterns to catch:
#   BASE = Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root
#   BASE = Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root
#   BASE = Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root

PAT = re.compile(
    r'(BASE\s*=\s*)Path\(r?"E:/[^"]*?cex_contagion_v0\.1((?:/[^"]*)?)"\)'
)

REPLACEMENT = r'\1Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root\n_TAIL = r"\2".lstrip("/")\nif _TAIL:\n    BASE = BASE / _TAIL'

def fix(path):
    src = path.read_text(encoding="utf-8")
    orig = src
    m = PAT.search(src)
    if not m:
        return False, "no match"
    tail = m.group(2) or ""
    tail_stripped = tail.lstrip("/")
    if tail_stripped:
        # Use a compact chained form
        new = f'BASE = Path(__file__).resolve().parent.parent / r"{tail_stripped}"  # cex_contagion_v2.0 root'
    else:
        new = 'BASE = Path(__file__).resolve().parent.parent  # cex_contagion_v2.0 root'
    src = PAT.sub(new, src)
    if src == orig:
        return False, "no change"
    path.write_text(src, encoding="utf-8")
    return True, "ok"

for p in sorted(SCRIPTS.glob("*.py")):
    ok, msg = fix(p)
    if ok:
        print(f"[fixed] {p.name}")
    elif msg != "no match":
        print(f"[?]     {p.name}: {msg}")
