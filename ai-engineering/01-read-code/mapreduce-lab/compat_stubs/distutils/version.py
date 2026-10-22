"""distutils.version.LooseVersion 的替身（只实现比较，够 mrjob 用）。

真正的 LooseVersion 在 Python 3.12 被删掉了（PEP 632）。
mrjob 只拿它来比较版本号字符串，比如 "5.2.1" < "6.0.0"。

实现方式：把 "3.13.3" 切成 [3, 13, 3]，逐段比；
段数不同时短的算小（"3.13" < "3.13.1"）。
"""

import re
from functools import total_ordering


@total_ordering
class LooseVersion:
    def __init__(self, vstring=None):
        self.vstring = vstring
        self.version = self._parse(vstring) if vstring is not None else []

    @staticmethod
    def _parse(vstring):
        parts = []
        for comp in re.split(r"[._\-]", str(vstring)):
            if not comp:
                continue
            parts.append(int(comp) if comp.isdigit() else comp)
        return parts

    def _cmp(self, other):
        if not isinstance(other, LooseVersion):
            other = LooseVersion(other)
        a, b = self.version, other.version
        for x, y in zip(a, b):
            if x == y:
                continue
            if isinstance(x, int) and isinstance(y, int):
                return -1 if x < y else 1
            # 类型不同（比如 1 和 "rc1"）就退化成字符串比较，保证不比到崩溃
            sx, sy = str(x), str(y)
            return -1 if sx < sy else 1
        return (len(a) > len(b)) - (len(a) < len(b))

    def __eq__(self, other):
        try:
            return self._cmp(other) == 0
        except Exception:
            return NotImplemented

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __hash__(self):
        return hash(tuple(self.version))

    def __str__(self):
        return self.vstring if self.vstring is not None else ""

    def __repr__(self):
        return f"LooseVersion ('{self}')"
