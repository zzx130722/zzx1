"""生成 pandas 练习用的示例数据（可重复运行，结果固定）。

为什么单独写一个生成脚本，而不是直接把 CSV 提交了事：
  1. 数据是"造"出来的，得有据可查 —— 你能看到每一列的取值规则；
  2. 想换规模（比如把订单数从 60 改成 6000）改一个常量就行；
  3. 固定随机种子，任何人重跑都得到一模一样的文件，笔记里的数字才对得上。

用法：
    ./.venv/Scripts/python.exe pandas/make_data.py
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
SEED = 20261022

REGIONS = ["华东", "华北", "华南", "西南"]
PRODUCTS = {
    "笔记本": 4999.0,
    "显示器": 1299.0,
    "键盘": 399.0,
    "鼠标": 129.0,
    "耳机": 799.0,
}


def make_sales(n: int = 60) -> pd.DataFrame:
    """练习一用：一张干净的销售明细表。"""
    rng = random.Random(SEED)
    rows = []
    for i in range(n):
        product = rng.choice(list(PRODUCTS))
        rows.append(
            {
                "order_date": f"2026-{rng.randint(7, 9):02d}-{rng.randint(1, 28):02d}",
                "region": rng.choice(REGIONS),
                "product": product,
                "quantity": rng.randint(1, 5),
                "unit_price": PRODUCTS[product],
            }
        )
    return pd.DataFrame(rows)


def make_orders(n: int = 40) -> pd.DataFrame:
    """练习二用：订单表，故意留了缺失值和一个"孤儿"客户。"""
    rng = random.Random(SEED + 1)
    rows = []
    for i in range(n):
        rows.append(
            {
                "order_id": 1000 + i,
                # 故意让第 3、11、25 行的 customer_id 缺失（模拟表单没填）
                "customer_id": None if i in (3, 11, 25) else rng.randint(1, 12),
                # 故意让第 5、17 行的 amount 缺失（模拟支付回调丢失）
                "amount": None if i in (5, 17) else rng.randint(50, 900),
                "order_date": f"2026-09-{rng.randint(1, 30):02d}",
            }
        )
    return pd.DataFrame(rows)


def make_customers(n: int = 12) -> pd.DataFrame:
    """练习二用：客户表，故意有 2 个重复的 customer_id。

    重复不是笔误，是现实：同一家公司被录入了两次，或者系统里主数据没去重。
    merge 时它会悄无声息地把订单行数放大 —— 这是本练习最重要的坑。
    """
    rng = random.Random(SEED + 2)
    cities = ["上海", "北京", "广州", "成都", "杭州", "深圳"]
    rows = []
    for cid in range(1, n + 1):
        rows.append(
            {
                "customer_id": cid,
                "name": f"客户{cid:02d}",
                "city": rng.choice(cities),
            }
        )
    # 客户 4 和客户 7 在系统里各存了两份（城市填得不一致）
    rows.append({"customer_id": 4, "name": "客户04", "city": "上海"})
    rows.append({"customer_id": 7, "name": "客户07", "city": "北京"})
    return pd.DataFrame(rows)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    sales = make_sales()
    orders = make_orders()
    customers = make_customers()

    # utf-8-sig：带 BOM 的 UTF-8。Windows 上用 Excel 直接打开不会乱码。
    # 代价是读取时要指定 encoding="utf-8-sig"，否则第一个列名前面会多一个 \ufeff。
    # 这个细节在练习一里专门演示了一次。
    sales.to_csv(DATA_DIR / "sales.csv", index=False, encoding="utf-8-sig")
    orders.to_csv(DATA_DIR / "orders.csv", index=False, encoding="utf-8-sig")
    customers.to_csv(DATA_DIR / "customers.csv", index=False, encoding="utf-8-sig")

    print(f"已生成 {DATA_DIR}")
    for name, df in [("sales.csv", sales), ("orders.csv", orders), ("customers.csv", customers)]:
        print(f"  {name:<14} {len(df):>3} 行 × {df.shape[1]} 列")
    print()
    print("演示用的缺失 / 重复（这些是练习二的重点）：")
    print(f"  orders.customer_id 缺失 {orders['customer_id'].isna().sum()} 个")
    print(f"  orders.amount      缺失 {orders['amount'].isna().sum()} 个")
    dup = customers["customer_id"].duplicated().sum()
    print(f"  customers.customer_id 重复 {dup} 个")


if __name__ == "__main__":
    main()
