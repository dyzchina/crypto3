# Regeneration Plan · v2.0 P2-P4 待做清单

> **Alan 敲定 2026-08-18 路径**：主轴（title/abstract/§1）冻结，其他章节按新指令 + 三级数据原则重跑生成。  
> P0 骨架 + P1 charter 已完成（本轮）；**P2-P4 下轮执行**。

---

## P0 已完成 ✅ · 2026-08-18 本轮

- `docs/spine_frozen.md` · Title + Abstract + §1 结构骨架冻结
- `docs/data_charter.md` · 三级数据原则清单（一级 REAL / 二级 PROXY / 三级 SIMULATED）
- 目录树：`data/{raw_por,processed}` + `manuscript/{figures}` + `scripts/` + `submission_bundle/` + `docs/` + `supplementary/`
- 一级 REAL 数据拷贝：145 MB DefiLlama raw + 8 CSV processed + 11 scripts + 4 real-data figures + refs.bib

---

## P1 已完成 ✅ · 2026-08-18 本轮

- 三级数据 charter 逐条锚定 → 每条 claim 有明确 (level, source, position, script) 四元组
- Fabrication 红线（禁止 fabricate 数字 / 未实现的 promise / 未 script-backed 的 CI）

---

## P2 待做（下轮）· 章节重跑生成 · 工期估 3-4 h

**输入**：spine（title/abstract/§1）+ 三级数据 charter + Alan 前面所有 v0.9-a → v0.9-m 累积的措辞决定

**输出**：`manuscript/main_eca_v2.tex` 完整稿

### P2.1 · §2 Setup（约 900-1000 词）
- ECA canonical opening（3-item roadmap）+ Def 1 + 三 dispersion 泛函 + Prop 1 (Pila-Wilkie 表示)
- 变量名统一：$p_e = (r_e, q_e, \phi_e)$，venue set $\mathcal{P}$
- 不引 Zilber-Pink conjecture 作 hypothesis（heuristic 措辞降级）

### P2.2 · §3 Bounds（约 1000-1100 词）
- ECA canonical opening（3 matching bounds preview）
- Theorem 1 (Prior polylog) + proof sketch → Pila-Wilkie 直接
- Theorem 2 (Wild lower) + proof sketch → o-minimal scale-induction（不引 Ax-Schanuel for j-function）
- Theorem 3 (Sticky) + proof sketch → 2D Pila-Wilkie
- Corollary 4 (Crossover) closed-form
- Theorem 5 (Pooling gain) $n^{-1/(2m)}$
- **Algorithm 1 换 `algorithm` 环境**（`algorithm2e` package）
- **新增 Fig 5 · Algorithm 1 flowchart 可视化**（3-step: dyadic partition → per-cap PW → composition）

### P2.3 · §4 Empirical（约 2000-2100 词）
- ECA canonical opening（3 headline preview）
- §4.1 Data · 三家 on-chain + Coinbase/Kraken proxy 降级到 v3.0
- §4.2 Estimator · 三 half-space distress indicator
- §4.3 Identification · SEC spot-BTC ETF approval (无具体日期) + 10 stablecoin placebo
- §4.4 Results · 5 features + double headline (2024-Q1 hard priors + 2025-Q3 Q75/IQR) + DiD τ=0.112 + wild bootstrap + Table 2 12-cell + pooling gain
- §4.5 图表插入：Fig 1 (5 CEX × 5 asset heatmap, Coinbase/Kraken hatch), Fig 3 (share trajectories), Fig 4 (dual-panel N_k vs prior)

### P2.4 · §5 Policy（约 400-450 词）
- ECA canonical opening
- 三条 corollary 独立段落：real-time audit / state-contingent capital buffer / coordinated-disclosure
- §5 audit line 双 headline 同步（2024-Q1 hard + 2025-Q3 Q75/IQR 都提及）
- 与 BCBS 2021 + FSB 2023 + Aldasoro 2023 显式引用

### P2.5 · §6 Conclusion（约 360 词）
- 三点贡献 recap + scope-and-limitations + extensions + acknowledgements
- **具体数字（τ, t, p, CI, pooling ratio, 2024-Q1 headline）在这里聚齐**（这是 Alan 敲定"具体结果数字应属于总结段"的对应位置）

### P2.6 · App A-E（约 1800 词）
- App A · Proof of Thm 1 (Pila-Wilkie 直接 counting)
- App B · Proof of Thm 2 (o-minimal scale-induction, geometric series 修数学 bug)
- App C · Proof of Thm 3 (Sticky 2D collapse, 加 canonical opening)
- App D · Transversality (加 3-venue rank check 真实 SVs)
- App E · Data (6 小节：Panel construction / Asset-class aggregation / Distress signal / Dating rule / Reproducibility archive / LOO robustness)

---

## P3 待做（下轮）· 图算法环境 + 脚本重跑 · 工期估 1.5 h

### P3.1 · Algorithm 1 换 `algorithm2e` 环境
- 引入 `\usepackage[ruled,vlined]{algorithm2e}` 到 preamble
- 重写 Algorithm 1 为标准伪代码 环境
- 编号变成 "Algorithm 1"（而非 "Figure 1"）
- 删掉原来 tabular float 包装

### P3.2 · 新增 Fig 5 · Algorithm 1 flowchart 可视化
- Python matplotlib 画 3-step flowchart：
  - Step 1: dyadic partition of $\mathcal{X}_H$ at width $R^{-1/2}$
  - Step 2: cell-wise Pila-Wilkie count on $\tau_c$ → $\hat C_c$
  - Step 3: $\ell^p$ composition → $\hat N_k$
- 保存为 `manuscript/figures/fig5_algorithm_flowchart.pdf`
- 主稿在 Algorithm 1 后插入 Fig 5 caption

### P3.3 · 重跑一遍 pipeline 核验
- `scripts/pull_defillama_cex.py` (可跳过 —— 数据已在)
- `scripts/aggregate_por.py` → 重生成 wide CSV
- `scripts/estimator_nk.py` → 重生成 nk_estimates.csv
- `scripts/loo_headline.py` → 重生成 LOO 稳健测试
- `scripts/did_regression.py` → 重生成 did_estimates.csv + robustness_grid.csv + pooling_gain.csv + rank_check.txt
- `scripts/wild_bootstrap.py` → 重生成 wild_bootstrap.csv
- 4 张 fig 脚本重跑：`figure_01_v04.py` + `fig4_v2_dual_threshold.py`
- **建 `scripts/build_all.sh`** · 一键 rebuild data + figures + tex + PDF

### P3.4 · 新脚本 `scripts/verify_data_charter.py`
- 扫描 tex 每处数字 → 对照 CSV 输出 → 报告任何 mismatch
- 扫描 App E 每处 PROXY 承诺 → 对照实际数据存在 → 报告任何 fabricated promise
- **每次 build 前必跑**

---

## P4 待做（下轮）· 全稿贯通校验 · 工期估 30 min

### P4.1 · 一致性校验清单

- [ ] Title 全稿唯一（tex 主稿 + cover letter + README + data_charter + spine_frozen）
- [ ] Abstract 128 词 / 5 连字符 / 无年份 / 无字母数字 一致
- [ ] §1 段落骨架符合 spine_frozen.md
- [ ] 三点贡献段词数 First 45 / Second 86 / Third 60 (v0.9-m 匀称)
- [ ] 三点贡献段无 \citet / 无年份 / 无 τ p CI 数字
- [ ] 数字全稿一致：
  - [ ] τ = 0.112 (5 处: Abstract? 无. Cover Letter, §4.4, Table 2, §6 Conclusion, App E)
  - [ ] Cluster SE = 0.026, t = 4.28（v0.9-c 起用真实 wild bootstrap 数字）
  - [ ] Wild bootstrap p < 0.001, CI [0.025, 0.199]
  - [ ] Pooling gain 0.709 (95% CI [0.62, 0.81]) —— 需要真跑一遍 bootstrap CI 确认
  - [ ] Rank SVs {0.816, 0.574, 0.530, 0.235, 1.5e-4}
- [ ] 术语一致：
  - [ ] "o-minimality programme" (全稿 6+ 处)
  - [ ] "unlikely intersection" (标题 + Prop 1 + §2 opening + App A)
  - [ ] "reserve simplex" / "reserve-simplex product" (定义在 §2)
  - [ ] "funding-implied third axis" (只在 §2.1 定义 + First 贡献段 emph 小标题)
- [ ] 交叉引用无 undefined refs（bibtex 通过）
- [ ] 美式拼写（analyze, harmonize, color, materialize）无残留 -ise/-ised
- [ ] 无内部版本号泄漏（"v0.4" / "v0.5" / "v2.0" 不出现在主稿）
- [ ] Fig 1 Coinbase/Kraken hatch N/A + App E 明确降级到 v3.0
- [ ] 无硬年份在 Abstract / Cover Letter（"January 2024" → "the spot-Bitcoin ETF approval"）

### P4.2 · 编译 + 打投稿包
- `xelatex → bibtex → xelatex → xelatex` 3-pass
- PDF ≤ 35 页
- 无 undef refs / cites
- `python scripts/build_submission_bundle.py`
- 输出 `submission_bundle/SHA256_MANIFEST.txt` 完整

### P4.3 · 更新 README + FACT + JOURNAL
- README v2.0：所有版本变化 / spine 冻结 / P0-P4 阶段成果
- FACT.md：CEX Contagion v2.0 章节更新
- JOURNAL：v2.0 milestone

---

## v2.0 与 v0.1 的关系

- **v0.1** 保留原样作为 reference（不删）
- **v2.0** 从头生成新的 `main_eca_v2.tex`，参考 v0.1 但不 mechanically 复制
- v2.0 用 `main_eca_v2.tex` 而不是 `main_eca_v01.tex` 命名以避免冲突
- 投稿包 `submission_bundle/` 与 v0.1 的 `submission_bundle_ECA_20260817/` 平级独立

---

## 下轮 Alan 只需说 "开工 P2"

我立即执行 P2.1 → P2.6 → P3 → P4，一次性交付 v2.0 完整投稿包（约 5-6 小时集中执行）。
