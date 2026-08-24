# Spine · Immutable Baseline for v2.0 Regeneration

> **锁定日期**：2026-08-18  
> **来源版本**：v0.9-m (cex_contagion_v0.1/manuscript/main_eca_v01.tex, 34 pages, 6452 words)  
> **锁定原则**：v2.0 全稿其他章节按此三轴基线重跑生成。此三轴**仅允许字符级微调**（例如修一个词以匹配 §4 真实数字），**不允许结构性重写**。

---

## 1. Title（不可变）

**Unlikely Intersections in Crypto Exchange Reserves: An O-Minimal Test for Systemic Risk**

- 无冒号前的"Contagion" 概念（Alan 敲定用 "Reserves"，o-minimality 直接锚定菲奖 Tsimerman citation）
- 副标题保留 "O-Minimal Test" 数学味 + "Systemic Risk" 经济学味

---

## 2. Abstract（128 词，不可变）

> Six major centralised cryptocurrency exchanges collapsed within seven months of each other. The cluster exposed a gap in systemic risk measurement that equity-based indices cannot fill: most crypto venues lack liquid equity. This paper builds a supervisory diagnostic from public reserve compositions. The joint reserve state is embedded in a product of simplices, and simultaneous distress corresponds to an unlikely intersection in the sense of the o-minimality programme in arithmetic geometry. Matching upper and lower bounds meet at a closed-form crossover threshold that separates a common systemic factor from idiosyncratic failure. The spot-Bitcoin ETF approval provides a sharp natural experiment. The full intersection attains its maximum in the approval quarter, whereas a stablecoin placebo shows no comparable jump. The diagnostic is computable in real time and yields a state-contingent capital buffer.

### 关键锚点（贯穿全稿必须一致）
- **无硬年份**（"the spot-Bitcoin ETF approval" 而非 "January 2024"）
- **无数学字母 / p / CI**（那些属于 §4 Results 和 §6 Conclusion）
- **连字符 5 个**：equity-based, closed-form, o-minimality (compound name, 计 1), spot-Bitcoin, state-contingent
- **首句 10 词** 事实陈述 + "The cluster" 回指
- **末句** "yields a state-contingent capital buffer"（Basel III 术语，非 "stress buffer multiplier"）

---

## 3. §1 Introduction 结构（不可变）

### §1 段落骨架

| 段 | 词数 | 内容锚点 |
|---|---|---|
| **§1.a Hook** | ~90 | 悖论钩子：exchanges 是 modern finance 最透明的 counterparties, yet no working measure uses this transparency |
| **§1.b Grounding** | ~180 | 六大破产事件列表 + $16 bn shortfall = 8% on-chain reserves + 中位 27 天间隔 + FTX 非 mechanical trigger |
| **§1.c Landing** | ~100 | 三候选假设（common factor / network amplification / unlikely intersections in state space） |
| Question paragraph | ~90 | Two edges of the same question + intersection frontier |
| Lit block §1 | ~180 | Network contagion (Allen-Gale, Freixas-Parigi-Rochet, etc.) + Systemic-risk (Adrian-Brunnermeier CoVaR, Acharya SES, Brownlees-Engle SRISK) |
| Lit block §2 | ~200 | Crypto microstructure + GKM 差异化 + BCBS/FSB/Aldasoro supervisory |
| Lit block §3 | ~150 | O-minimality programme (Pila-Wilkie, van den Dries, Bakker-Klingler-Tsimerman) + Tsimerman 2026 Fields Medal 直接 citation |
| Contribution First | 45 | Reserve-simplex-product + funding-implied third axis 反转叙事 (2D snapshot → lift to 3D) |
| Contribution Second | 86 | Matching o-minimal bounds → closed-form crossover threshold → testable prediction |
| Contribution Third | 60 | Concentration-as-mechanism finding + 3 policy corollaries |
| Paper structure | ~130 | Section roadmap + SHA-256 replication pointer |

**§1 总词数：约 1289** ← v0.9-m 定稿数字

### §1 硬约束（不可修改）
- 三点贡献段 **不带具体数字**、不带 \citet、不带具体年份、不带机构名
- 三点贡献段 **纯定性**：First 反转叙事、Second closed-form threshold、Third 3 policy corollaries
- 首段悖论 hook 保留（"most transparent counterparties... Yet no working measure uses this transparency"）
- Lit block 三段拆分（Network / Crypto+Supervisory / O-minimality）
- 二段末 "by borrowing from an unlikely place" 悬念钩子 → 三段首 "The o-minimality programme..." 直入
- 末段加 replication pointer："All data and code are public, archived with SHA-256 hashes"

### §1 允许的字符级微调（仅限）
- 修一个词以匹配 §4 真实数字（例如 τ 值变化时同步 §1 language）
- 修拼写从英式到美式（analyse → analyze, centralise → centralize）
- 修 typo

---

## 4. 与 v2.0 其他章节的交叉引用锚

**§1 里出现的实证数字（这些是 v0.1 已实测的一级 REAL）：**
- 六大破产事件日期（2022-06-13 Celsius → 2023-01-19 Genesis）
- $16 billion 客户负债 shortfall（Table 1 里 1.2+1.3+8.7+1.3+3.4 汇总）
- 8% 三家 2025-Q4 on-chain reserves ratio（$16 bn / $209.4 bn）
- 中位 27 天事件间隔
- FTX 前 Voyager/Celsius 已破产（four to five months earlier）
- March 2023 banking shock（Silvergate/Signature 银行崩塌）预期两个月后
- Tsimerman 2026 Fields Medal（arithmetic geometry / o-minimality methodology cited）

**§1 未出现（属于 §4 Results 和 §6 Conclusion）：**
- τ = 0.112 / t = 4.28 / wild bootstrap p < 0.001 / CI [0.025, 0.199]
- Pooling gain 0.709 / 95% CI [0.62, 0.81]
- Rank SVs {0.816, 0.574, 0.530, 0.235, 1.5e-4}
- 39 quarterly snapshots
- 2025-Q3 / 2024-Q1 double-headline 具体季度

这些数字在 §4 和 §6 里首次露面，§1 只暗示"empirical location of the frontier"。

---

## 5. 冻结校验清单（P4 全稿校验时用）

- [ ] Title 全稿唯一（tex 主稿、cover letter、README）
- [ ] Abstract 全稿唯一（128 词、5 连字符、5 步 canonical 结构、无年份/字母/p）
- [ ] §1 段落骨架符合上表（11 段、词数在 ±10% 内）
- [ ] 三点贡献段词数：First 45 / Second 86 / Third 60 (v0.9-m 匀称目标)
- [ ] §1 无 \citet 在贡献段 / 无具体年份 / 无 τ p CI 数字
- [ ] Fields Medal Tsimerman citation 在 §1 lit block §3 位置

---

## 6. 主轴改动日志（v2.0 生成过程中）

如果 P2-P4 期间需要修改 spine，在此追加记录：

| 日期 | 章节 | 改动 | 理由 |
|---|---|---|---|
| （无）| — | — | 冻结基线 |
