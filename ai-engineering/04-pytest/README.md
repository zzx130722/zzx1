# 04 · pytest 入门 + 人工把关

## 装好了什么

```
pytest 9.1.1
```

装在项目 venv 里（不是全局）。跑法一律用 venv 的 python：

```powershell
cd $HOME\WorkBuddy\2026-10-13-16-35-32\dev-basics

# 正式测试（12 passed, 5 xfailed）
.venv\Scripts\python.exe -X utf8 -m pytest ai-engineering\04-pytest -q

# 待审查的 AI 测试（11 passed，其中 4 个是假绿）
cd ai-engineering\04-pytest
..\..\.venv\Scripts\python.exe -X utf8 -m pytest ai_tests_to_review.py -v
```

> `-q` 是安静模式，`-v` 是逐条列出。出问题时加 `-x` 遇到第一个失败就停，
> 加 `--tb=short` 让失败堆栈短一点。

## 四个文件的分工

| 文件 | 是什么 | 期望结果 |
|---|---|---|
| `test_report.py` | **正确示范**：对 `refactored/report.py` 的 8 个测试函数（12 条用例） | 全绿 |
| `test_buggy_contract.py` | 把 03 的 **5 个 bug 用 `xfail(strict=True)` 固定** | 5 xfailed |
| `ai_tests_to_review.py` | AI 生成的 8 个测试，**4 个是假绿** | 11 passed（别被数字骗了） |
| `REVIEW-ANSWERS.md` | 上面那份的答案 + 人工把关清单 | 先自己读代码判断，再看 |

`conftest.py` 只做一件事：把 `02-refactor/` 和 `03-debug-drill/` 加进 `sys.path`，
这样测试里能直接 `from refactored.report import ...`。

## pytest 只要记住四条

**① 文件名 `test_*.py`，函数名 `test_*`，用 `assert`**

```python
def test_summarize_empty_returns_empty():
    assert summarize([]) == []
```

不需要 `class TestXxx(unittest.TestCase)`，不需要 `self.assertEqual`。
`assert` 失败时 pytest 会自己把两边的值都打出来。

**② `@pytest.mark.parametrize` 把一张表格变成多条测试**

```python
@pytest.mark.parametrize(("value", "expected"), [
    (Decimal("2645.50"), "2645.5"),
    (Decimal("3509.00"), "3509.0"),
])
def test_format_amount(value, expected):
    assert format_amount(value) == expected
```

好处是失败时能一眼看出**是哪一行数据**挂的，而不是"某个循环里的某次断言失败"。

**③ `xfail(strict=True)`：把"已知的错"变成"会提醒你的债"**

```python
@pytest.mark.xfail(strict=True, reason="bug: cart=[] 是可变默认参数")
def test_add_to_cart_does_not_leak():
    assert add_to_cart("apple") == ["apple"]
    assert add_to_cart("banana") == ["banana"]   # 现在必挂
```

- 现在：挂 → 标记为 xfail → 套件仍然绿
- **修好之后**：通过 → `strict=True` 让它变成 `FAILED (XPASS(strict))` → 你去删掉那行标记

这是它和 `try/except` 的本质区别：**一个是记账，一个是掩盖**。
`test_buggy_contract.py` 里 5 条全是这个写法。

**④ fixture：每条测试前的准备动作**

```python
@pytest.fixture(autouse=True)
def fresh_module():
    importlib.reload(buggy_app)
    yield
```

`autouse=True` 表示每条测试都自动执行。这里用来重置模块级状态
（`buggy_app` 里那个可变默认参数会跨测试污染，不 reload 的话测试顺序一变结果就变）。

**测试之间必须互不影响** —— 这是 pytest 的第一原则，比"测得全"更重要。
一条测试挂了导致另一条也挂，你会花双倍时间去查一个 bug。

## 验收：不看代码回答

1. `xfail(strict=True)` 修好之后会发生什么？为什么这样设计？
2. `parametrize` 和"在测试里写 for 循环"的区别是什么？（提示：失败时你看得见哪一行吗）
3. `test_every_order_has_positive_amount` 为什么是假绿？（`REVIEW-ANSWERS.md` 第 4 条）
4. 你的项目里哪个函数最容易写测试？哪个最难？难的那个该怎么拆？

第 4 题的答案在 `02-refactor/REFACTOR-NOTES.md` 第二节最后一段：
`report.py` 里两个函数不碰文件不打印，所以一行就能测；原版那段面条代码离不开 CSV，根本没法测。
**"好不好测"本身就是设计质量的度量。**
