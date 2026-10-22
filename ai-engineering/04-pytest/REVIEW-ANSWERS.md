# 人造把关：这 8 个测试里，4 个什么都没测

## 先看一个实验

把 `refactored/report.py` 里的 `format_amount` 整个函数体换成一行：

```python
def format_amount(value: Decimal) -> str:
    return "WRONG"
```

然后跑 `pytest ai_tests_to_review.py`，结果：

```
4 failed, 7 passed
```

**函数已经 100% 错了，还有 7 个测试是绿的。** 那 7 个里就藏着这一节要讲的东西。

---

## 四个假绿，逐个拆

### 1. `test_render_returns_something`

```python
assert text is not None
```

`render()` 只要不返回 `None` 就通过 —— 而它是个返回 `str` 的函数，**几乎不可能返回 `None`**。
所以这条断言的信息量是零。它唯一能抓到的是"有人把函数体删空了"。

**它会漏掉**：格式全错、金额算错、区域漏掉、TOTAL 多打一位 —— 全绿。

**改法**：断言完整字符串，一个字符都不放过。
```python
assert render([("East", Decimal("10.00"))]) == "East : 10.0\nTOTAL : 10.0\n"
```

---

### 2. `test_format_amount_handles_zero`

```python
try:
    assert format_amount(Decimal("0.00")) == "0"
except AssertionError:
    pass
```

这条**有两处错，一处比一处严重**：

1. 期望值写错了：`format_amount(Decimal("0.00"))` 的正确结果是 `"0.0"`，不是 `"0"`
2. `except AssertionError: pass` 把断言失败**吃掉**了 —— 于是这条测试永远绿

第 2 点是致命的。**一个测试最不能做的事，就是吞掉自己的断言异常。**
写这段代码的人大概是想"这个用例可能是边界，先别让它挂"——那就该用 `pytest.mark.xfail`，
而不是 try/except。前者会记录"这里预期失败"，后者只是让问题消失。

**这类测试比没有测试更危险**：你以为这个边界被保护了，实际上没有。

---

### 3. `test_summarize_groups_by_region`

```python
monkeypatch.setattr(report, "summarize", lambda orders: [("Mock", Decimal("1"))])
assert report.summarize([]) == [("Mock", Decimal("1"))]
```

它把 `summarize` **换成了自己的假实现**，然后验证这个假实现返回了什么。
测的是 lambda，不是被测代码。

这是 mock 用错方向的典型：**mock 应该替换「依赖」（数据库、网络、时间），不是替换「被测对象」。**
把被测对象 mock 掉，这个测试就只剩"Python 的赋值是有效的"这一条结论了。

**改法**：`summarize` 是纯函数（输入 list，输出 list），根本不需要 mock。直接喂数据、断言结果。

---

### 4. `test_every_order_has_positive_amount`

```python
orders: list[Order] = []
for item in orders:
    assert item.amount > 0
```

`orders` 是空列表，**循环体一次都没执行**，所以这条测试什么也没断言。

这种 bug 特别隐蔽，因为代码长得完全合理 —— 它看起来像是在巡检所有订单。
真相是：数据源是空的，巡检了个寂寞。而且它会一直绿，直到有人手动往 `orders` 里加一条。

**改法**：先断言数据非空，再巡检。
```python
assert orders, "测试数据不该是空的"
for item in orders:
    assert item.amount > 0
```

或者更好：用 `pytest.mark.parametrize` 把用例一条条列出来，空列表就变成"0 个用例"，
pytest 会直接报 `no tests ran`，不会假装通过。

---

## 四个里面哪些是真有效的

| 测试 | 判定 | 说明 |
|---|---|---|
| `test_format_amount_edge_cases`（4 条参数化） | ✅ 有效 | 改坏后立刻红，证明它真的在断言 |
| `test_summarize_empty_returns_empty` | ✅ 有效 | 但只覆盖空输入，单靠它不够 |
| `test_summarize_total_is_manually_computed` | ✅ 有效 | 期望值是手算的 `15.50`，没有用被测代码算自己 |
| `test_render_line_count_matches_regions` | ⚠️ 偏弱 | 只数行数，不验证每行内容。金额算错、区域名拼错，它都发现不了 |

"偏弱"不等于"没用"：它能抓住"少打了一行 TOTAL"这类结构问题。
但一个模块如果只有这种测试，等于没有测试。

---

## 人工把关清单（拿到 AI 生成的测试，逐条过）

**先做一件事**：把被测代码故意改坏一处（返回错误值、删掉一个分支），看测试红不红。
不红的，就是假绿。这一条能筛掉 90% 的垃圾测试。

然后逐条检查：

1. **有没有 `assert` 顶着返回值？** 只有 `is not None` / `len(x) > 0` 的，补充具体断言
2. **有没有 try/except 包住断言？** 有就是假绿，直接删
3. **有没有 mock 掉被测函数本身？** 有就是自娱自乐
4. **循环/推导式里的断言，数据源确定非空吗？** 空集合 = 零断言
5. **期望值是写死的还是算出来的？** 用被测代码算期望值 = 自己证明自己
6. **只测了 happy path 吗？** 边界（空、0、负数、超长、并列）各来一条
7. **断言是"相等"还是"包含"？** `assert "East" in text` 抓不到金额错误，该用 `==`
8. **测试名说的是行为还是函数名？** `test_summarize_2` 是无信息量，`test_summarize_tie_breaks_by_region_name` 才是

---

## 让 AI 生成测试的正确问法

```text
被测代码：<贴函数>
它的契约：<输入什么、输出什么、什么情况下抛什么异常>

请生成测试，要求：
1. 每个测试只验证一件事，测试名要说明「验证的是什么行为」
2. 期望值必须写死在测试里，**不要调用被测函数去计算期望值**
3. 必测：空输入、边界值（0 / 1 / 最大值）、并列/相等的情况、非法输入
4. 不要 catch AssertionError，不要 mock 被测函数本身
5. 每条测试后面加一行注释：**把它对应的实现改坏成什么样，它会红**
```

第 5 条是关键。**能说清"改坏什么会让它红"的测试，才是真测试。**
说不出来的，AI 自己也知道它是个摆设。

---

## 自测

1. 为什么 `except AssertionError: pass` 比没有测试更糟？
2. `test_render_line_count_matches_regions` 要改成什么样才算"有效"？
3. 你给 `split_bill`（03 里那个整除 bug）写测试，最少要几条？分别测什么？
4. `xfail(strict=True)` 和 `try/except` 都能让"预期失败的测试"不报警，区别是什么？
   （提示：修好之后呢）
