# A股量化投研知识库

> 面向A股市场的投资研究与量化策略知识体系 | 更新于 2026-06-12

## 知识库结构

```
source/
├── INDEX.md                              ← 你正在阅读的总览
├── 00-inbox/                             ← 📥 放入新材料的文件夹
│   └── README.md                           使用说明
├── 01-classic-strategies/                 ← 经典交易策略
│   ├── momentum-trend.md                  动量与趋势跟踪策略
│   ├── mean-reversion.md                  均值回归与反转策略
│   ├── pairs-stat-arb.md                  配对交易与统计套利
│   └── factor-investing.md                因子投资与多因子模型
├── 02-technical-analysis/                ← K线与技术分析
│   ├── candlestick-basics.md              K线基础与蜡烛图形态
│   ├── technical-indicators.md            技术指标大全
│   └── chart-patterns.md                  图表形态分析
├── 03-investment-fundamentals/            ← 投资基础知识
│   ├── market-structure-ashare.md         A股市场结构与交易规则
│   ├── portfolio-risk-mgmt.md             组合构建与风险管理
│   └── fundamental-concepts.md            基本面与估值基础
├── 04-hedging-derivatives/               ← 对冲与衍生品
│   ├── options-basics.md                  期权入门与定价
│   ├── hedging-strategies.md              对冲策略（股指期货/ETF期权）
│   └── volatility-trading.md             波动率与偏斜交易
├── 05-execution-costs/                   ← 交易执行与成本
│   ├── microstructure-ashare.md           A股微观结构与委托机制
│   └── transaction-cost-model.md          交易成本建模
└── 06-reading-list/                      ← 推荐书单
    └── recommended-books.md              书单与学习路径
```

## 学习路径

```
Stage 1 - 基础建立（2-4周）
├── 03-investment-fundamentals/market-structure-ashare.md  → A股规则
├── 02-technical-analysis/candlestick-basics.md            → K线基础
├── 02-technical-analysis/technical-indicators.md          → 技术指标
└── 03-investment-fundamentals/fundamental-concepts.md      → 基本面

Stage 2 - 策略学习（4-8周）
├── 01-classic-strategies/momentum-trend.md     → 动量策略
├── 01-classic-strategies/mean-reversion.md     → 均值回归
├── 01-classic-strategies/factor-investing.md   → 因子投资
└── 01-classic-strategies/pairs-stat-arb.md     → 配对交易

Stage 3 - 对冲与执行（2-4周）
├── 04-hedging-derivatives/options-basics.md         → 期权基础
├── 04-hedging-derivatives/hedging-strategies.md     → 对冲策略
├── 05-execution-costs/microstructure-ashare.md     → 微观结构
└── 05-execution-costs/transaction-cost-model.md     → 成本建模

Stage 4 - 深化（持续）
├── 04-hedging-derivatives/volatility-trading.md    → 波动率交易
├── 03-investment-fundamentals/portfolio-risk-mgmt.md → 组合风控
└── 06-reading-list/recommended-books.md              → 拓展阅读
```

## 核心要点速览

| 领域 | 入门文件 | 关键书 |
|------|---------|--------|
| 动量策略 | momentum-trend.md | Ernie Chan |
| 均值回归 | mean-reversion.md | Ernie Chan |
| 因子投资 | factor-investing.md | Gappy 2025 |
| K线分析 | candlestick-basics.md | Steve Nison |
| 技术指标 | technical-indicators.md | John Murphy |
| A股规则 | market-structure-ashare.md | 交易所规则文档 |
| 期权对冲 | hedging-strategies.md | Natenberg |
| 波动率 | volatility-trading.md | Natenberg/Bergomi |
| 交易成本 | transaction-cost-model.md | Johnson/Almgren |
| 组合风控 | portfolio-risk-mgmt.md | Grinold & Kahn |

## 📥 新材料

发现好的材料？放入 `00-inbox/` 文件夹，后续整理归类。

参见 `00-inbox/README.md` 了解归档方法。