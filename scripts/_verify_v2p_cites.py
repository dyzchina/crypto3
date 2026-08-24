import re
with open('E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.aux','rb') as f:
    aux = f.read().decode('utf-8', errors='replace')
cited = set(re.findall(r'\\bibcite\{([^}]+)\}', aux))
print(f'bibcite in aux = {len(cited)}')

with open('E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/refs.bib','rb') as f:
    bib = f.read().decode('utf-8', errors='replace')
in_bib = set(re.findall(r'@\w+\{([^,\s]+),', bib))
print(f'bib entries    = {len(in_bib)}')

with open('E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex','rb') as f:
    tex = f.read().decode('utf-8', errors='replace')
tex_cites = set()
for m in re.finditer(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])?\{([^}]+)\}', tex):
    for k in m.group(1).split(','):
        tex_cites.add(k.strip())
print(f'unique cite keys in tex = {len(tex_cites)}')
print(f'MISSING (tex cites not in bib) = {tex_cites - in_bib}')
print(f'ORPHANS (in bib not cited)     = {sorted(in_bib - tex_cites)}')
