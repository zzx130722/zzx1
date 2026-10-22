"""临时补丁：让 mrjob 0.7.4 能在 Python 3.13 上 import 通过。

背景（真跑出来的问题）:
    mrjob 最新版就是 0.7.4，发布于 2021 年，源码里有 `import pipes`。
    而标准库 `pipes` 在 Python 3.11 被标为废弃、**3.13 直接删除**。
    于是 `from mrjob.job import MRJob` 立刻抛 ModuleNotFoundError。

mrjob 全仓库只用到 `pipes.quote` 这一个函数，它等于 `shlex.quote`，
所以补一个同名模块放在脚本目录即可（脚本目录在 sys.path 首位，会优先于标准库）。

⚠️ 这是实验用的权宜之计，不是正经解法。正经做法二选一：
    ① 给项目单独建 Python 3.11/3.12 的 venv
    ② 换用仍在维护的同类库（如 dask / pyspark 的本地模式）
"""

from shlex import quote

__all__ = ["quote"]
