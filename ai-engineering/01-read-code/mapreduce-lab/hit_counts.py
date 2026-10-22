#!/usr/bin/env python
"""原版 HitCounts —— 补上两个 `...`，外加一处 None 判断（理由见 README 坑 2）。

跑法（mrjob 0.7.4，已装进 .venv）:
    python hit_counts.py -r inline sample.log

`-r inline` 是 mrjob 的「单进程模拟器」：不开 Hadoop、不启子进程，
map 完直接 shuffle 再 reduce，适合纯粹想看懂逻辑的时候。
输出是「key + 一个制表符 + value」，形如:

    ["2016-01", "/index.html"]	2

注意 key 打印成了 JSON 数组 —— Python 里的元组 (period, url) 被 mrjob 序列化成了
["2016-01", "/index.html"]。这是 mrjob 默认用 JSON 协议的缘故；
换成裸 Hadoop Streaming 就没这好事了，key 必须是字符串，得自己拼 "2016-01\t/index.html"。

想看它在「像个真分布式的样子」下怎么跑（会 fork 子进程）:
    python hit_counts.py -r local sample.log

⚠️ 但上面这条在 Windows 上跑不通，实测报:
    Step 1 of 1 failed: [WinError 2] 系统找不到指定的文件。
原因：local runner 用 `sh -c`、`cat` 这类 POSIX 工具串管道，Windows 上没有。
**所以在 Windows 上只能 `-r inline`。** 想真跑 local/hadoop，得进 WSL 或 Linux 机器。
"""

import re
import sys
from pathlib import Path

# 把 compat_stubs/ 插到 sys.path 最前面。
# 原因：mrjob 0.7.4（2021 年的最后一版）还在 import pipes / distutils，
# 而这两个标准库在 Python 3.12 / 3.13 里已经被删干净了。
# 不插这三行，`from mrjob.job import MRJob` 会直接 ModuleNotFoundError。
sys.path.insert(0, str(Path(__file__).parent / "compat_stubs"))

from mrjob.job import MRJob  # noqa: E402  （必须放在改 sys.path 之后）

_REQUEST_RE = re.compile(
    r'"(?:GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH)\s+(\S+)\s+HTTP/[\d.]+"'
)
_TS_RE = re.compile(r"\[(\d{2})/([A-Za-z]{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})")
_MONTHS = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}


class HitCounts(MRJob):
    def extract_url(self, line):
        """Extract the generated url from the log line."""
        m = _REQUEST_RE.search(line)
        return m.group(1) if m else None

    def extract_year_month(self, line):
        """Return the year and month portions of the timestamp."""
        m = _TS_RE.search(line)
        if not m:
            return None
        mm = _MONTHS.get(m.group(2).capitalize())
        return f"{m.group(3)}-{mm}" if mm else None

    def mapper(self, _, line):
        """Parse each log line, extract and transform relevant lines.

        Emit key value pairs of the form:

        (2016-01, url0), 1
        (2016-01, url0), 1
        (2016-01, url1), 1
        """
        url = self.extract_url(line)
        period = self.extract_year_month(line)
        # 原版没有这两行。没有它们，取到 None 时 key 会变成 (None, '/x')，
        # 脏数据会以「一个叫 None 的月份」的形式悄悄进结果表。
        if url is None or period is None:
            return
        yield (period, url), 1

    def reducer(self, key, values):
        """Sum values for each key.

        (2016-01, url0), 2
        (2016-01, url1), 1
        """
        yield key, sum(values)


if __name__ == "__main__":
    HitCounts.run()
