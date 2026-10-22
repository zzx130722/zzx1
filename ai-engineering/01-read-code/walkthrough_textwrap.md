# 走查：`textwrap.TextWrapper._wrap_chunks`（Python 3.13 标准库，238–339 行）

选这段的理由：它 **102 行、没有任何 import、没有任何外部依赖**，却包含了几乎所有"读大代码"会遇到的麻烦 ——
私有方法、改传入列表的副作用、为了性能做的反直觉处理、嵌套循环 + `while...else`、一个写了四行的布尔表达式。
把它读通，比读十个玩具示例有用。

配套脚本：`experiments.py`（7 个实验，对应下面 7 段）。**先跑脚本、先自己猜**，再回来读。

```powershell
cd $HOME\WorkBuddy\2026-10-13-16-35-32\dev-basics
.venv\Scripts\python.exe -X utf8 ai-engineering\01-read-code\experiments.py
```

---

## 第 0 步：先别读实现，只读签名和 docstring

```python
def _wrap_chunks(self, chunks):
    """_wrap_chunks(chunks : [string]) -> [string]
```

docstring 里有 7 句关键的话，逐句翻译成"我该怎么测"：

| 原文 | 意思 | 对应的测试 |
|---|---|---|
| `Chunks correspond roughly to words and the whitespace between them` | chunk 是「词」或者「一整段连续空白」，空白自己也是一块 | `_split_chunks("aa   bb cc")` 切出 5 块，中间 `'   '` 单独一块 |
| `each chunk is indivisible (modulo 'break_long_words')` | 默认不能把一个词拆开 | 长单词要么整块进下一行，要么被 `_handle_long_word` 硬切 |
| `Chunks should not have internal whitespace` | 前置条件：调用方保证块内没有空白 | 这是**契约**，不是它要检查的东西 |
| `Whitespace chunks will be removed from the beginning and end of lines` | 行首行尾空白会被删 | 但**中间**的空格保留，会挂在上一行末尾 |
| `some lines may be longer than this`（`break_long_words=False` 时） | 宽度是软保证 | 长单词会超宽 |
| `length 'self.width' or less` | 但有 `indent` 时要扣掉缩进 | `width = self.width - len(indent)` |
| 两个 `raise ValueError` | 宽 ≤ 0、placeholder 放不下，直接崩 | 这是**它能崩**的唯一两种情况 |

**这 7 条就是全部验收标准。** 后面 102 行都是在满足它们，没有一条是随意的。

---

## 段 1（251–260）：前置校验，把丑话说完再干活

```python
lines = []
if self.width <= 0:
    raise ValueError("invalid width %r (must be > 0)" % self.width)
if self.max_lines is not None:
    if self.max_lines > 1:
        indent = self.subsequent_indent      # 多行时用「后续行缩进」
    else:
        indent = self.initial_indent         # 只有一行时用「首行缩进」
    if len(indent) + len(self.placeholder.lstrip()) > self.width:
        raise ValueError("placeholder too large for max width")
```

两个细节：

1. **为什么 `raise` 放在最前面**：后面的主体逻辑因此可以假定「宽度是正的、placeholder 一定放得下」，不用每处都 `if`。这是"边界校验前置"的标准写法 —— 你在自己项目里也该这么写。
2. **`indent` 这个局部变量在这里只用来做一次判断**，真正的排版缩进在段 4 里会重新赋一遍。读代码时容易以为它是"设置缩进"，其实是"用最坏情况的缩进去验证 placeholder 是否放得下"。

---

## 段 2（262–264）：三行代码，为了省掉一次 O(n²)

```python
# Arrange in reverse order so items can be efficiently popped
# from a stack of chucks.          ← 注意：chucks 是拼错的，应为 chunks
chunks.reverse()
```

后面所有取元素的地方都是 `chunks[-1]` 读、`chunks.pop()` 取 —— 全都发生在**尾部**。
所以先把列表倒过来，就能一直用 O(1) 的 `pop()`，而不是 O(n) 的 `pop(0)`。

这不是"风格偏好"，是量级差异。脚本里的实测（n = 50000）：

| 写法 | 耗时 |
|---|---|
| `pop()` 从尾部取完整个列表 | 约 0.0025 s |
| `pop(0)` 从头部取完整个列表 | 约 2.78 s |

**差三个数量级。** 每次跑的具体数字会变，量级不会。

另一个容易读错的地方：`chunks.reverse()` 是**原地反转**，改的是调用方传进来的那个列表。
顺序看起来"反了"，但取出来的元素顺序**没变** —— 因为读的位置也一起反了。脚本里用
`["a","b","c"]` 反转后再逐个 `pop()`，拿到的仍然是 `a, b, c`，有 assert 兜着。

---

## 段 3（266–285）：每一轮只负责"攒一行"

```python
while chunks:
    cur_line = []          # 这一行已经收下的块
    cur_len = 0            # 它们的总长度（自己维护，不反复 sum）
    if lines:  indent = self.subsequent_indent
    else:      indent = self.initial_indent
    width = self.width - len(indent)
    if self.drop_whitespace and chunks[-1].strip() == '' and lines:
        del chunks[-1]     # 行首的空白块直接扔掉
```

三个要点：

- **`cur_len` 是手工维护的缓存**。段 5 里 `cur_len += l`，段 6 里 `cur_len -= ...`，段 5 的 `_handle_long_word` 之后又用 `sum(map(len, cur_line))` 重算一次。**维护缓存的地方越多，越容易忘。** 这里作者自己就在一处用回算了 —— 这就是 review 时该盯的位置。
- **`width` 已扣掉缩进**，所以下面所有比较都是对"这一行的可用宽度"。
- **`and lines` 这个条件**：只在"已经不是第一行"时才丢行首空白。第一行开头的空白是另一条逻辑删掉的 —— 段 6（行尾空白）会把整块 `'   '` 当行尾一并丢掉。脚本里 `wrap("   aa bb   ", width=3)` 得到 `['aa', 'bb']`，前三格空白就是这么消失的。

---

## 段 4（287–303）：塞到塞不下为止

```python
while chunks:
    l = len(chunks[-1])
    if cur_len + l <= width:          # 注意是 <=，正好填满也算放得下
        cur_line.append(chunks.pop())
        cur_len += l
    else:
        break                          # 这一行满了
if chunks and len(chunks[-1]) > width:              # 比「整行」还宽
    self._handle_long_word(chunks, cur_line, cur_len, width)
    cur_len = sum(map(len, cur_line))                # 重算！
```

- `<=` 不是 `<`：宽度恰好相等时放得下，这是最容易写错的一处边界。
- 两个条件不是一回事：**「放不进当前行」**（break 那里）和 **「放不进任何行」**（第二个 if）。
  后者才需要硬切。把这两个混在一起，就会出现"明明还能放下一行的词被切碎"。
- `cur_len = sum(...)` 这次重算是必须的，因为 `_handle_long_word` 可能改了 `cur_line`。
  **这类"回算"是代码里的自卫措施，不是冗余** —— 后面 review 那节会看到 AI 把它当 bug 报出来的情况。

---

## 段 5（305–308）：删行尾空白，顺手把缓存也改对

```python
if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
    cur_len -= len(cur_line[-1])
    del cur_line[-1]
```

只有 4 行，但演示了"删除元素时必须同步改缓存"这条铁律。
少写 `cur_len -= ...` 这一行，`cur_len` 就会偏大，后续判断会把词错误地挤到下一行。

---

## 段 6（310–337）：这一行到底要不要收尾

这是全函数最难的一段。外层 `if` 的条件写了 6 行：

```python
if (self.max_lines is None                          # ① 不限行数
    or len(lines) + 1 < self.max_lines              # ② 还没到上限
    or (not chunks or                                # ③ 内容已经发完
        self.drop_whitespace and len(chunks) == 1 and not chunks[0].strip())
       and cur_len <= width):                       # 且没超宽
    lines.append(indent + ''.join(cur_line))         # 正常收下这一行
```

拆成三个"或"来读，就一点不难：

1. **不限行数** → 不用考虑截断，收。
2. **还没写到第 max_lines 行** → 收。
3. **剩下的块已经空了**（`not chunks`，或者只剩一块纯尾巴空白）**且这一行没超宽** → 收。
   也就是说：内容正好排完时，**不该多一个 `...`**。

脚本里验证过这第三种：

| 输入 | 结果 |
|---|---|
| `wrap("aa bb cc dd ee", 6, max_lines=2, placeholder="...")` | `['aa bb', 'cc...']` ← 真截断了 |
| `wrap("aa bb cc dd", 6, max_lines=2, placeholder="...")` | `['aa bb', 'cc dd']` ← 刚好排完，不加省略号 |

`else` 分支干三件事，按顺序：

```python
while cur_line:
    if cur_line[-1].strip() and cur_len + len(self.placeholder) <= width:
        cur_line.append(self.placeholder)     # ① 末尾还有余地，直接塞省略号
        lines.append(indent + ''.join(cur_line))
        break
    cur_len -= len(cur_line[-1])              # ② 塞不下，就把最后一个词退掉再试
    del cur_line[-1]
else:                                          # ← while 正常跑完（一次都没 break）
    if lines:                                  # ③ 这一行被退空了，退回到上一行去加省略号
        prev_line = lines[-1].rstrip()
        if len(prev_line) + len(self.placeholder) <= self.width:
            lines[-1] = prev_line + self.placeholder
            break
    lines.append(indent + self.placeholder.lstrip())
break
```

**`while ... else` 在这里是关键。** `else` 不是"if 不成立时执行"，而是"循环**没被 break 打断**、正常跑完时执行"。
这里的语义正好是：**所有词都退光了还没塞下省略号** → 那就去上一行加，或者单独占一行。

读到 `while/for ... else` 时的通用办法：把 `else` 在心里念成 **"如果一次 break 都没发生"**。

那个 `>` 和 `>=` 也值得留意：`cur_len + len(placeholder) <= width` 是"塞得下"，草率的改法会写成 `<`，
于是只剩一个字符的余地时也会退词。这类边界改动**单看 diff 完全看不出问题**，必须跑用例。

---

## 三个反直觉点（也是 review 的抓手）

1. **数据结构顺序和阅读顺序相反**（段 2）。不看到 `chunks[-1]` 就理解不了为什么反转。
2. **`l` 当变量名**（288 行）。合法，但 `flake8` 的 E741（ambiguous variable name）会报警，PEP 8 不建议单字符 `l`（和数字 1 难分）。
3. **注释里 `chucks` 拼错了**（263 行），应为 `chunks`。这段代码在 CPython 里躺了很多年，没有人改 ——
   说明**注释的错误不会被任何测试发现**。这也解释了为什么 code review 不能只看 CI 绿不绿。

---

## 你的作业：自己读一段，别问我

读 `csv.DictReader`（`csv.py`，标准库），回答三个问题，写完再让 AI 对答案：

1. 它为什么把 `fieldnames` 缓存成 `self._fieldnames`，而不是每次从 `reader` 里取？
2. `line_num` 和文件的行号**一定相等**吗？什么时候不等？
3. 如果 CSV 的数据行比表头长，`restkey` 会把它放到哪里？比表头短呢，`restval` 补什么？

> 提示：`DictReader` 只有 60 行左右，比 `_wrap_chunks` 简单，但它的坑在"状态跨行保存"上 ——
> 这类"对象在多次迭代之间记住东西"的代码，读的时候要按**时间顺序**在纸上画状态表，而不是从上往下看。

---

## 一句话总结

读长函数的顺序永远是：**先读契约（签名 + docstring）→ 再找"这段在担心什么"（每个 if 都在防一种情况）→ 最后才看具体实现**。
反过来（从第一行往下啃）会读到一半就丢主线，这是新手最常见的读法，也是最容易放弃的读法。
