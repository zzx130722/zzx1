"""把兄弟目录加进 sys.path，让测试能 import 到被测试的代码。

真实项目里通常用 `pip install -e .` 把包装进环境，那样就不需要这一段。
这个练习不打包，所以用最直白的办法。
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for sibling in ("02-refactor", "03-debug-drill"):
    path = str(HERE.parent / sibling)
    if path not in sys.path:
        sys.path.insert(0, path)
