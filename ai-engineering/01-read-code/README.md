# 01 · 读开源代码 + AI review

两条子任务共用一套方法：**先让 AI 复述，再让它举证**。

| 文件 | 是什么 | 怎么用 |
|---|---|---|
| `walkthrough_textwrap.md` | 对 `textwrap._wrap_chunks`（102 行）的完整走查，切成 7 段 | 先自己看源码，卡住时看对应段 |
| `experiments.py` | 7 个实验，每个都是「问 → 猜 → 验」 | **先猜再跑**，跑完回到走查对答案 |
| `review-drill.md` | review 的提问模板 + 7 条常见意见的裁决 | 读第 2 节的裁决表，重点看"怎么自己验" |

## 跑起来

```powershell
cd $HOME\WorkBuddy\2026-10-13-16-35-32\dev-basics
.venv\Scripts\python.exe -X utf8 ai-engineering\01-read-code\experiments.py
```

`-X utf8` 不能省：Windows 控制台默认按 GBK 解码，中文输出会变成乱码（不是代码错了）。

## 为什么拿标准库开刀

- 它**一定在你机器上**，不用 clone、不用装依赖，`inspect.getsource` 就能看到当前版本的真实实现
- 它是**被几百万人用过**的代码，敢写得这么绕一定有其原因 —— 正好练"先假设作者是对的，再找出他为什么对"
- 它有真实的瑕疵（拼错的注释、不合规的变量名），适合练"该不该改"的判断，而不是只能挑出语法错

## 读完的标准

不是"看懂了"，而是能回答：

1. `chunks.reverse()` 那行的注释说为了 `pop()` 高效 —— 换成 `pop(0)` 会慢多少？（数量级，不用精确值）
2. 303 行的 `cur_len = sum(map(len, cur_line))` 能不能删？（先答"能/不能"，再给理由）
3. 291 行 `<=` 改成 `<`，哪个用例会挂？

三个都答得上来，再去 `review-drill.md` 第 2 节对答案。答不上来就先跑 `experiments.py` 的实验 2、4、5。

## 作业（不写进代码，写给自己的笔记）

读 `csv.DictReader`（`csv.py`，60 行左右），回答 `walkthrough_textwrap.md` 末尾那三个问题。
读完把答案贴给 AI，让它**只做一件事：指出你答错的**。
