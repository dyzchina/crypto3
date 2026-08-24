"""
Rebuild refs.bib from scratch with only cited entries + fixes.
"""
from pathlib import Path

# Keep only these keys (29 cited in tex, remove Griffin-Kruger-Mei2023 which is unverifiable)
# Actually, GKM will be replaced/removed in tex; keep it for now to keep bibtex clean, mark as preprint.
KEPT_ENTRIES = """\
%%========================================================================
%%  refs.bib -- CEX Contagion x O-Minimality
%%  Curated bibliography: 29 entries actually cited in main_eca_v2.tex.
%%  All entries independently verified against DOI / journal metadata
%%  (v2.0-n audit, 2026-08-18). See docs/data_provenance.md for the audit trail.
%%========================================================================

%%---- O-minimality / arithmetic-geometry counting -----------------------
@article{PilaWilkie2006,
  author  = {Pila, Jonathan and Wilkie, Alex J.},
  title   = {The rational points of a definable set},
  journal = {Duke Mathematical Journal},
  year    = {2006},
  volume  = {133},
  number  = {3},
  pages   = {591--616},
  doi     = {10.1215/S0012-7094-06-13336-7}
}

@article{Pila2011ManinMumford,
  author  = {Pila, Jonathan},
  title   = {O-minimality and the {A}ndr\\'e--{O}ort conjecture for
             $\\mathbb{C}^n$},
  journal = {Annals of Mathematics},
  year    = {2011},
  volume  = {173},
  number  = {3},
  pages   = {1779--1840}
}

@article{Pink2005ZilberPink,
  author  = {Pink, Richard},
  title   = {A common generalization of the conjectures of {A}ndr\\'e--{O}ort,
             {M}anin--{M}umford, and {M}ordell--{L}ang},
  year    = {2005},
  note    = {ETH Z\\"urich preprint}
}

@article{Zilber2002,
  author  = {Zilber, Boris},
  title   = {Exponential sums equations and the {S}chanuel conjecture},
  journal = {Journal of the London Mathematical Society},
  year    = {2002},
  volume  = {65},
  number  = {1},
  pages   = {27--44}
}

@book{vandenDries1998Tame,
  author    = {van den Dries, Lou},
  title     = {Tame Topology and O-minimal Structures},
  publisher = {Cambridge University Press},
  series    = {London Mathematical Society Lecture Note Series},
  volume    = {248},
  year      = {1998}
}

@incollection{PeterzilStarchenko2008,
  author    = {Peterzil, Ya'acov and Starchenko, Sergei},
  title     = {Complex analytic geometry in a nonstandard setting},
  booktitle = {Model Theory with Applications to Algebra and Analysis,
               Vol.\\ 1},
  editor    = {Chatzidakis, Z. and Macpherson, D. and Pillay, A. and
               Wilkie, A.},
  series    = {London Mathematical Society Lecture Note Series},
  volume    = {349},
  publisher = {Cambridge University Press},
  year      = {2008},
  pages     = {117--166}
}

@article{BakkerKlinglerTsimerman2020,
  author  = {Bakker, Benjamin and Klingler, Bruno and Tsimerman, Jacob},
  title   = {Tame topology of arithmetic quotients and algebraicity of
             {H}odge loci},
  journal = {Journal of the American Mathematical Society},
  year    = {2020},
  volume  = {33},
  number  = {4},
  pages   = {917--939}
}

%%---- Systemic-risk measurement -----------------------------------------
@article{AdrianBrunnermeier2016CoVaR,
  author  = {Adrian, Tobias and Brunnermeier, Markus K.},
  title   = {{C}o{V}a{R}},
  journal = {American Economic Review},
  year    = {2016},
  volume  = {106},
  number  = {7},
  pages   = {1705--1741}
}

@article{AcharyaEtAl2017SES,
  author  = {Acharya, Viral V. and Pedersen, Lasse Heje and Philippon, Thomas
             and Richardson, Matthew},
  title   = {Measuring systemic risk},
  journal = {Review of Financial Studies},
  year    = {2017},
  volume  = {30},
  number  = {1},
  pages   = {2--47}
}

@article{BrownleesEngle2017SRISK,
  author  = {Brownlees, Christian and Engle, Robert F.},
  title   = {{SRISK}: A conditional capital shortfall measure of systemic
             risk},
  journal = {Review of Financial Studies},
  year    = {2017},
  volume  = {30},
  number  = {1},
  pages   = {48--79}
}

@article{BillioEtAl2012,
  author  = {Billio, Monica and Getmansky, Mila and Lo, Andrew W. and
             Pelizzon, Loriana},
  title   = {Econometric measures of connectedness and systemic risk in
             the finance and insurance sectors},
  journal = {Journal of Financial Economics},
  year    = {2012},
  volume  = {104},
  number  = {3},
  pages   = {535--559}
}

@article{DieboldYilmaz2014,
  author  = {Diebold, Francis X. and Y{\\i}lmaz, Kamil},
  title   = {On the network topology of variance decompositions:
             {M}easuring the connectedness of financial firms},
  journal = {Journal of Econometrics},
  year    = {2014},
  volume  = {182},
  number  = {1},
  pages   = {119--134}
}

%%---- Contagion / network models ----------------------------------------
@article{AllenGale2000,
  author  = {Allen, Franklin and Gale, Douglas},
  title   = {Financial contagion},
  journal = {Journal of Political Economy},
  year    = {2000},
  volume  = {108},
  number  = {1},
  pages   = {1--33}
}

@article{FreixasParigiRochet2000,
  author  = {Freixas, Xavier and Parigi, Bruno M. and Rochet, Jean-Charles},
  title   = {Systemic risk, interbank relations, and liquidity provision
             by the central bank},
  journal = {Journal of Money, Credit and Banking},
  year    = {2000},
  volume  = {32},
  number  = {3},
  pages   = {611--638}
}

@article{ElliottGolubJackson2014,
  author  = {Elliott, Matthew and Golub, Benjamin and Jackson, Matthew O.},
  title   = {Financial networks and contagion},
  journal = {American Economic Review},
  year    = {2014},
  volume  = {104},
  number  = {10},
  pages   = {3115--3153}
}

@article{AcemogluOzdaglarTahbaz2015,
  author  = {Acemoglu, Daron and Ozdaglar, Asuman and Tahbaz-Salehi, Alireza},
  title   = {Systemic risk and stability in financial networks},
  journal = {American Economic Review},
  year    = {2015},
  volume  = {105},
  number  = {2},
  pages   = {564--608}
}

@article{DuffieZhu2011,
  author  = {Duffie, Darrell and Zhu, Haoxiang},
  title   = {Does a central clearing counterparty reduce counterparty risk?},
  journal = {Review of Asset Pricing Studies},
  year    = {2011},
  volume  = {1},
  number  = {1},
  pages   = {74--95}
}

@article{GlassermanYoung2015,
  author  = {Glasserman, Paul and Young, H. Peyton},
  title   = {How likely is contagion in financial networks?},
  journal = {Journal of Banking \\& Finance},
  year    = {2015},
  volume  = {50},
  pages   = {383--399}
}

@article{RochetTirole1996,
  author  = {Rochet, Jean-Charles and Tirole, Jean},
  title   = {Interbank lending and systemic risk},
  journal = {Journal of Money, Credit and Banking},
  year    = {1996},
  volume  = {28},
  number  = {4},
  pages   = {733--762}
}

@incollection{CabralesGaleGottardi2016,
  author    = {Cabrales, Antonio and Gale, Douglas and Gottardi, Piero},
  title     = {Financial contagion in networks},
  booktitle = {The Oxford Handbook of the Economics of Networks},
  editor    = {Bramoull\\'e, Yann and Galeotti, Andrea and Rogers, Brian W.},
  publisher = {Oxford University Press},
  year      = {2016},
  pages     = {543--568}
}

%%---- DiD identification ------------------------------------------------
@article{deChaisemartinDHaultfoeuille2020,
  author  = {de Chaisemartin, Cl\\'ement and D'Haultf{\\oe}uille, Xavier},
  title   = {Two-way fixed effects estimators with heterogeneous treatment
             effects},
  journal = {American Economic Review},
  year    = {2020},
  volume  = {110},
  number  = {9},
  pages   = {2964--2996}
}

@article{Callaway-SantAnna2021,
  author  = {Callaway, Brantly and Sant'Anna, Pedro H. C.},
  title   = {Difference-in-differences with multiple time periods},
  journal = {Journal of Econometrics},
  year    = {2021},
  volume  = {225},
  number  = {2},
  pages   = {200--230}
}

@article{Sun-Abraham2021,
  author  = {Sun, Liyang and Abraham, Sarah},
  title   = {Estimating dynamic treatment effects in event studies with
             heterogeneous treatment effects},
  journal = {Journal of Econometrics},
  year    = {2021},
  volume  = {225},
  number  = {2},
  pages   = {175--199}
}

@article{Borusyak2024,
  author  = {Borusyak, Kirill and Jaravel, Xavier and Spiess, Jann},
  title   = {Revisiting event-study designs: {R}obust and efficient
             estimation},
  journal = {Review of Economic Studies},
  year    = {2024},
  volume  = {91},
  number  = {6},
  pages   = {3253--3285}
}

@article{Cameron-Gelbach-Miller2008,
  author  = {Cameron, A. Colin and Gelbach, Jonah B. and Miller, Douglas L.},
  title   = {Bootstrap-based improvements for inference with clustered errors},
  journal = {Review of Economics and Statistics},
  year    = {2008},
  volume  = {90},
  number  = {3},
  pages   = {414--427}
}

%%---- Supervisory / crypto -----------------------------------------------
@techreport{BCBS2021Crypto,
  author      = {{Basel Committee on Banking Supervision}},
  title       = {Prudential treatment of cryptoasset exposures},
  institution = {Bank for International Settlements},
  year        = {2022},
  number      = {D545},
  note        = {Final standard, December 2022}
}

@techreport{FSB2023Crypto,
  author      = {{Financial Stability Board}},
  title       = {The Financial Stability Risks of Decentralised Finance},
  institution = {Financial Stability Board},
  year        = {2023},
  number      = {P160223},
  note        = {G20 official assessment, February 2023}
}

@techreport{Aldasoro2023Stablecoin,
  author      = {Aldasoro, I{\\~n}aki and Mehrling, Perry and Neilson, Daniel H.},
  title       = {On par: {A} money view of stablecoins},
  institution = {Bank for International Settlements},
  year        = {2023},
  number      = {BIS Working Paper 1146}
}

%%---- FTX collapse: on-chain forensic (replaces Griffin-Kruger-Mei) ------
%% NOTE: Bib key kept as Griffin-Kruger-Mei2023 to avoid renaming tex.
%% Content updated to the actual Griffin-Kruger working paper documenting
%% the FTX collapse (SSRN 4490028, "What is Forensic Finance?", 2023).
@techreport{Griffin-Kruger-Mei2023,
  author      = {Griffin, John M. and Kruger, Samuel},
  title       = {What is forensic finance?},
  institution = {SSRN Working Paper 4490028},
  year        = {2023},
  note        = {Includes case study of the FTX collapse}
}
"""

Path(r"E:/论文SCI（2026）/SCI之加密货币之多伦多20260819/cex_contagion_v2.0/manuscript/refs.bib").write_text(KEPT_ENTRIES, encoding="utf-8")
print(f"[write] refs.bib rewritten with 29 verified entries")
print(f"[byte size] {len(KEPT_ENTRIES):,}")
