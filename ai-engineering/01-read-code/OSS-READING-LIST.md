# 读别人的开源代码：去哪找、读哪个、从哪进

> 这份清单解决的是「想看别人写好的完整项目」这件事。
> 本文所有数字都是 2026-10-22 用 GitHub API 现查的，不是抄来的。
> 读单个函数的功夫见 `walkthrough_textwrap.md`；这份管「怎么挑、怎么进」。

---

## 一、先能找到：4 个入口

| 入口 | 直接点开 | 什么时候用 |
|---|---|---|
| 趋势榜 | <https://github.com/trending/python?since=weekly> | 不知道看什么，看本周冒头的 |
| 话题页 | <https://github.com/topics/cli> / <https://github.com/topics/pandas> | 想按领域找 |
| 搜索 | <https://github.com/search?q=language%3Apython+stars%3A%3E5000&type=repositories> | 有明确条件时最准 |
| Awesome 列表 | <https://github.com/vinta/awesome-python> | 想按「做哪类东西」找 |

搜索框里能直接写限定符，三条常用的：

```text
language:python stars:>5000 pushed:>2026-01-01        # 热门且还在维护
language:python stars:1000..5000 topic:cli            # 中等规模、做 CLI 的
language:python size:<2000 stars:>500                 # 代码量小的（size 单位 KB）
```

**`pushed:>` 是最有用的一个限定符。** 星标高但三年没动的仓库，代码风格和现在的 Python 差得远，读了反而学坏习惯。

---

## 二、读得动的 7 个（规模实测 + 可直接点开的网址）

按「入口文件大小」排序——**入口越小越好读**，因为它决定了你第一眼要看多少东西。

> ⚠️ **网址里的分支名不能想当然。** 2026-10-22 逐个核验：这 7 个里有 2 个的默认分支仍是
> `master`（`tqdm`、`tiangolo/typer`），其余是 `main`。把 `master` 写成 `main` 就是 404，
> 而且报错页面长得像「文件不存在」，很容易误以为是自己记错了路径。

### 第一梯队：一次坐下就能读完（建议从这里开始）

**① `python-dotenv` — 5.7 KB，191 行**

- 项目首页：<https://github.com/theskumar/python-dotenv>
- 入口文件：<https://github.com/theskumar/python-dotenv/blob/main/src/dotenv/parser.py>
- 测试怎么调：<https://github.com/theskumar/python-dotenv/blob/main/tests/test_parser.py>
- 学：手写一个小解析器、配置加载、CLI 三件套

**② `requests` — 7.0 KB，一个函数 3 行**

- 项目首页：<https://github.com/psf/requests>
- 入口文件：<https://github.com/psf/requests/blob/main/src/requests/api.py>
- 学：好用的 API 长什么样（`get`/`post`/`put` 七个动词，每个都只是一行 `return request(...)`）

### 第二梯队：需要分几次读

**③ `tqdm` — 56.7 KB**

- 项目首页：<https://github.com/tqdm/tqdm>
- 入口文件：<https://github.com/tqdm/tqdm/blob/master/tqdm/std.py> ← **`master`**
- 学：进度条怎么在迭代中偷偷刷新输出、怎么算速度

**④ `typer` — 67.5 KB**

- 项目首页：<https://github.com/tiangolo/typer>
- 入口文件：<https://github.com/tiangolo/typer/blob/master/typer/main.py> ← **`master`**
- 学：用类型注解 + 装饰器自动造 CLI

**⑤ `openai-python` — 95.6 KB**

- 项目首页：<https://github.com/openai/openai-python>
- 入口文件：<https://github.com/openai/openai-python/blob/main/src/openai/_client.py>
- 学：官方 SDK 怎么封装 HTTP、重试、流式响应

### 第三梯队：当参考书查，别通读

**⑥ `click` — 153.3 KB**

- 项目首页：<https://github.com/pallets/click>
- 入口文件：<https://github.com/pallets/click/blob/main/src/click/core.py>
- 学：命令行框架的核心抽象（`Context` / `Command`），是 Python CLI 界的教科书

**⑦ `bottle` — 171.2 KB，整个框架一个文件**

- 项目首页：<https://github.com/bottlepy/bottle>
- 入口文件：<https://github.com/bottlepy/bottle/blob/main/bottle.py>
- 学：一个 Web 框架的最小完整实现，约 4000 行。听着吓人，但**不用在几十个目录间跳**，
  是「一个项目从零长起来」的最佳样本。当参考书，按需搜索关键字。

补充两个事实，避免你被教程带偏：

- `requests` 已经迁到 `src/requests/` 目录，网上大量教程写的 `requests/api.py` 是**旧路径，会 404**。
  `sessions.py` 33 KB、`models.py` 40 KB，别从这两个开始。
- 「把 `github.com/…/blob/…` 里的 `github.com` 换成 `github.dev`」= 网页版 VS Code，
  可以全局搜索、看定义跳转，**读代码时比网页阅读器强太多**。
  例：<https://github.dev/theskumar/python-dotenv>

---

## 三、三条铁律：从哪个文件读起

**① 先 `tests/` 再 `src/`**

测试是「这段代码该怎么用」的活文档，而且一段一个断言，不用理解全貌就能读。
`python-dotenv` 的 `tests/` 里有 `test_parser.py`，看完你就知道 `parser.py` 的每个函数吃进什么吐什么。

**② 先小文件，后大文件**

同一个目录下，5 KB 的文件通常是「定义和常量」，40 KB 的才是「主逻辑」。
先读小的建立词汇表（`Order` 是什么、`RowParseError` 是什么），再读大的才不会卡。

**③ 先找入口函数，别从第一行读**

入口的标志：`if __name__ == "__main__"`、`def main(`、`cli.py`、`__main__.py`。
从入口往下跟一次完整调用，比顺着文件从头读到尾效率高一个量级。
这正是 `walkthrough_textwrap.md` 里做的事：先问「这个函数在整条链路里负责哪一段」。

---

## 四、一个 40 分钟的完整走法（以 python-dotenv 为例，含网址）

```text
0-5 分    https://github.com/theskumar/python-dotenv
          只看 README 前 20 行：它解决什么问题

5-10 分   https://github.dev/theskumar/python-dotenv
          按 Ctrl+P 搜 test_parser.py，先看测试里怎么调用

10-25 分  同窗口继续读 src/dotenv/parser.py（5.7 KB，一次能读完）

25-35 分  读 src/dotenv/main.py 的前 100 行，找「谁调用了 parser」

35-40 分  回 https://github.com/theskumar/python-dotenv/blob/main/src/dotenv/parser.py
          点右上「Blame / 追溯」，看这文件最近为什么被改
```

**第一步就能偷懒的方式**：把第二节表格里任意一个网址的 `github.com` 换成 `github.dev`，
直接进网页版 VS Code，不用一层层点目录。

第四步的「追溯」经常被忽略，但它是理解**设计意图**最快的入口——
代码告诉你「现在是什么样」，提交历史告诉你「为什么要变成这样」。

---

## 五、什么样的项目别通读

| 特征 | 例子 | 怎么办 |
|---|---|---|
| 仓库 > 5 MB 源码 | `Textualize/rich`（50 MB） | 只读你用到的那一个模块 |
| 大量生成代码 | protobuf / 客户端 SDK 的 `types/` | 跳过，那是自动生成的 |
| 只有 notebook | 教学仓库 | 当文章读，别当工程学 |
| 三年没提交 | — | 换一个，学了也是过时的写法 |

**判断标准就一条：你能不能在一次坐下里读完它的入口。** 读不完就说明该换小的，不是你的问题。
