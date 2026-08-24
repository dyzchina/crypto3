# CEX Contagion × O-Minimality · v2.0 Regeneration Bundle

**建库**：2026-08-18  
**上级路径**：`E:\论文SCI（2026）\SCI之加密货币之多伦多\`  
**参考版本**：`cex_contagion_v0.1/` (v0.9-m, 34 pages, 6452 words)  
**当前阶段**：P0 骨架 + P1 数据 charter 完成 · P2-P4 待执行

---

## 项目定位（不变）

- **Title (Alan 敲定, v0.9-c 起)**：*Unlikely Intersections in Crypto Exchange Reserves: An O-Minimal Test for Systemic Risk*
- **目标**：Econometrica initial submission (single-blind)
- **备胎瀑布**：ECA → JF → RFS → JFE
- **作者**：Hongjun Gou (ICBC Beijing 100140) 单作者
- **核心 slogan**：*"Pila-Wilkie counting theorem transferred to reserve-simplex geometry — the first empirical instrument for joint CEX distress"*

## v2.0 相对 v0.1 的核心变化

| 维度 | v0.1 (v0.9-m) | **v2.0** |
|---|---|---|
| **生成方式** | 增量式（v0.1 → v0.2 → ... → v0.9-m）| **主轴冻结 + 其他章节按新指令重跑** |
| **数据原则** | 隐式（有 fabricated 数字 → 后期修 v0.7）| **显式 3-level charter** (REAL/PROXY/SIMULATED) |
| **Algorithm 1** | figure float 包 tabular（Alan 反映"未见图"）| **`algorithm2e` 环境 + Fig 5 flowchart 可视化** |
| **Fig 数** | 4 | **5**（新增 Algorithm 1 flowchart）|
| **主轴自由度** | 段落级修改 | **仅字符级微调** |
| **一致性校验** | 手动 | **`verify_data_charter.py` 自动扫描** |

## 目录结构

```
cex_contagion_v2.0/
├── docs/                              # 冻结基线 + 生成计划
│   ├── spine_frozen.md                # 主轴（title + abstract + §1）冻结基线 ✅
│   ├── data_charter.md                # 三级数据原则 ✅
│   ├── regeneration_plan.md           # P2-P4 待做清单 ✅
│   └── section1_intro_frozen.tex      # §1 Introduction 冻结 tex 副本
├── manuscript/                        # v2.0 主稿
│   ├── main_eca_v2_spine.tex          # 主轴 tex 基线 (preamble + title + abstract + §1) ✅
│   ├── main_eca_v2.tex                # (P2 生成) 完整 v2.0 主稿
│   ├── refs.bib                       # 从 v0.1 拷贝 ✅
│   ├── cover_letter.txt               # (P2 生成)
│   └── figures/                       # 5 张 fig
│       ├── fig1_reserve_heatmap.pdf   # 一级 REAL, 从 v0.1 拷贝 ✅
│       ├── fig2_event_timeline.pdf    # 从 v0.1 拷贝 ✅
│       ├── fig3_share_trajectories.pdf # 一级 REAL ✅
│       ├── fig4_empirical_frontier.pdf # 一级 REAL (dual-panel) ✅
│       └── fig5_algorithm_flowchart.pdf # (P3 生成) NEW
├── data/
│   ├── raw_por/
│   │   ├── binance/   # 55.4 MB DefiLlama raw ✅
│   │   ├── okx/       # 43.5 MB ✅
│   │   ├── bybit/     # 46.4 MB ✅
│   │   ├── coinbase/  # (v3.0 SEC 10-Q) — PROXY level, empty in v2.0
│   │   └── kraken/    # (v3.0 Nexia PDF) — PROXY level, empty in v2.0
│   └── processed/     # 8 CSV/TXT 全部真实脚本输出 ✅
│       ├── cex_por_snapshots.csv
│       ├── cex_por_snapshots_wide.csv
│       ├── nk_estimates.csv
│       ├── did_estimates.csv
│       ├── robustness_grid.csv
│       ├── pooling_gain.csv
│       ├── rank_check.txt
│       └── wild_bootstrap.csv
├── scripts/                           # 11 Python + 1 Bash ✅
│   ├── _common.py                     # Clash proxy fallback + retry + QUARTERS
│   ├── pull_defillama_cex.py          # 3-CEX 数据抓取
│   ├── aggregate_por.py               # 5-class 聚合 + 归一化
│   ├── estimator_nk.py                # Algorithm 1 empirical implementation
│   ├── loo_headline.py                # LOO robustness test
│   ├── did_regression.py              # 4 estimator × 3 outcome grid
│   ├── wild_bootstrap.py              # CGM 2008 Rademacher B=9999
│   ├── fig4_v2_dual_threshold.py      # Fig 4 dual-panel 双阈值
│   ├── figure_01_v04.py               # Fig 1 + Fig 3 生成器
│   ├── wordcount.py
│   ├── build.sh                       # xelatex 3-pass + bibtex
│   ├── build_all.sh                   # (P3 建) 一键 rebuild data + figures + tex + PDF
│   ├── build_fig5_algorithm.py        # (P3 建) Algorithm flowchart 可视化
│   └── verify_data_charter.py         # (P3 建) 数字/PROXY/SIMULATED 一致性扫描
├── supplementary/                     # (P4 建) 补充材料
└── submission_bundle/                 # (P4 建) 最终投稿包 + SHA-256 manifest
```

## 三级数据原则速览（`docs/data_charter.md` 详）

| Level | 例 | 位置 |
|---|---|---|
| ① REAL | DefiLlama 三家 × 13 季度 / DiD τ=0.112 / Wild bootstrap CI / Rank SVs / 五破产 gap | 100% script-backed |
| ② PROXY | funding φ = long-tail alt / Coinbase 10-Q / Kraken Nexia PDF | App E.2 标注 |
| ③ SIMULATED | §5 policy log-3 factor / capital multiplier formula | §5/App C 显式说明 |

**红线**：不 fabricate 数字 / 不用付费墙内数据 / 不用未公开内部资料。

## 下一步执行

**下轮**（Alan 说 "开工 P2"）：
- P2 · 章节重跑（§2-§6 + App A-E）— 约 3-4 h
- P3 · Algorithm 1 环境 + Fig 5 flowchart + verify_data_charter.py — 约 1.5 h
- P4 · 全稿一致性校验 + 投稿包重打 — 约 30 min

**总工期约 5-6 h**（下轮一次性完成 v2.0 定稿）。

---

## 版本 log

| 版本 | 日期 | 阶段 |
|---|---|---|
| v0.1 → v0.9-m | 2026-08-17 | 增量迭代（保留在 `../cex_contagion_v0.1/`）|
| **v2.0-P0** | **2026-08-18** | **骨架 + spine 冻结 + 数据 charter 完成** ← 本轮 |
| v2.0-P1 | 2026-08-18 | 数据 charter 完成 ← 本轮 |
| v2.0-P2 | 下轮 | 章节重跑 §2-§6 + App A-E |
| v2.0-P3 | 下轮 | Algorithm 环境 + Fig 5 + 验证脚本 |
| v2.0-P4 | 下轮 | 全稿一致性 + 投稿包 |
