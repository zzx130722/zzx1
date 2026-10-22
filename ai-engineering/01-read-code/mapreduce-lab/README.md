# HitCounts：一段 20 行的 MapReduce，缺了两块就得自己补

你贴的那段代码长这样（tutorial 里最常被抄的 mrjob 例子）：

```python
class HitCounts(MRJob):
    def extract_url(self, line):
        """Extract the generated url from the log line."""
        ...
    def extract_year_month(self, line):
        """Return the year and month portions of the timestamp."""
        ...
    def mapper(self, _, line):
        url = self.extract_url(line)
        period = self.extract_year_month(line)
        yield (period, url), 1
    def reducer(self, key, values):
        yield key, sum(values)
```

它想干的事一句话说完：**读访问日志，统计「每个月里每个 URL 被请求了多少次」**。

---

## 一、先看出这四个细节，比跑通更重要

### ① 两个 `...` 不是省略号，是「没写」

`extract_url` 和 `extract_year_month` 的函数体只有一个 `...`。
Python 里 `...` 是合法表达式（Ellipsis），**所以这段代码语法没错、能 import、不报错**，
但一跑就 `TypeError: cannot unpack non-sequence` / 或者更隐蔽地返回 `None`。

这是教程代码最常见的坑：它把最关键的正则藏起来了，只留下结构。
**结构能看懂 ≠ 会写。** 这两个函数本身不难，难的是「日志里 URL 长什么样」这件事你得知道。

### ② `mapper(self, _, line)` 的第一个参数为什么是 `_`

mrjob 喂给 mapper 的是 `(key, line)` 两个值，key 是**这一行在文件里的字节偏移量**。
这个统计用不到它，于是用 `_` 表示「我知道你给了，但我不要」。
——`_` 不是语法要求，只是 Python 的约定俗成。写成 `def mapper(self, offset, line)` 完全等价。

### ③ key 是一个元组，这决定了它只能在 mrjob 里跑

`yield (period, url), 1` 里的 key 是 `('2016-01', '/index.html')`。
Hadoop 和 MapReduce 的 key 在框架层面**都是字节串**，元组是 Python 的东西。
mrjob 之所以能这么写，是因为它默认用 **JSON 协议**把元组序列化成 `["2016-01", "/index.html"]` 再传。

换成裸 Hadoop Streaming（不用 mrjob），你得自己拼成 `"2016-01\t/index.html"` 这样的字符串，
reducer 里再 split 回来。**「能用元组当 key」是 mrjob 送的便利，不是 MapReduce 的本性。**

### ④ reducer 的 `values` 是迭代器，只能遍历一次

```python
def reducer(self, key, values):
    yield key, sum(values)      # 可以
```

```python
def reducer(self, key, values):
    total = sum(values)
    cnt = len(values)           # ← 这里永远是 0，因为 values 已经被 sum 走完了
```

Hadoop 是**边读边喂**的：10 亿条 value 不可能先在内存里堆成 list。
所以 `values` 是个一次性迭代器。想用两次就得先 `values = list(values)`——但那也就把内存吃了。

---

## 二、补完之后真跑（实测输出）

两个 `...` 我在 `hit_counts.py` 里补成了正则。跑：

```powershell
cd $HOME\WorkBuddy\2026-10-13-16-35-32\dev-basics\ai-engineering\01-read-code\mapreduce-lab
..\..\..\.venv\Scripts\python.exe -X utf8 hit_counts.py -r inline sample.log
```

```
["2016-01", "/blog/mapreduce"]	1
["2016-01", "/index.html"]	2
["2016-01", "/pricing"]	1
["2016-02", "/api/hits"]	1
["2016-02", "/blog/mapreduce"]	1
["2016-02", "/index.html"]	1
```

`-r inline` 是 mrjob 的单进程模拟器，不开 Hadoop 也不 fork 子进程，
就是老老实实 map 一遍、shuffle 一遍、reduce 一遍。**学逻辑用它最干净。**

---

## 三、四个坑，每个都配了实测证据

### 坑 1（最要命）：mrjob 在 Python 3.13 上根本 import 不进来

```
ModuleNotFoundError: No module named 'pipes'
```

`pipes` 在 3.11 被标废弃、**3.13 删除**；`distutils` 在 **3.12 删除**。
而 mrjob 最新版就是 **0.7.4（2021 年）**，源码里三处都用了：

| mrjob 要的 | Python 3.13 现状 | 补丁（在本目录 `compat_stubs/`） |
|---|---|---|
| `pipes.quote` | 已删除 | 一行 `from shlex import quote` |
| `distutils.spawn.find_executable` | 已删除 | `shutil.which` |
| `distutils.version.LooseVersion` | 已删除 | 重写一个能比版本号的类 |

补完才跑得起来。**这不是 mrjob 的错，是「库停更三年、解释器一路向前」的必然结果**
——你自己选技术栈时会天天遇到这件事：**一个库的最后提交时间，比它的星标数重要得多。**

### 坑 2：不加 `None` 判断，结果表里会凭空多出 `null` 行

原版 mapper 直接 `yield (period, url), 1`，取不到就 `None`。
我把它改成「取不到就 `return`」，然后**实测了不改的后果**：

```
[null, "/index.html"]	1        ← 时间戳坏的那行
[null, null]	1                 ← 整行没 URL 也没时间戳的那行
```

这两行会安静地躺在结果里。**它不报错、不告警，就是让「2016-01 的访问量」少算几条。**
数据类 bug 的典型形态：错得不明显，但每个月都少一点。

### 坑 3：`extract_url` 到底取哪个 URL，能得出完全不同且都「跑通」的结论

Apache 日志一行里有**三个** URL 可抓：请求行里的路径、`Referer` 头、UA 里的链接。
取不同的字段，同一个脚本都跑得通，但回答的是不同的问题：

| 取哪个 | 语义 | 本样本的丢弃率 |
|---|---|---|
| 请求行路径 `"GET /index.html HTTP/1.1"` | 这个**页面**被请求几次 | 9 行丢 2 行（22%） |
| `Referer` 头 | 这个**来源页**把人带过来几次 | 9 行丢 6 行（67%） |

试一下就知道差距有多大：

```powershell
..\..\..\.venv\Scripts\python.exe -X utf8 hit_counts_local.py sample.log --url-source referer
```

只剩 2 个 key、丢弃 67%——因为大部分访问没有 Referer（直接访问、命令行 curl）。
**「跑通了」和「统计对了」是两件事。** 写分析脚本前先问一句：我统计的到底是哪个量。

### 坑 4：`-r local` 在 Windows 上跑不了

```
Step 1 of 1 failed: [WinError 2] 系统找不到指定的文件。
```

local runner 要用 `sh -c`、`cat` 这些 POSIX 工具串管道，Windows 上没有。
**Windows 上只能 `-r inline`。** 真想跑 local/hadoop，进 WSL 或找台 Linux。

---

## 四、这个目录里有什么

| 文件 | 是什么 | 怎么用 |
|---|---|---|
| `hit_counts.py` | **mrjob 原版结构**，补上两个 `...`（另加了一处 `None` 判断，见坑 2） | `python hit_counts.py -r inline sample.log` |
| `hit_counts_local.py` | **纯标准库重写**：map → shuffle → reduce 三步手动展开，每步中间结果都打印 | `python hit_counts_local.py sample.log` |
| `compat_stubs/` | 坑 1 的三个补丁（`pipes`、`distutils.spawn`、`distutils.version`） | 被 `hit_counts.py` 自动加载，不用管 |
| `sample.log` | 9 行小样本，**刻意混了 2 行脏数据** | — |

`hit_counts_local.py` 是这份材料的重点。它把框架藏起来的那三步摊开给你看：

```
--- MAP 阶段的输出（7 条）---
  ('2016-01', '/index.html') , 1
  ('2016-01', '/pricing') , 1
  ...
--- SHUFFLE 之后（6 个 key，已按 key 排好序）---
  ('2016-01', '/index.html') -> [1, 1]
  ...
--- REDUCE 的结果（6 行）---
  ('2016-01', '/index.html') , 2
  ...
统计口径: 输入 9 行 -> 有效 7 条 -> 丢弃 2 行（占 22%）
```

**shuffle 那一步就是 MapReduce 的全部魔法**：按 key 排序、让相同的 key 挨在一起、
再切成一组一组喂给 reducer。所谓「分布式」不过是把这三步切到多台机器上跑，
排序换成了外排（数据大到内存放不下时先落盘再归并）。

---

## 五、三方交叉验算（防止「跑通了但算错了」）

同一个问题我用了三套互不相关的实现，结果必须一致：

```powershell
# ① mrjob（JSON 协议、框架调度）
python hit_counts.py -r inline sample.log

# ② 纯 Python 手写三段式
python hit_counts_local.py sample.log

# ③ 完全不碰上面两份代码：sed 抽字段 + awk 换月份 + sort | uniq -c
```

三份的输出都是 6 个 key，`('2016-01', '/index.html') = 2`，其余各 1。
**写统计脚本时可以借这个习惯**：用一条你信得过的 shell 管道核对 Python 的结果，
比盯着 Python 的输出来回看要可靠得多。
