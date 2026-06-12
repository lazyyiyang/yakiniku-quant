# 交易成本建模

> 交易成本是量化策略的隐形杀手——回测不建模成本，实盘一定亏钱

## A股交易成本构成

### 显性成本

| 成本项 | 费率 | 方向 | 说明 |
|--------|------|------|------|
| 佣金 | ~万2.5 | 双向 | 可协商，最低万1 |
| 印花税 | 千0.5 | 卖出 | 2023年减半后 |
| 过户费 | 万0.1 | 双向 | 沪市 |
| 规费 | 万0.687 | 双向 | 经手费+证管费 |

**单次交易总成本估算**：
```
买入：0.025% + 0.01% + 0.0687% ≈ 0.1%（万1）
卖出：0.025% + 0.05% + 0.01% + 0.0687% ≈ 0.15%（万1.5）

一个完整回合（买+卖）：约 0.25%（万2.5）
```


### 隐性成本

#### 滑点（Slippage）

```
滑点 = 实际成交价 - 预期价格

来源：
1. 买卖价差：立即成交必须穿过价差
2. 市场冲击：大单推动价格不利方向移动
3. 延迟：下单到成交的时间差
4. 涨跌停：无法成交的价差无限大

量化估算：
大盘股：5-10 bps（0.05-0.1%）
中盘股：10-30 bps（0.1-0.3%）
小盘股：30-100 bps（0.3-1%）
微盘股：100+ bps（>1%）
```

#### 市场冲击（Market Impact）

```python
def estimate_market_impact(
    trade_value: float,       # 交易金额
    daily_volume: float,       # 日均成交额
    daily_volatility: float,   # 日波动率
    participation_rate: float = 0.1  # 参与率上限
) -> dict:
    """
    A股市场冲击估算模型（平方根模型）
    
    参与率 = 交易金额 / 日均成交额
    冲击 ≈ 日波动率 × 参与率的平方根
    
    经验调整系数：
    - 大盘股：0.5
    - 中盘股：0.8
    - 小盘股：1.2
    """
    participation = trade_value / daily_volume
    
    # 限制参与率
    if participation > participation_rate:
        execution_days = trade_value / (daily_volume * participation_rate)
    else:
        execution_days = 1
    
    # 平方根冲击模型
    impact_bps = daily_volatility * 10000 * (participation ** 0.5)
    
    return {
        'participation_rate': participation,
        'impact_bps': impact_bps,
        'execution_days': execution_days,
        'is_feasible': participation < 0.2  # 超过20%参与率不稳定
    }
```

## 完整成本模型

### A股策略成本核算

```python
def calculate_total_cost_ashare(
    position_value: float,    # 持仓市值
    turnover_annual: float,   # 年换手率（倍数）
    avg_stock_size: str,      # 股票规模类别
    use_limit_orders: bool = True  # 是否限价单
) -> dict:
    """
    A股策略全年成本估算
    """
    # 显性成本
    commission = 0.00025 * 2       # 双向佣金万2.5
    stamp_tax = 0.0005 * 1          # 卖出印花税千0.5
    transfer_fee = 0.00001 * 2     # 双向过户费
    explicit_cost = commission + stamp_tax + transfer_fee
    
    # 滑点/冲击成本
    impact_bps = {
        'mega_cap': 3,     # 超大盘 3bps
        'large_cap': 8,     # 大盘 8bps
        'mid_cap': 20,      # 中盘 20bps
        'small_cap': 50,    # 小盘 50bps
        'micro_cap': 150    # 微盘 150bps
    }
    
    if not use_limit_orders:
        # 市价单滑点更大
        impact_multiplier = 1.5
    else:
        impact_multiplier = 1.0
    
    implicit_single = impact_bps.get(avg_stock_size, 20) * impact_multiplier / 10000
    
    # 单次完整交易成本
    single_trade_cost = explicit_cost + implicit_single * 2
    
    # 年度总成本 = 单次成本 × 年换手率
    annual_cost = single_trade_cost * turnover_annual
    
    return {
        'explicit_single': explicit_cost,
        'implicit_single': implicit_single,
        'total_single_trade': single_trade_cost,
        'annual_turnover': turnover_annual,
        'annual_cost_pct': annual_cost,
        'annual_cost_amount': position_value * annual_cost,
        'break_even_return': annual_cost  # 需要多少收益才能覆盖成本
    }
```

### 策略盈亏平衡点

```
换手率           大盘股       中盘股       小盘股
-----------     ---------    ---------    ---------
月度(12x)        3.6%         7.2%         16.8%
双周(24x)        7.2%        14.4%         33.6%
周度(52x)       15.6%        31.2%         72.8%
日度(252x)      75.6%       151.2%         不可能

含义：
- 大盘股月度换仓：策略需年化跑赢基准3.6%以上
- 中盘股月度换仓：策略需年化跑赢基准7.2%以上
- 小盘股周度换仓：几乎不可能覆盖成本
- 日度换仓：唯有超大盘股+低冲击才可能
```


## 执行优化

### 交易时间优化

```
A股日内成交分布：
- 9:30-10:00：成交活跃，开盘冲击大
- 10:00-11:30：成交平稳
- 13:00-14:00：成交回升
- 14:00-14:30：成交平稳
- 14:30-15:00：尾盘拉升/杀跌

建议执行时段：
- 避开开盘30分钟（波动大、冲击大）
- 避开尾盘30分钟（做净值/异常波动）
- 最佳执行时段：10:00-11:20, 13:00-14:20
```

### 订单拆分

```python
def vwap_execution(
    total_shares: int,
    volume_profile: dict  # 各时段成交量占比
) -> list:
    """
    VWAP执行：按历史成交量比例拆分大单
    
    A股典型时段成交量分布：
    9:30-10:00 → 15%
    10:00-11:30 → 30%
    13:00-14:00 → 25%
    14:00-14:57 → 25%
    14:57-15:00 → 5%
    """
    executions = []
    for period, pct in volume_profile.items():
        executions.append({
            'period': period,
            'shares': int(total_shares * pct)
        })
    return executions
```

### 限价单策略

```
限价单执行：
1. 定价限价单：挂在买一/卖一价，等待成交
2. 改进限价单：挂在买二价，提高成交概率
3. 冰山订单：只显示部分挂单量

A股限制：
- A股没有原生冰山订单功能
- 需要通过算法模拟（小量分批挂单）

策略建议：
- 流动性好的股票 → 限价单（节省滑点）
- 流动性差的股票 → 市价单（避免无法成交）
- 大单拆分 → VWAP/TWAP算法
```


## 回测中的成本建模

```python
def apply_transaction_costs_ashare(
    returns: pd.Series,
    trades: pd.DataFrame,
    stock_sizes: dict  # 股票 → 规模类别
) -> pd.Series:
    """
    在回测中应用A股真实的交易成本
    """
    cost_config = {
        'mega_cap': {'explicit': 0.0008, 'impact': 0.0005},
        'large_cap': {'explicit': 0.0008, 'impact': 0.0015},
        'mid_cap': {'explicit': 0.0008, 'impact': 0.003},
        'small_cap': {'explicit': 0.0008, 'impact': 0.007},
        'micro_cap': {'explicit': 0.0008, 'impact': 0.02},
    }
    
    total_cost = 0
    for _, trade in trades.iterrows():
        size = stock_sizes.get(trade['stock'], 'mid_cap')
        cfg = cost_config[size]
        single_cost = cfg['explicit'] + cfg['impact']
        total_cost += trade['value'] * single_cost
    
    net_returns = returns.copy()
    net_returns.iloc[-1] -= total_cost / returns.sum()
    
    return net_returns
```

## 参考阅读

- Johnson, *Algorithmic Trading and DMA* — 执行算法经典
- Webster, *Handbook of Price Impact Modeling* (2023) — 价格冲击最新研究
- Almgren & Chriss (2001), "Optimal Execution" — 执行优化奠基论文