# 走查：一个 37 万星标项目的构建脚本

> 对象：`donnemartin/system-design-primer` 的 `generate-epub.sh`
>
> - 仓库 <https://github.com/donnemartin/system-design-primer>（37.5 万星标、5.9 万 fork）
> - 文件 <https://github.com/donnemartin/system-design-primer/blob/master/generate-epub.sh>
> - 2026-10-22 抓取：**1192 字节 / 54 行**，与 `shell-lab/generate-epub.sh` 逐字一致
> - ⚠️ 默认分支是 **`master`** 不是 `main`；文件名是 **`generate-epub.sh`** 不是 `epub-generator.sh`
>
> 本文出现的每个数字都是在 `shell-lab/` 里真跑出来的，不是读代码猜的。
> 想自己看一遍：`bash shell-lab/run_lab.sh`（不需要装 pandoc，脚本自带一个「假 pandoc」）

---

## 一、它到底在干什么（30 秒看完）

```
generate-epub.sh
│
├─ check_dependencies        检查 pandoc 装没装
│
├─ generate_with_solutions   把整本书拼成一个临时文件，再转成 README.epub
│    ├─ cat README.md                              ← 正文开头
│    ├─ for 每个 solutions/system_design/* 目录
│    │     └─ cat <那个目录>/README.md             ← 逐个方案追加
│    └─ generate_from_stdin
│
└─ generate × 3              三个语种各转一次（ja / zh-Hans / zh-TW）
     └─ cat README-<lang>.md | generate_from_stdin
```

核心只有一句：

```bash
pandoc --metadata-file=epub-metadata.yaml --metadata=lang:$2 --from=markdown -o $1 <&0
```

`pandoc` 从标准输入读 markdown，写成 epub。上面所有函数都是在「把内容喂进 stdin」和「把文件名传进去」。

**这个设计的思路是对的**：拼文件 → 一次转换，比每个章节单独转再合并简单得多。

---

## 二、逐段看，5 个地方值得停一下

### 段 ①　第 3–12 行：`generate_from_stdin`

```bash
generate_from_stdin() {
  outfile=$1
  language=$2
  echo "Generating '$language' ..."
  pandoc --metadata-file=epub-metadata.yaml --metadata=lang:$2 --from=markdown -o $1 <&0
  echo "Done! You can find the '$language' book at ./$outfile"
}
```

三个细节：

1. **`$1` 和 `$outfile` 混着用**——同一个东西，第 9 行写 `$1`、第 11 行写 `$outfile`。读的人要在脑子里做一次映射。
2. **`<&0` 是纯噪音**。没有传 `-i`，pandoc 本来就读标准输入，`<&0` 等于说「把标准输入接到标准输入」。
3. **`echo "Done!"` 不管 pandoc 成不成功都会执行** ——这是整个脚本最严重的问题，见下一节。

### 段 ②　第 14–28 行：`generate_with_solutions`

```bash
tmpfile=$(mktemp /tmp/sytem-design-primer-epub-generator.XXX)
cat ./README.md >> $tmpfile
for dir in ./solutions/system_design/*; do
  case $dir in *template*) continue;; esac
  case $dir in *__init__.py*) continue;; esac
  : [[ -d "$dir" ]] && ( cd "$dir" && cat ./README.md >> $tmpfile && echo "" >> $tmpfile )
done
cat $tmpfile | generate_from_stdin 'README.epub' 'en'
rm "$tmpfile"
```

- `sytem` 少了个 `s`——不影响运行，但说明这行没人认真看过。
- 第 22 行开头那个 **`:`** 是个货真价实的 bug，见下一节。
- `cat $tmpfile | generate_from_stdin ...` 多起了一个进程，等价于 `generate_from_stdin ... < $tmpfile`。
- `rm "$tmpfile"` 放在最后一行——中间任何一步提前退出，这个文件就永远留在 `/tmp` 里了。

### 段 ③　第 30–35 行：`generate`

```bash
generate () {
  name=$1
  language=$2
  cat $name.md | generate_from_stdin $name.epub $language
}
```

看起来无害的一行，但它隐含一个假设：**`$name.md` 一定存在**。如果不存在，`cat` 报错到 stderr，管道里的 pandoc 收到 **0 字节**，然后……老老实实生成一本空书，并报 `Done!`。

### 段 ④　第 38–50 行：依赖检查

```bash
check_dependencies () {
  for dependency in "${dependencies[@]}"
  do
    if ! [ -x "$(command -v $dependency)" ]; then
      echo "Error: $dependency is not installed." >&2
      exit 1
    fi
  done
}
dependencies=("pandoc")
check_dependencies
```

函数在第 38 行定义，`dependencies` 在第 48 行才赋值——**因为函数体是调用时才解析变量，所以能用**。这是「靠调用顺序成立」的写法，脆弱但不致命。

`-x "$(command -v ...)"`：`command -v` 本身已经回答了「能不能执行」，再套一层 `-x` 多余了，而且对 shell 内建命令会误判。

### 段 ⑤　第 51–54 行：主流程

```bash
check_dependencies
generate_with_solutions
generate README-ja ja
generate README-zh-Hans zh-Hans
generate README-zh-TW zh-TW
```

没有 `set -e`，没有 `set -u`，没有 `set -o pipefail`。**上面每一步失败，脚本都会继续往下跑，最后返回 0。**

---

## 三、问题清单（全部实测，按严重度排）

`bash shell-lab/run_lab.sh` 会把这些全部复现出来。

### 🔴 1. pandoc 失败，脚本仍报成功

**实测**（场景 A，假 pandoc 每次 `exit 1`）：

```
── 原版 ──
Generating 'en' ...
Done! You can find the 'en' book at ./README.epub
Generating 'ja' ...
Done! You can find the 'ja' book at ./README-ja.epub
Generating 'zh-Hans' ...
Done! ...
Generating 'zh-TW' ...
Done! ...
      退出码：0   ← 它说"一切正常"
      产物：一个 .epub 都没有
```

**四个 `Done!`、退出码 0、一本都没生成。**

原因：`echo "Done!"` 是 `pandoc` 之后的独立命令；没开 `set -e`，pandoc 的 `exit 1` 被忽略；脚本最后一个命令是 `generate README-zh-TW`，它内部的 `echo` 又返回 0，所以整个脚本的退出码也是 0。

**后果**：CI 里这一步永远是绿的。发布出去的四本电子书全是旧的——因为新的一本都没生成。

### 🔴 2. 源文件缺失 → 生成 0 字节空书，仍报成功

**实测**（场景 B，假 pandoc 正常，但仓库里没有 `README-ja.md`）：

```
── 原版 ──
      退出码：0
      产物：README-ja.epub       FAKE-EPUB(0 bytes)
      产物：README-zh-Hans.epub  FAKE-EPUB(0 bytes)
      产物：README-zh-TW.epub    FAKE-EPUB(0 bytes)
      产物：README.epub          FAKE-EPUB(81 bytes)
```

**3 本 0 字节的书，全部标着 Done!**

这条比第 1 条更阴险：`cat` 确实往 stderr 喊了 `No such file or directory`，但**产物存在、退出码 0**，所以任何检查「文件是否生成」的监控都拦不住它。

### 🟠 3. 冒号把目录判断吞掉了

原版第 22 行：

```bash
: [[ -d "$dir" ]] && ( cd "$dir" && cat ./README.md >> $tmpfile && echo "" >> $tmpfile )
```

`:` 是 shell 内建命令，含义是「什么都不做，返回成功」。所以 `[[ -d "$dir" ]]` **不是条件，而是 `:` 的参数**——被完整忽略。`&&` 判断的是 `:` 的退出码，永远是 0。

**实测**（`bash shell-lab/run_lab.sh colon`）：

```
  目标 ./nonexistent
      原版（带冒号）：判定为目录，执行 cd      ← 不存在也进
      正确（无冒号）：跳过
  目标 ./notadir.txt
      原版（带冒号）：判定为目录，执行 cd      ← 普通文件也进
      正确（无冒号）：跳过
  目标 ./realdir
      原版（带冒号）：判定为目录，执行 cd
      正确（无冒号）：判定为目录，执行 cd
```

**在真实仓库里为什么没炸**：`solutions/system_design/` 下恰好只有子目录，唯一的普通文件 `__init__.py` 被上一行的 `case` 排掉了。

只要有人往里放一个 `notes.md` 或 `.DS_Store`（Windows/macOS 上很常见），每次构建就会多一条：

```
generate-epub.sh: line 22: cd: ./solutions/system_design/notes.md: Not a directory
```

而因为错误被 `&&` 挡住、循环继续，**你不会注意到**。

### 🟡 4. 临时文件不能保证清理

`tmpfile` 在第 15 行建，第 27 行删。中间任何一步 `exit`（包括 Ctrl+C）都会留下文件。正确做法是 `trap`。

### 🟡 5. 无用管道 + 无用重定向

```bash
cat $tmpfile | generate_from_stdin 'README.epub' 'en'    # 多一个 cat 进程
pandoc ... <&0                                          # 把 stdin 接到 stdin
```

两处都在做「等价于什么都不做」的事，但会让读的人以为这里有什么讲究。

### 🔵 6. 变量不加引号

`$tmpfile`、`$name`、`$1` 全部裸奔。当前路径里没有空格所以没事，但 `cd "我的 项目"` 这种目录一出现就会裂成两个参数。

### 🔵 7. shebang 里多了个空格

```
#! /usr/bin/env bash
```

Linux 内核会跳过 `#!` 后的空白，所以能用；POSIX 未定义这个行为，部分 Unix 上会失败。标准写法是 `#!/usr/bin/env bash`（现在很多脚本又改成 `#!/usr/bin/env -S bash`）。

---

## 四、修复版做了 11 处改动

完整代码见 `shell-lab/generate-epub-fixed.sh`，每处都有编号注释。核心只有四条：

```bash
set -euo pipefail          # ① 失败就停，管道任一环失败也算失败
trap cleanup EXIT          # ② 无论怎么退出都清理
[[ -d "$dir" ]] || continue # ⑧ 去掉冒号
[[ -f "$name.md" ]] || exit 1  # ⑪ 源头拦住，别让空输入流进 pandoc
```

**同样的两个场景，修复版的表现：**

| 场景 | 原版 | 修复版 |
|---|---|---|
| A：pandoc 每次都失败 | 4 次 `Done!`、退出码 **0**、0 个 epub | 第 1 次就停、退出码 **1** |
| B：缺 `README-ja.md` | 4 个 epub（3 个 0 字节）、退出码 **0** | 1 个 epub（81 字节）、报 `Error`、退出码 **1** |

场景 B 里那个 `81 bytes` 可以验算：`README.md` 35 + `design_a/README.md` 22 + `design_b/README.md` 22 + 两个空行 2 = **81**。模板目录和 `noise.txt` 都被正确排除了——**成功路径的输出和原版一字不差**，改的只是出错时说不说话。

---

## 五、我自己修的时候也踩了坑（这一节比上面都重要）

第一版修复版我写了：

```bash
generate_with_solutions() {
  local tmpfile
  tmpfile=$(mktemp ...)
  trap 'rm -f "$tmpfile"' EXIT
  ...
}
```

跑出来：

```
generate-epub-fixed.sh: line 1: tmpfile: unbound variable
```

而且临时文件**一个都没删掉**。

原因：`trap ... EXIT` 在**脚本**退出时执行，但那时 `generate_with_solutions` 早就返回了，`local tmpfile` 已经销毁。开了 `set -u`，展开一个不存在的变量直接报错，`rm` 根本没跑。

改成全局变量 + `"${tmpfile:-}"` 兜底才对：

```bash
worktmp=""
trap 'rm -f "${worktmp:-}"' EXIT
```

**这件事的教训不是「`local` 不好」**，而是：

> 我按「标准做法」写了 `local` 和 `trap`，两件事各自都对，**组合起来错了**。
> 而这种错误不会在阅读时暴露，只有真跑才会。

同一个道理，这一路上还踩了两个：`rm -rf` 删不掉「自己当前所在的目录」（Windows 报 `Device or resource busy`），所以 `cleanup` 里得先 `cd /`；以及这个环境里 `mktemp` 会返回 `C:\...` 风格的路径，被 `rm` 的安全包装拒绝，得强制用 `/tmp`。

---

## 六、从这个脚本能带走的三条规律

**① 「跑通了」和「跑对了」是两件事**

这个脚本在真实仓库里是能用的，作者也一直在用。但它的「成功」靠的是环境配合：文件都在、pandoc 装对了、目录里没有杂文件。**环境一变，它不会报错，它会撒谎。**

判断一个脚本可不可信，最快的办法是问：**「如果这一步失败了，我会知道吗？」** 如果答案是「不会」，那它现在能跑只是运气。

**② 错误没人接住，就会变成数据**

第 2 条问题是典型的「静默失败」：`cat` 报错了，但错误只写到 stderr；管道把 0 字节交给 pandoc；pandoc 尽职地生成了一本空书；`echo` 尽职地报成功。

**每一环都「没做错」，串起来就是错的。** 这也是为什么 `set -o pipefail` 重要——默认情况下管道的退出码只看最后一个命令。

**③ 37 万星标不代表每行都值得学**

这个仓库的价值是那几十篇 markdown 文档，`generate-epub.sh` 只是打包用的辅助工具，没有测试、没人 review。

**读开源代码要先分清「这个项目的核心资产是什么」**：核心资产处的代码往往非常讲究，周边工具常常是「能用就行」。`python-dotenv` 的 `parser.py` 值得逐行读，这个构建脚本值得读的是**它出错的方式**。

---

## 七、自测（不看上面，先自己答）

1. 原版跑完，`$?` 是多少？为什么是这个值？
2. `: [[ -d "$dir" ]] && ...` 里，`[[ ]]` 实际被当成了什么？
3. 为什么「缺 README-ja.md」比「pandoc 挂了」更难发现？
4. 修复版里 `worktmp` 为什么不能是 `local`？
5. 场景 B 修复版产物是 81 字节，这 81 字节由哪几部分组成？

答案都在上面四节里。**能不看文档答出第 2、4 题，说明你抓住了 shell 里最容易错的两个机制**：内建命令的参数语义、trap 的执行时机。
