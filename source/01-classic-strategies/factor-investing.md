# 因子投资与多因子模型

> 分解收益来源：你的Alpha是真的Alpha，还是只是Beta？

## 核心思想

因子投资的核心假设：**资产收益可以被少数几个共同因子解释**。

- 你的策略收益 = 市场因子 + 规模因子 + 价值因子 + ... + 真正的Alpha
- 如果"Alpha"可以被已知因子解释，那不是Alpha，只是隐含的因子暴露
- 因子投资的本质是系统性、规则化地获取因子溢价

## 主要因子

### 经典五大因子（Fama-French 五因子模型）

| 因子 | 英文名 | 含义 | 长期溢价 |
|------|--------|------|---------|
| 市场 | Market (RMRF) | 市场风险暴露 | ~8%年化 |
| 规模 | SMB (Small Minus Big) | 小市值溢价 | 不稳定 |
| 价值 | HML (High Minus Low) | 低估值溢价 | 近年衰减 |
| 盈利 | RMW (Robust Minus Weak) | 高盈利溢价 | 较稳定 |
| 投资 | CMA (Conservative Minus Aggressive) | 低投资溢价 | 较稳定 |

### A股特色因子

| 因子 | 说明 | A股表现 |
|------|------|---------|
| 反转 | 短期（1个月）反转效应 | A股极强 |
| 换手率 | 低换手率溢价 | A股显著 |
| 波动率 | 低波动率溢价 | A股存在，但有波动率陷阱 |
| 动量 | 3-12个月动量 | A股弱于美股，需结合反转 |
| 北向资金 | 沪深港通净流入 | 事件驱动型因子 |
| 融资融券 | 融资余额变化 | A股特有情绪指标 |

## 因子研究流程

### 1. 因子构建

```python
def build_factor(data, factor_name, params):
    """
    因子构建的标准流程
    """
    if factor_name == 'value':
        # BP = 每股净资产 / 每股股价
        factor = data['book_value_per_share'] / data['close']
    elif factor_name == 'momentum':
        # 过去N个月收益（剔除最近1个月，避免短期反转）
        factor = data['close'] / data['close'].shift(params['lookback']) - 1
    elif factor_name == 'volatility':
        # 过去N日波动率
        factor = data['close'].pct_change().rolling(params['lookback']).std() * np.sqrt(252)
    elif factor_name == 'turnover':
        # 换手率
        factor = data['volume'] / data['float_shares']

    return factor
```

### 2. 因子检验 — 信息系数（IC）

```python
from scipy import stats

def calculate_ic(factor, forward_returns):
    """
    计算因子IC（信息系数）
    
    IC > 0.03：有效因子
    IC > 0.05：强因子
    IC > 0.10：极强因子（很可能有问题）
    """
    # Rank IC（Spearman相关）比Pearson IC更稳健
    ic, p_value = stats.spearmanr(factor, forward_returns)

    # IC的统计显著性
    ic_series = factor.groupby(factor.index.to_period('M')).apply(
        lambda x: stats.spearmanr(x, forward_returns.loc[x.index])[0]
    )

    ir = ic_series.mean() / ic_series.std()  # 信息比率

    return {
        'ic': ic,
        'p_value': p_value,
        'ir': ir,
        't_stat': ic_series.mean() / (ic_series.std() / np.sqrt(len(ic_series))),
        'pct_positive': (ic_series > 0).mean()
    }
```

**因子有效性标准**：
- |IC均值| > 0.03
- IC-t统计量 > 2（或IC-IR > 0.5）
- 月度IC > 0 的比例 > 60%

### 3. 因子组合构建

```
方法一：等权重
  - 所有因子Z-score等权平均
  - 简单、稳健

方法二：IC加权
  - 按历史IC加权
  - 历史表现好的因子权重更大
  - 风险：IC可能非平稳

方法三：最优化
  - 最大化预期收益 / 风险
  - 容易过拟合
```


## 因子投资在A股的挑战

### 挑战1：因子拥挤

```
大量资金追逐相同因子 → 因子拥挤 → 溢价衰减
A股典型情况：
- 小市值因子在2017年前极强，之后衰减
- 价值因子近几年持续跑输成长
- 低波动因子随ETF规模增长而衰减

对策：监控因子拥挤度指标（因子相关性、换手率、持股市值）
```

### 挑战2：风格轮动

```
A股风格轮动极为剧烈：
- 2013-2015：小盘成长占优
- 2017-2018：大盘价值占优
- 2019-2020：核心资产
- 2021-2023：小盘价值回归
- 风格切换可导致因子收益在±30%波动

对策：因子择时（虽难）或真正的多因子分散化
```

### 挑战3：壳价值与退市

```
A股退市制度日趋严格：
- 2020年退市新规后，退市公司增加
- 壳价值大幅缩水 → 小市值因子逻辑变化
- 必须加入退市风险过滤

对策：剔除ST、*ST、退市风险股
```

### 挑战4：交易成本

```
A股交易成本构成：
- 佣金：万2.5左右（双向）
- 印花税：千1（卖出）
- 滑点：视流动性

因子换手率对成本极为敏感：
- 月度换仓 → 成本可控
- 周度换仓 → 需要更强的因子IC
- 日度换仓 → 交易成本可能吞噬全部因子溢价
```


## 多因子Alpha策略框架

```
1. 因子挖掘
   → 基本面因子、技术因子、另类数据因子
   → IC检验、因子衰减分析

2. 因子清洗
   → 去极值（MAD法）
   → 标准化（Z-score）
   → 中性化（行业+市值中性化）

3. 因子组合
   → 等权/ IC加权 / 最优化
   → 因子挖矿的Bonferroni校正

4. 组合构建
   → 因子得分 → 排序 → 分组
   → 多头组 vs 空头组（或纯多头）
   → 优化权重（风险平价/最小方差）

5. 风险控制
   → 行业暴露限制
   → 个股权重上限
   → 换手率约束
```


## 参考阅读

- Fama & French (2015), "A Five-Factor Asset Pricing Model"
- Paleologo (Gappy), *The Elements of Quantitative Investing* (2025)
- Grinold & Kahn, *Active Portfolio Management* — IR框架
- Barra风险模型文档 — A股因子模型实务