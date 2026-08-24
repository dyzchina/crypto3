# Bankruptcy first-day declarations — Table 1 source references

Table 1 of `manuscript/main_eca_v2.pdf` reports reserve gaps (customer
liabilities minus recoverable assets) at the chapter 11 filing dates of
five centralised-crypto entities in 2022–2023. Numbers come from each
estate's first-day declaration filed with the bankruptcy court.

These PDF filings are public docket documents (11 U.S.C. § 107 makes
bankruptcy filings presumptively public). Kroll and Stretto host the
official case dockets. Direct retrieval requires accepting the docket
site's terms of use.

| Case | Docket # | Court | Filed | Gap (USD bn) | Docket URL |
|---|---|---|---|---:|---|
| Celsius Network LLC | 22-10964 | Southern District of New York | 2022-07-13 | 1.2 | [https://cases.stretto.com/celsius](https://cases.stretto.com/celsius) |
| Voyager Digital Holdings, Inc. | 22-10943 | Southern District of New York | 2022-07-05 | 1.3 | [https://cases.stretto.com/voyager](https://cases.stretto.com/voyager) |
| FTX Trading Ltd. (with Alameda Research LLC) | 22-11068 | District of Delaware | 2022-11-11 | 8.7 | [https://restructuring.ra.kroll.com/FTX](https://restructuring.ra.kroll.com/FTX) |
| BlockFi Inc. | 22-19361 | District of New Jersey | 2022-11-28 | 1.3 | [https://restructuring.ra.kroll.com/BlockFi](https://restructuring.ra.kroll.com/BlockFi) |
| Genesis Global Capital, LLC | 23-10063 | Southern District of New York | 2023-01-19 | 3.4 | [https://restructuring.ra.kroll.com/genesis](https://restructuring.ra.kroll.com/genesis) |

## Detailed reserve-gap references

### Celsius Network LLC (case 22-10964)

- **Filed**: 2022-07-13  
- **Court**: United States Bankruptcy Court, Southern District of New York  
- **Declaration**: Declaration of Alex Mashinsky, Chief Executive Officer, in Support of Chapter 11 Petitions and First Day Motions  
- **Reserve gap**: USD 1.2 bn — First-day declaration, ¶ 47-56 (assets vs customer liabilities)  
- **Docket URL**: https://cases.stretto.com/celsius  

### Voyager Digital Holdings, Inc. (case 22-10943)

- **Filed**: 2022-07-05  
- **Court**: United States Bankruptcy Court, Southern District of New York  
- **Declaration**: Declaration of Stephen Ehrlich, Chief Executive Officer, in Support of Chapter 11 Petitions and First Day Motions  
- **Reserve gap**: USD 1.3 bn — First-day declaration Schedule A (crypto assets vs customer accounts)  
- **Docket URL**: https://cases.stretto.com/voyager  

### FTX Trading Ltd. (with Alameda Research LLC) (case 22-11068)

- **Filed**: 2022-11-11  
- **Court**: United States Bankruptcy Court, District of Delaware  
- **Declaration**: Declaration of John J. Ray III in Support of Chapter 11 Petitions and First Day Motions  
- **Reserve gap**: USD 8.7 bn — Ray declaration (Nov 17, 2022), Section III.A (customer-fund misappropriation summary)  
- **Docket URL**: https://restructuring.ra.kroll.com/FTX  

### BlockFi Inc. (case 22-19361)

- **Filed**: 2022-11-28  
- **Court**: United States Bankruptcy Court, District of New Jersey  
- **Declaration**: Declaration of Mark A. Renzi, Financial Advisor to the Debtors, in Support of the Debtors' Chapter 11 Petitions and First Day Motions  
- **Reserve gap**: USD 1.3 bn — Renzi first-day declaration, Schedule of Assets and Liabilities summary  
- **Docket URL**: https://restructuring.ra.kroll.com/BlockFi  

### Genesis Global Capital, LLC (case 23-10063)

- **Filed**: 2023-01-19  
- **Court**: United States Bankruptcy Court, Southern District of New York  
- **Declaration**: Declaration of A. Derar Islim, Interim Chief Executive Officer, in Support of the Debtors' Chapter 11 Petitions and First Day Motions  
- **Reserve gap**: USD 3.4 bn — Islim first-day declaration ¶ 20 (intercompany loan portfolio impairment)  
- **Docket URL**: https://restructuring.ra.kroll.com/genesis  

## Reproducibility note

For strict replication, download each first-day declaration PDF from the
docket URLs above and place them in this directory using the filename
convention `{case_no}_first_day.pdf`. Then re-run
`python scripts/build_manifest.py` to add SHA-256 hashes to `MANIFEST.sha256`.
