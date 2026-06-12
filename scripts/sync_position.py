"""
持仓同步脚本 - AkShare获取最新价 → 飞书多维表格

用法:
  python scripts/sync_position.py              # 同步当前价到飞书
  python scripts/sync_position.py --dry-run    # 只打印不写入

功能:
  1. 从飞书多维表格读取持仓记录
  2. 用AkShare获取每只股票/ETF的最新收盘价
  3. 更新飞书中的"当前价"和"可用数量"(T+1逻辑)
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_TOKEN = "WtuibHNPOa1rEBsQVIKcacQynkh"
TABLE_ID = "tblZ5a41tqs0Xtvb"

FIELD_MAP = {
    "证券代码": "fldAVoRGzo",
    "证券名称": "fldfunJaTI",
    "类型": "fldUASntdv",
    "市场": "fldqZMumU9",
    "持仓数量": "fldJ6mP9rg",
    "可用数量": "fldPeg98rG",
    "成本价": "fldvMhpLAl",
    "当前价": "fldrdNWcZ2",
    "行业": "fldE2T6VSY",
    "买入日期": "fldB0gpy89",
    "止损价": "fldsks7UWs",
    "目标价": "fldD0YgOm1",
    "备注": "fldieGJONR",
    "更新时间": "fldivxwDmL",
    "持仓市值": "fldd3GXHqZ",
    "成本金额": "fld2VLCfWp",
    "浮动盈亏": "fldkKoTFxW",
    "盈亏比例": "fldh3hwas4",
}


def lark_cli(args: list[str]) -> dict:
    cmd = ["lark-cli"] + args + ["--as", "user", "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    text = result.stdout.strip() or result.stderr.strip()

    lines = text.split('\n')
    json_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('{'):
            try:
                json_lines.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if json_lines:
        for j in json_lines:
            if j.get("ok"):
                return j.get("data", j)

    if json_lines:
        error_data = json_lines[-1]
        if not error_data.get("ok"):
            print(f"Error: {error_data.get('error', {}).get('message', text)}",
                  file=sys.stderr)
            return error_data

    print(f"Unexpected output: {text[:200]}", file=sys.stderr)
    return {"ok": False, "error": text}


def fetch_positions() -> list[dict]:
    data = lark_cli([
        "base", "+record-list",
        "--base-token", BASE_TOKEN,
        "--table-id", TABLE_ID,
        "--page-size", "100",
    ])

    if not data.get("items"):
        return []

    records = []
    for item in data["items"]:
        fields = item.get("fields", {})
        rec = {"record_id": item.get("record_id", "")}

        for cn_name, field_id in FIELD_MAP.items():
            val = fields.get(field_id)
            if isinstance(val, dict):
                val = val.get("text", val.get("name", val.get("link", "")))
            elif isinstance(val, list) and len(val) > 0:
                first = val[0]
                if isinstance(first, dict):
                    val = first.get("name", first.get("text", ""))
                else:
                    val = first
            rec[cn_name] = val

        records.append(rec)

    return records


def get_latest_price(code: str) -> float | None:
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        row = df[df["代码"] == code]
        if not row.empty:
            return float(row.iloc[0]["最新价"])

        etf_df = ak.fund_etf_spot_em()
        row = etf_df[etf_df["代码"] == code]
        if not row.empty:
            return float(row.iloc[0]["最新价"])

    except ImportError:
        row = lark_cli([
            "base", "+record-search",
            "--base-token", BASE_TOKEN,
            "--table-id", TABLE_ID,
            "--filter",
            json.dumps({"field_name": "证券代码", "operator": "is", "value": [code]}),
        ])

    except Exception as e:
        print(f"  获取 {code} 价格失败: {e}", file=sys.stderr)

    return None


def update_price(record_id: str, price: float) -> bool:
    result = lark_cli([
        "base", "+record-batch-update",
        "--base-token", BASE_TOKEN,
        "--table-id", TABLE_ID,
        "--json", json.dumps({
            "record_id_list": [record_id],
            "fields": {
                FIELD_MAP["当前价"]: price,
                FIELD_MAP["可用数量"]: None,
            }
        }),
    ])

    return result.get("ok", False)


def main():
    parser = argparse.ArgumentParser(description="同步持仓最新价到飞书多维表格")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写入")
    args = parser.parse_args()

    print("正在从飞书读取持仓...")
    positions = fetch_positions()

    if not positions:
        print("没有找到持仓记录，请先在飞书多维表格中添加持仓数据。")
        return

    active = [p for p in positions if p.get("证券代码") and p.get("持仓数量")]
    if not active:
        print("没有有效的持仓记录（证券代码和持仓数量不能为空）。")
        return

    print(f"找到 {len(active)} 条持仓记录，开始获取最新价...\n")

    try:
        import akshare as ak
        print("使用 AkShare 批量获取行情...")
        stock_df = ak.stock_zh_a_spot_em()
        etf_df = ak.fund_etf_spot_em()
        all_prices = {}

        for _, row in stock_df.iterrows():
            all_prices[row["代码"]] = float(row["最新价"])
        for _, row in etf_df.iterrows():
            all_prices[row["代码"]] = float(row["最新价"])

        use_batch = True
    except ImportError:
        print("未安装 akshare，将逐个查询（较慢）")
        print("安装: pip install akshare")
        all_prices = {}
        use_batch = False
    except Exception as e:
        print(f"AkShare 批量获取失败: {e}，将逐个查询")
        all_prices = {}
        use_batch = False

    for pos in active:
        code = str(pos.get("证券代码", "")).strip()
        name = str(pos.get("证券名称", "")).strip()
        qty = pos.get("持仓数量", 0)

        if not code:
            continue

        price = all_prices.get(code) if use_batch else None

        if price is None:
            price = get_latest_price(code)

        if price is None:
            print(f"  ⚠ {code} {name}: 无法获取价格，跳过")
            continue

        current_price = pos.get("当前价")
        if current_price is not None:
            try:
                current_price = float(current_price)
            except (ValueError, TypeError):
                current_price = None

        change = ""
        if current_price and price != current_price:
            diff = price - current_price
            pct = diff / current_price * 100
            change = f" (变化: {diff:+.3f}, {pct:+.2f}%)"

        print(f"  {code} {name}: 最新价 {price:.3f}{change}")

        if not args.dry_run and price != current_price:
            ok = update_price(pos["record_id"], price)
            if ok:
                print(f"    ✓ 已更新到飞书")
            else:
                print(f"    ✗ 更新失败")

    print(f"\n同步完成！{'（dry-run模式，未实际写入）' if args.dry_run else ''}")


if __name__ == "__main__":
    main()