"""Rewrite Theorem <-> Proposition thm:lower refs after downgrade."""
from pathlib import Path
import re
TEX = Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/main_eca_v2.tex")
c = TEX.read_text(encoding="utf-8")

# Match "Theorem~\ref{thm:lower}" or "Theorem \ref{thm:lower}"
# and rewrite to "Proposition~\ref{thm:lower}" — except the App proof section header
# We keep the app section header intact (say Proof of the wild-regime rate).

# Replace "Theorems~\ref{thm:prior}--\ref{thm:lower}" specially → keep Theorem umbrella intact
# but change trailing thm:lower to prop:lower would break; the label is still thm:lower, so
# just leave the plural "Theorems" form alone (it's admissible loosely).

# General rule: change "Theorem~\ref{thm:lower}" (singular) to "Proposition~\ref{thm:lower}"
c2 = re.sub(r"Theorem~\\ref\{thm:lower\}", r"Proposition~\\ref{thm:lower}", c)

# Also handle "Theorem \\ref" (space variant)
c2 = re.sub(r"Theorem \\ref\{thm:lower\}", r"Proposition \\ref{thm:lower}", c2)

# App section header currently reads: "\section{Proof of Theorem~\ref{thm:lower} (Wild-regime ..."
# Change label there — since the object is now a Proposition, but the proof appendix
# is still a proof-of-proposition. Change section title to "Argument for ...".
c2 = c2.replace(
    r"\section{Proof of Theorem~\ref{thm:lower} (Wild-regime",
    r"\section{Argument for Proposition~\ref{thm:lower} (Wild-regime",
)
# Similarly fix "Proof of Theorem~\ref{thm:prior}" and "thm:sticky" stay as Theorem (still theorems)

# Also change explicit references to "wild-regime lower bound of Theorem" mid-sentence
# now correctly says Proposition
# Change: "wild-regime lower bound of Theorem~..." lines were already caught by regex above.

TEX.write_text(c2, encoding="utf-8")

# quick post-check
n_thm = len(re.findall(r"Theorem~\\ref\{thm:lower\}", c2))
n_prop = len(re.findall(r"Proposition~\\ref\{thm:lower\}", c2))
print(f"[remaining] Theorem~\\ref{{thm:lower}} = {n_thm}")
print(f"[updated]  Proposition~\\ref{{thm:lower}} = {n_prop}")
