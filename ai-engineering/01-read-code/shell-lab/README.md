# shell-lab：让一段真实脚本当场撒谎给你看

这里放的是 `donnemartin/system-design-primer`（37.5 万星标）的 `generate-epub.sh`，
原版 54 行，以及一个修复版和一套实验装置。

**目的不是学会写 shell，是学会一件事：怎么判断一段「能跑」的脚本到底可不可信。**

---

## 怎么跑

Windows 上用 Git Bash（VS Code 的默认终端就是），不需要装 pandoc：

```bash
cd ai-engineering/01-read-code/shell-lab

bash run_lab.sh          # 跑全部：两个失败场景 + 冒号实验
bash run_lab.sh colon    # 只看冒号那一行
```

输出里会直接看到：

```
── 原版 ──
Generating 'en' ...
Done! You can find the 'en' book at ./README.epub
...
      退出码：0   ← 它说"一切正常"
      产物：一个 .epub 都没有
```

---

## 文件说明

| 文件 | 是什么 |
|---|---|
| `generate-epub.sh` | **原版**，逐字照抄自 GitHub（1192 字节 / 54 行）。不要修它 |
| `generate-epub-fixed.sh` | 修复版，11 处改动都标了编号 |
| `run_lab.sh` | 实验装置：造最小仓库、造假 pandoc、跑两版对照、退出时清理 |
| `../walkthrough_generate_epub.md` | 逐段讲解 + 问题清单 + 实测数字 |

---

## 两个关键设计，值得知道

**① 用「假 pandoc」控制失败**

`run_lab.sh` 会往临时目录的 `bin/` 里写一个 `pandoc`，并把它塞在 `PATH` 最前面。
这个假的只做两件事：读走 stdin、按需要写产物或 `exit 1`。

这样就能**精确构造**「pandoc 挂了」和「pandoc 正常但源文件缺失」两种场景，
不用真的把磁盘写满。这是测外部依赖的标准手法，比 `mock` 更容易理解——它就是个 7 行的脚本。

**② 假 pandoc 会把 stdin 的字节数写进产物**

所以产物长这样：

```
FAKE-EPUB(81 bytes)
```

**字节数是证据**。81 = 35 + 22 + 22 + 2，分别对应 `README.md`、两个方案目录、两个空行。
如果拼装逻辑错了，这个数字立刻就变。

---

## 不会污染你的东西

- 所有文件都在 `mktemp -d` 造的临时目录里，退出时删除
- 不碰 `dev-basics/` 下任何真实数据
- 不装任何软件

（`run_lab.sh` 里 `cleanup` 会先 `cd /` 再 `rm`——因为 **`rm -rf` 删不掉自己当前所在的目录**，
Windows 上会报 `Device or resource busy`。这个小坑本身也写进了文档第五节。）
