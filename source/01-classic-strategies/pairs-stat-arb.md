# 配对交易与统计套利

> 找到两个资产的长期均衡关系，在偏离时交易

## 核心原理

统计套利（Statistical Arbitrage）的核心：**通过统计方法发现价格关系，在关系偏离时建仓，回归时平仓**。

配对交易是最简单的统计套利形式：
- 找到两只走势高度相关的股票（如同行业龙头）
- 计算价差的统计特征
- 价差偏离时执行配对交易

## 配对交易流程

### 第一步：寻找配对

**基本面筛选**（最可靠）：
- 同行业、同板块股票（如工商银行 vs 建设银行）
- 产业链上下游（如整车 vs 零部件）
- 同一公司的A/H股

**统计筛选**：
```python
from statsmodels.tsa.stattools import coint

def find_cointegrated_pairs(prices, significance=0.05):
    """遍历所有股票对，寻找协整关系"""
    n = len(prices.columns)
    pairs = []

    for i in range(n):
        for j in range(i+1, n):
            score, p_value, _ = coint(
                prices.iloc[:, i], prices.iloc[:, j]
            )
            if p_value < significance:
                pairs.append({
                    'asset_i': prices.columns[i],
                    'asset_j': prices.columns[j],
                    'p_value': p_value,
                    'score': score
                })

    return sorted(pairs, key=lambda x: x['p_value'])
```

### 第二步：计算对冲比率

```python
import statsmodels.api as sm

def calculate_hedge_ratio(y, x):
    """OLS回归计算对冲比率"""
    X = sm.add_constant(x)
    model = sm.OLS(y, X).fit()
    hedge_ratio = model.params[1]
    return hedge_ratio

# spread = price_A - hedge_ratio × price_B
```

### 第三步：计算价差与信号

```python
def generate_pairs_signals(spread, entry_z=2.0, exit_z=0.5, stop_z=4.0):
    """
    基于Z-score生成交易信号
    
    entry_z: 入场阈值（标准差倍数）
    exit_z:  出场阈值
    stop_z:  止损阈值
    """
    # 滚动标准化
    lookback = max(20, int(half_life * 2))
    z_score = (spread - spread.rolling(lookback).mean()) / spread.rolling(lookback).std()

    signals = []
    position = 0

    for z in z_score:
        if position == 0:
            if z < -entry_z:
                position = 1   # 做多价差（买A卖B）
            elif z > entry_z:
                position = -1  # 做空价差（卖A买B）
        elif position == 1:
            if z > exit_z or z < -stop_z:
                position = 0   # 平仓
        elif position == -1:
            if z < -exit_z or z > stop_z:
                position = 0   # 平仓

        signals.append(position)

    return signals
```

### 第四步：风险管理

```
止损规则：
- 价差Z超过止损阈值（如4σ）→ 立即平仓
- 协整关系p值 > 0.10 → 停止交易此配对
- 单笔最大亏损 ≤ 总资金的2%

持仓限制：
- 同一行业最多3对配对（避免行业集中风险）
- 总配对数 ≤ 20（保证分散化）
- 单对持仓 ≤ 总资金的5%
```


## A股配对交易的实用场景

### 场景1：银行股配对

```
工商银行 vs 建设银行
农业银行 vs 中国银行
平安银行 vs 招商银行

特点：走势高度相关，基本面驱动因素相似
注意：A股银行股配对价差较窄，需要更精细的入场时机
```

### 场景2：AH股配对

```
同一公司A股 vs H股
- 常见折溢价现象
- 价差有均值回归特征
- 需要考虑汇率因素和交易时间差异

注意：沪港通/深港通额度限制和交易成本
```

### 场景3：ETF配对

```
沪深300ETF vs 中证500ETF
上证50ETF vs 沪深300ETF
行业ETF之间的配对（如消费 vs 医药）

优势：流动性好，交易成本低
```

### 场景4：期现套利

```
股指期货 vs 现货ETF
- 当股指期货升水时：买ETF、卖期货
- 当股指期货贴水时：卖ETF、买期货

需要考虑：
- 跟踪误差
- 分红影响
- 保证金成本
- 合约到期换月
```


## 从配对到多因子统计套利

配对交易是统计套利的最简单形式。更高级的版本：

| 层级 | 策略 | 说明 |
|------|------|------|
| Level 1 | 配对交易 | 2只股票，1个价差 |
| Level 2 | 多配对组合 | N对配对，分散化 |
| Level 3 | 多因子套利 | 对冲N个因子暴露，只留Alpha |
| Level 4 | 高频做市 | 毫秒级，超短期均值回归 |

**A股限制**：
- 融券成本高 → 纯多头+对冲（股指期货）更实际
- 涨跌停板 → 配对两端可能无法同时成交
- T+1 → 当日无法平仓，增加隔夜风险

## 协整检验的注意事项

| 问题 | 说明 |
|------|------|
| 样本内偏差 | 历史上协整不代表未来协整 |
| 多重检验 | 测试1000对自然有50对显著（5%水平） |
| 伪回归 | 相关系数高但无协整关系 |
| 结构性变化 | 公司事件（合并、重组）会破坏协整 |
| 数据频率 | 日频数据可能有噪声，周频可能更稳健 |

## 参考阅读

- Ernie Chan, *Algorithmic Trading* — 配对交易最实用的入门书
- Isichenko, *Quantitative Portfolio Management* (2021) — 统计套利理论
- Gatev, Goetzmann, Rouwenhorst (2006), "Pairs Trading: Performance of a Relative-Value Arbitrage Rule"