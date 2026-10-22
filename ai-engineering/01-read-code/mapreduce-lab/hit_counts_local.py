#!/usr/bin/env python
"""MapReduce 三段式，纯标准库实现 —— 不用装 mrjob / Hadoop 也能跑。

对照的原始代码（tutorial 里那段 HitCounts）:

    class HitCounts(MRJob):
        def extract_url(self, line): ...
        def extract_year_month(self, line): ...
        def mapper(self, _, line):
            url = self.extract_url(line)
            period = self.extract_year_month(line)
            yield (period, url), 1
        def reducer(self, key, values):
            yield key, sum(values)

那段代码有两个 `...`，缺了就是跑不了。这里把那两个 `...` 补上，
再把 mrjob 藏在框架里的 map -> shuffle -> reduce 三步手动展开，让每一步的中间结果都看得见。

用法:
    python hit_counts_local.py sample.log                # 统计「请求路径」被访问次数
    python hit_counts_local.py sample.log --url-source referer   # 统计「来源页」被带去流量
"""

from __future__ import annotations

import re
import sys
from itertools import groupby
from pathlib import Path

# ---- ① 把 extract_url / extract_year_month 这两个 `...` 补上 -------------------

# Apache/Nginx 的 access log 里，请求行长这样:  "GET /index.html HTTP/1.1"
# 抓第二个字段。不带这个正则的写法（比如 line.split()）会被 UA 里的空格搞乱。
_REQUEST_RE = re.compile(
    r'"(?:GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH)\s+(\S+)\s+HTTP/[\d.]+"'
)

# 最后一个引号字段是 UA，它前面那个是 Referer。
# 用「从行尾往前数」的写法，是因为 Referer 里可能含空格、含引号转义。
_REFERER_RE = re.compile(r'"([^"]*)"\s*"[^"]*"\s*$')

# 时间戳: [03/Jan/2016:10:12:01 +0000]
_TS_RE = re.compile(
    r"\[(\d{2})/([A-Za-z]{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})"
)

# 刻意不用 datetime.strptime(t, "%d/%b/%Y:%H:%M:%S %z"):
# %b 依赖进程的 locale，在中文 Windows 上解析 "Jan" 可能直接抛 ValueError。
# 这种「在我机器上跑得通」的写法，换台机器就挂 —— 手写映射表是稳的。
_MONTHS = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}


def extract_url(line: str, source: str = "request") -> str | None:
    """从一行日志里取出 URL。取不到就返回 None（不抛异常，交给调用方跳过）。"""
    if source == "referer":
        m = _REFERER_RE.search(line)
        if not m:
            return None
        url = m.group(1).strip()
        # 日志里没有 Referer 时会写 "-"，这不算一个 URL
        return None if url in ("", "-") else url

    m = _REQUEST_RE.search(line)
    return m.group(1) if m else None


def extract_year_month(line: str) -> str | None:
    """返回 '2016-01' 这样的年月；解析不了返回 None。"""
    m = _TS_RE.search(line)
    if not m:
        return None
    _, mon, year = m.group(1), m.group(2), m.group(3)
    mm = _MONTHS.get(mon.capitalize())
    return f"{year}-{mm}" if mm else None


# ---- ② mapper: 一行输入 -> 若干 (key, 1) ------------------------------------


def mapper(line: str, source: str = "request"):
    """对应原代码的 mapper(self, _, line)。

    第一个参数在原代码里是 `_`，因为 mrjob 传的是「字节偏移量」，
    这个例子用不上，所以用下划线表示「我知道有这个参数，但我不用」。
    """
    url = extract_url(line, source)
    period = extract_year_month(line)
    # 两个有一个取不到，这行就丢掉 —— 注意：是「静默丢掉」，见 README 的坑 3
    if url is None or period is None:
        return
    yield (period, url), 1


# ---- ③ shuffle: 按 key 分组（Hadoop 里这一步由框架做，还会顺手排序）---------


def shuffle(pairs):
    """把 mapper 的输出排序 -> 相同的 key 相邻 -> 分组。"""
    return [
        (key, [v for _, v in group])
        for key, group in groupby(sorted(pairs, key=lambda p: p[0]), key=lambda p: p[0])
    ]


# ---- ④ reducer: (key, [1,1,1]) -> (key, 3) ----------------------------------


def reducer(key, values):
    """对应原代码的 reducer(self, key, values)。

    values 是一个「可迭代对象」而不是列表 —— Hadoop 是边读边喂的，
    如果数据量是 10 亿条，框架不可能先在内存里攒成一个 list 再交给你。
    所以 reducer 里只能用一次 values（想用两次得先 list(values)）。
    """
    yield key, sum(values)


# ---- ⑤ 把三步串起来，并且把每一步的中间结果打印出来 --------------------------


def run(path: Path, source: str = "request") -> list[tuple[tuple[str, str], int]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = [ln for ln in lines if ln.strip()]

    print(f"输入: {path.name}  共 {len(lines)} 行   url 来源 = {source}\n")

    # --- MAP ---
    mapped = []
    for ln in lines:
        mapped.extend(mapper(ln, source))
    print(f"--- MAP 阶段的输出（{len(mapped)} 条）---")
    for k, v in mapped:
        print(f"  {k} , {v}")

    # --- SHUFFLE ---
    groups = shuffle(mapped)
    print(f"\n--- SHUFFLE 之后（{len(groups)} 个 key，已按 key 排好序）---")
    for k, vals in groups:
        print(f"  {k} -> {vals}")

    # --- REDUCE ---
    result = []
    for k, vals in groups:
        result.extend(reducer(k, vals))
    print(f"\n--- REDUCE 的结果（{len(result)} 行）---")
    for k, total in result:
        print(f"  {k} , {total}")

    dropped = len(lines) - len(mapped)
    print(
        f"\n统计口径: 输入 {len(lines)} 行 -> 有效 {len(mapped)} 条 -> "
        f"丢弃 {dropped} 行（占 {dropped / len(lines):.0%}）"
    )
    return result


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"找不到文件: {path}", file=sys.stderr)
        return 2
    source = "request"
    if "--url-source" in argv:
        source = argv[argv.index("--url-source") + 1]
        if source not in ("request", "referer"):
            print("--url-source 只能是 request 或 referer", file=sys.stderr)
            return 2
    run(path, source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
