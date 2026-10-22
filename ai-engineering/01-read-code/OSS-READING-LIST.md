# 读别人的开源代码：去哪找、读哪个、从哪进

> 这份清单解决的是「想看别人写好的完整项目」这件事。
> 本文所有数字都是 2026-10-22 用 GitHub API 现查的，不是抄来的。
> 读单个函数的功夫见 `walkthrough_textwrap.md`；这份管「怎么挑、怎么进」。

---

## 一、先能找到：4 个入口

| 入口 | 地址 | 什么时候用 |
|---|---|---|
| 趋势榜 | `github.com/trending/python?since=weekly` | 不知道看什么，看本周冒头的 |
| 话题页 | `github.com/topics/cli`、`/topics/pandas` | 想按领域找 |
| 搜索 | 见下面三条 | 有明确条件时最准 |
| Awesome 列表 | `github.com/vinta/awesome-python` | 想按「做哪类东西」找 |

搜索框里能直接写限定符，三条常用的：

```text
language:python stars:>5000 pushed:>2026-01-01        # 热门且还在维护
language:python stars:1000..5000 topic:cli            # 中等规模、做 CLI 的
language:python size:<2000 stars:>500                 # 代码量小的（size 单位 KB）
```

**`pushed:>` 是最有用的一个限定符。** 星标高但三年没动的仓库，代码风格和现在的 Python 差得远，读了反而学坏习惯。

---

## 二、读得动的 7 个（规模实测）

按「入口文件大小」排序——**入口越小越好读**，因为它决定了你第一眼要看多少东西。

| 项目 | 星标 | 入口文件 | 读它能学到什么 |
|---|---|---|---|
| `theskumar/python-dotenv` | 8.9k | `src/dotenv/parser.py` **5.7 KB** | 手写一个小解析器、配置加载、CLI 三件套 |
| `psf/requests` | 54.5k | `src/requests/api.py` **7.0 KB** | 好用的 API 长什么样（7 个动词函数一行一个） |
| `tqdm/tqdm` | 31.4k | `tqdm/std.py` **56.7 KB** | 进度条：怎么在迭代中偷偷刷新输出 |
| `tiangolo/typer` | 20.2k | `typer/main.py` **67.5 KB** | 用类型注解 + 装饰器自动造 CLI |
| `openai/openai-python` | 31.9k | `src/openai/_client.py` **95.6 KB** | 官方 SDK 怎么封装 HTTP、重试、流式响应 |
| `pallets/click` | 17.8k | `src/click/core.py` **153.3 KB** | 命令行框架的核心抽象（Context/Command） |
| `bottlepy/bottle` | 8.8k | `bottle.py` **171.2 KB**（单文件） | 一个 Web 框架的最小完整实现 |

补充两个事实，避免你被教程带偏：

- `requests` 已经迁到 `src/requests/` 目录，网上大量教程写的 `requests/api.py` 是**旧路径，会 404**。
  `sessions.py` 33 KB、`models.py` 40 KB，别从这两个开始。
- `bottle` 整个框架是**一个文件**，171 KB 约 4000 行。听起来吓人，但它是「一个项目从零长起来」的最佳样本——
  不用在几十个目录间跳。

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

## 四、一个 40 分钟的完整走法（以 python-dotenv 为例）

```text
0-5 分    打开 github.com/theskumar/python-dotenv，只看 README 前 20 行：它解决什么问题
5-10 分   按 t，输入 test_parser，先看测试里怎么调用
10-25 分  按 .，打开网页版 VS Code，读 src/dotenv/parser.py（5.7 KB，一次能读完）
25-35 分  读 src/dotenv/main.py 的前 100 行，找「谁调用了 parser」
35-40 分  回到 GitHub，点文件里的「追溯」，看 parser.py 最近被改过什么、为什么改
```

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
