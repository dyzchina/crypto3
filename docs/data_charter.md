# Data Charter · Three-Tier Data Principle for v2.0

> **Alan 敲定 2026-08-18**：论文所需数据的使用原则  
> ① **一级 REAL** = 已有真实数据 → 做实证  
> ② **二级 PROXY** = 无直接真实数据但有可核查中介代理 → 用代理并明确标注  
> ③ **三级 SIMULATED (grounded)** = 完全无数据也无代理 → 有根据的理论模拟，**必须显式标"simulated / grounded projection"**  
> **红线**：不 fabricate 数据；不使用付费墙内数据；不使用非公开的内部资料

---

## 一级 REAL · 直接可用（v2.0 全部保留）

| Claim | 数据源 | 位置 (稿件) | 位置 (repo) |
|---|---|---|---|
| **DefiLlama 三家 CEX × 13 季度面板** | api.llama.fi/protocol/{slug} (Binance-CEX / okx / Bybit) | §4.1 Data | `data/raw_por/{binance,okx,bybit}/*_quarterly.json` |
| **Binance 2025-12-31 on-chain reserves** = \$168.9 B | 同上 | §4.1 | `data/processed/cex_por_snapshots_wide.csv` |
| **OKX 2025-12-31 on-chain reserves** = \$22.1 B | 同上 | §4.1 | 同上 |
| **Bybit 2025-12-31 on-chain reserves** = \$18.4 B | 同上 | §4.1 | 同上 |
| **三家合计** = \$209.4 B 三家 total = \$16bn/\$209bn ≈ 8% | 计算 | §1.b, §4.1 | 计算式 |
| **五大破产储备缺口** (bn USD)：Celsius 1.2, Voyager 1.3, FTX 8.7, BlockFi 1.3, Genesis 3.4 | Chapter 11 first-day motions / SoFA / 341 meeting reports | Table 1 | (公开司法文件，未存 raw JSON) |
| **五起破产日期** (2022-06-13 → 2023-01-19) | Chapter 11 filings (SDNY/D. Del./D.NJ) | §1.b 首段 + Table 1 | 同上 |
| **DiD τ = 0.112** | TWFE 回归 (39 CEX + 130 stablecoin obs) | §4.4 Results | `data/processed/did_estimates.csv`, `robustness_grid.csv` |
| **DiD 稳健 SE = 0.026, t = 4.28** | Cluster-robust on 13 clusters | 同上 | `data/processed/wild_bootstrap.csv` |
| **Wild-cluster bootstrap p < 0.001, 95% CI [0.025, 0.199]** | CGM 2008 Rademacher, B=9999 seed=4626 | 同上 | `data/processed/wild_bootstrap.csv` |
| **12-cell robustness grid**（全 12 cells 正号）| `did_regression.py` outputs | Table 2 | `data/processed/robustness_grid.csv` |
| **Pooling gain observed = 0.709** | Panel σ_pooled / σ_avg-single | §4.4 pooling paragraph | `data/processed/pooling_gain.csv` |
| **Pooling gain 95% CI [0.62, 0.81]** | Non-parametric bootstrap of 39 obs | 同上 | `did_regression.py` (bootstrap generated inline) |
| **Rank check** (3-venue × 5-asset centred matrix) SVs = {0.816, 0.574, 0.530, 0.235, 1.5e-4}, rank = 4 = m-1 | SVD | App D | `data/processed/rank_check.txt` |
| **$\hat N_k(t)$ 双阈值实证 2022-Q4 → 2025-Q4** | Panel-wise Q75/IQR + Domain hard-prior | §4.4 + Fig 4 | `data/processed/nk_estimates.csv` + `loo_headline.py` LOO 输出 |
| **2024-Q1 hard-prior $\hat N_3 = 1$** | Domain thresholds (native>0.15 OR safe<0.60 OR tail>0.25) | §4.4, Fig 4b | `loo_headline.py` |
| **2025-Q3 Q75/IQR $\hat N_3 = 1$** | Panel-wise 3 half-spaces union | §4.4, Fig 4a | `estimator_nk.py` |
| **10 家 stablecoin placebo 面板** | DefiLlama 35 稳定币档案里选前 10 | §4.3 identification | `../datawang（dld)/raw/defillama/stable_*.json` (v0.1 已下载 168MB) |

---

## 二级 PROXY · 允许使用但必须标注

| 理论对象 | 代理数据 | 代理理由 | 标注位置 |
|---|---|---|---|
| **Funding-implied third axis $\phi_e$** | Long-tail-alt share on DefiLlama panel | Perpetual futures funding rate 与 alt volume 在理论上正相关（inventory / market-maker skew channel）；App E.2 明确写出代理关系 | App E.2 + §4.4 Fig 3 caption |
| **Coinbase reserve composition** | SEC 10-Q Note 5 Customer Custodial Funds by asset class (季频) | Coinbase custody 大多链下无 DefiLlama 索引；SEC 10-Q 是公开可核 quarterly disclosure | Fig 1 Coinbase 行 hatch N/A + App E.1 说明 v3.0 补齐 |
| **Kraken reserve composition** | Nexia SAB&T 半年度审计 PDF | 同上 (custody 链下) | Fig 1 Kraken 行 hatch N/A + App E.1 |
| **五破产事件储备缺口精确日期版本** | Chapter 11 filing date 而非 asset seizure date | Filing date 是唯一公开可核的时间锚点 | Table 1 caption 说明 |
| **Distress indicator threshold Q75 / IQR** | Panel-wise 分位数（in-sample fit）| 明确用 LOO 稳健测试作 falsification check | App E.3 + App E.6 LOO |
| **Persistence exponent $\beta \in [0.3, 0.5]$** | 无经验估计，用理论合理范围 | Long-memory finance literature 惯用区间 | §4 Results text 明确写"under the smoothness class $\beta \in [0.3, 0.5]$" |

---

## 三级 SIMULATED (grounded) · 完全无数据 · 必须标注

| 理论 claim | 模拟依据 | 标注位置 |
|---|---|---|
| **§5 policy $\log 3 \approx 40\%$ $H^\varepsilon$ loss reduction** | 直接从 Theorem 1 常数展开推算（月度 vs 季度 attestation, T×3 → $\log 3$ factor）| §5 policy 段公式 |
| **Regime-dependent capital multiplier formula** $\max\{1, \hat N_k / c_{k,\varepsilon}(\log T)^{\alpha}\}$ | 理论公式，未实证校准 $c$ | §5, App C 说明这是 illustrative formula |
| **Coordinated-disclosure "monthly attestation" recipe** | 无经验数据，理论上 log-factor argument | §5 policy 段 |

---

## 与 v0.1 的差异

**v0.1** 的问题：
- 部分数字（如 pooling gain "0.62-0.81" bootstrap CI）在 tex 里出现，但 wild_bootstrap.py 只跑了 DiD 的 CI，pooling gain 的 bootstrap CI **未跑真数据**（属 fabricated bootstrap output）
- App E 里描述"Coinbase SEC 10-Q Note 5"作为二级 PROXY，但 v0.1 **未真实拉过 Coinbase 10-Q**（属未做的 promise）
- §1 曾用 "$\hat\tau=0.112, t=3.26, p=0.001, CI[0.043, 0.181]$" 均为 fabricated 数字，v0.7 起用真 wild_bootstrap 替换

**v2.0** 的处理：
1. 一级 REAL：验证每个数字都能从脚本重跑对齐 → **v2.0 P3 阶段跑一遍全脚本核实**
2. 二级 PROXY：将 v0.1 未做的 SEC 10-Q / Kraken PDF 明确降级到 v3.0 待办；v2.0 里 Fig 1 用 hatch N/A + App E 明确"v3.0 will fill 5-venue"
3. 三级 SIMULATED：不引入新的 simulated 数据；只用理论公式（不涉及数值 fit）

---

## 三级 Fabrication 红线（v2.0 严禁）

- 任何未由脚本重跑输出的经验数字（例如"Pooling gain CI [0.62, 0.81]"如果 wild_bootstrap.py 没 output → 必须要么补脚本要么删稿件里数字）
- 任何未在 refs.bib 里存在的引用
- 任何 App E 里承诺但未实现的数据 join（Coinbase 10-Q / Kraken Nexia）**必须明确降级到 v3.0 待办**
- 任何 §5 里的政策数字 "40% 减少"如果不能从理论直接推算 → 必须删或改成"substantially"

---

## v2.0 P3 阶段的验证脚本清单

`scripts/verify_data_charter.py`（v2.0 P3 阶段建）：
- 检查主稿里每一处数字都对应 CSV / TXT 输出
- 检查所有 PROXY 都有 App E 标注
- 检查所有 SIMULATED 都有 §5/§App 说明

**每次 build 前跑一次**。
