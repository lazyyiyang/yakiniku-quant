# 推荐书单与学习路径

> 面向A股量化和投研的精选书单，去除数学理论、编程和面试内容

## 核心书单

### 交易策略

| 书名 | 作者 | 侧重点 | 优先级 |
|------|------|--------|--------|
| **Quantitative Trading** | Ernie Chan | 策略开发入门，回测框架 | ★★★ |
| **Algorithmic Trading** | Ernie Chan | 均值回归、动量、配对交易 | ★★★ |
| **The Elements of Quantitative Investing** | Paleologo (Gappy) 2025 | 因子投资最新方法论 | ★★★ |
| **Advanced Portfolio Management** | Paleologo (Gappy) 2025 | 基本面量化基金经理指南 | ★★ |

### 技术分析

| 书名 | 作者 | 侧重点 | 优先级 |
|------|------|--------|--------|
| **Japanese Candlestick Charting Techniques** | Steve Nison | K线分析圣经 | ★★★ |
| **Technical Analysis of the Financial Markets** | John Murphy | 技术分析圣经 | ★★★ |
| **Encyclopedia of Chart Patterns** | Thomas Bulkowski | 图表形态统计大全 | ★★ |

### 衍生品与对冲

| 书名 | 作者 | 侧重点 | 优先级 |
|------|------|--------|--------|
| **Options, Futures, and Other Derivatives** | John Hull | 衍生品入门圣经 | ★★★ |
| **Option Volatility and Pricing** | Natenberg | 波动率实务圣经 | ★★★ |
| **Dynamic Hedging** | Taleb | 期权对冲实务 | ★★ |

### 市场微观结构

| 书名 | 作者 | 侧重点 | 优先级 |
|------|------|--------|--------|
| **Algorithmic Trading and DMA** | Johnson | 直接市场接入经典 | ★★★ |
| **Handbook of Price Impact Modeling** | Webster 2023 | 价格冲击最新 | ★★ |

### 投资基础

| 书名 | 作者 | 侧重点 | 优先级 |
|------|------|--------|--------|
| **Security Analysis** | Graham & Dodd | 价值投资圣经 | ★★ |
| **Investment Valuation** | Damodaran | 估值方法论大全 | ★★ |

### 统计套利与组合

| 书名 | 作者 | 侧重点 | 优先级 |
|------|------|--------|--------|
| **Quantitative Portfolio Management** | Isichenko | 统计套利理论与实践 | ★★ |
| **Active Portfolio Management** | Grinold & Kahn | 主动管理，IR框架 | ★★ |
| **Advances in Financial Machine Learning** | López de Prado | 金融ML方法论（有争议） | ★ |

### 软阅读

| 书名 | 作者 | 内容 | 推荐理由 |
|------|------|------|----------|
| **The Man Who Solved the Market** | Zuckerman | Jim Simons与量化革命 | 了解Renaissance |
| **The Quants** | Scott Patterson | 量化交易者群像 | 2008危机前后 |
| **My Life as a Quant** | Emanuel Derman | 物理学家转型量化 | 理解量化思维 |


## A股学习路线图

```
Stage 1 - 策略入门（1-2个月）
├── Ernie Chan: Quantitative Trading
├── Murphy: Technical Analysis（技术分析基础）
├── Nison: Candlestick Charting（K线基础）
└── 熟悉A股规则和数据

Stage 2 - 策略深化（2-3个月）
├── Ernie Chan: Algorithmic Trading
├── Hull: Options（衍生品基础）
├── Gappy: Elements of Quantitative Investing
└── 开始策略开发和回测

Stage 3 - 对冲与衍生品（1-2个月）
├── Natenberg: Option Volatility
├── Taleb: Dynamic Hedging
├── Johnson: Algorithmic Trading and DMA
└── ETF期权实践

Stage 4 - 组合与风控（持续）
├── Grinold & Kahn: Active Portfolio Management
├── Isichenko: Quantitative Portfolio Management
└── 实盘验证和策略迭代
```


## 免费资源

| 资源 | 链接 | 说明 |
|------|------|------|
| **Quantopian Lectures归档** | [GitHub Gist](https://gist.github.com/ih2502mk/50d8f7feb614c8676383431b056f4291) | 最完整的量化课程（免费） |
| **Convex Optimization** | [免费在线](https://www.web.stanford.edu/~boyd/cvxbook/) | Boyd & Vandenberghe |
| **Foundations of RL for Finance** | [免费PDF](https://stanford.edu/~ashlearn/RLForFinanceBook/book.pdf) | Rao & Jelvis |
| **AkShare** | [akshare.xyz](https://akshare.xyz) | A股免费数据接口 |

## A股数据工具

| 工具 | 类型 | 免费 | 说明 |
|------|------|------|------|
| AkShare | Python库 | 是 | A股数据最全面的开源库 |
| Tushare | Python库 | 需积分 | 数据较全，需注册 |
| JoinQuant | 平台 | 部分 | 回测+研究一体化 |
| RiceQuant | 平台 | 部分 | 回测+研究一体化 |
| vnpy | 框架 | 是 | 开源交易框架 |
| qlib | 框架 | 是 | 微软开源量化研究框架 |