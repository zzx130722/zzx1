# -*- coding: utf-8 -*-
"""销售报表 —— 重构前的版本。

这是反面教材：一个函数都没有，所有逻辑平铺在主流程里。
对照 refactored/ 看差异，但不要学这里的任何写法。

用法：
    python legacy_sales_report.py                      # 默认读 data/sales_clean.csv
    python legacy_sales_report.py data/sales_dirty.csv  # 指定输入
"""
import csv
import sys

# 读数据
if len(sys.argv) > 1:
    f = open(sys.argv[1])
else:
    f = open('data/sales_clean.csv')
rows = []
for line in csv.reader(f):
    rows.append(line)
f.close()
# print(len(rows))  # 调试用，先留着

# 按区域汇总销售额
a = {}
amt = 0.0
for i in range(1, len(rows)):
    row = rows[i]
    try:
        amt = float(row[3])
    except:
        pass
    if row[1] in a:
        a[row[1]] = a[row[1]] + amt
    else:
        a[row[1]] = amt

# 排序：销售额从高到低
items = []
for k in a:
    items.append([k, a[k]])
for j in range(len(items) - 1):
    if items[j][1] < items[j + 1][1]:
        t = items[j]
        items[j] = items[j + 1]
        items[j + 1] = t

# 拼报表
s = ''
total = 0.0
for it in items:
    v = round(it[1], 2)
    s = s + it[0] + ' : ' + str(v) + '\n'
    total = total + v
s = s + 'TOTAL : ' + str(round(total, 2)) + '\n'

print(s)

# 存一份
out = open('report_legacy.txt', 'w')
out.write(s)
out.close()

# 老版本留着，万一要回滚
# for k in sorted(a.keys()):
#     print k, a[k]
