"""_audit_bib.py — bib key coverage + cite frequency audit."""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

bib = open('manuscript/refs.bib', 'r', encoding='utf-8').read()
bib_keys = set(re.findall(r'@\w+\{([^,\s]+)', bib))
print(f"Bib entries: {len(bib_keys)}")

tex = open('manuscript/Main.tex', 'r', encoding='utf-8').read()
tex_nc = "\n".join(l for l in tex.split("\n") if not l.lstrip().startswith("%"))

cite_keys = set()
freq = {}
CITE = re.compile(r"\\cite[tp]?\*?\{([^}]+)\}")
for m in CITE.finditer(tex_nc):
    for k in m.group(1).split(','):
        k = k.strip()
        cite_keys.add(k)
        freq[k] = freq.get(k, 0) + 1

print(f"Distinct citation keys in tex: {len(cite_keys)}")
print()

missing = cite_keys - bib_keys
unused = bib_keys - cite_keys
if missing:
    print(f"🔴 CITED but NOT in bib ({len(missing)}):")
    for k in sorted(missing): print(f"   {k}")
else:
    print(f"✓ Every cited key is in bib ({len(cite_keys)}/{len(cite_keys)})")

if unused:
    print(f"\n⚠ In bib but NEVER cited ({len(unused)}):")
    for k in sorted(unused): print(f"   {k}")
else:
    print("\n✓ Every bib entry is cited")

print()
print("Cite frequency (all):")
for k, n in sorted(freq.items(), key=lambda x: -x[1]):
    print(f"  {n:>3}x  {k}")
