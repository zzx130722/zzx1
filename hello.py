"""开发环境自检脚本：跑通它，说明环境搭好了。

用法：
    python hello.py
"""

import platform
import sys


def main() -> None:
    in_venv = sys.prefix != sys.base_prefix

    print("环境自检")
    print("-" * 34)
    print(f"Python 版本  : {sys.version.split()[0]}")
    print(f"解释器路径   : {sys.executable}")
    print(f"是否在虚拟环境: {'是' if in_venv else '否  <-- 需要激活 .venv'}")
    print(f"操作系统     : {platform.system()} {platform.release()}")

    try:
        import pandas as pd

        print(f"pandas 版本  : {pd.__version__}")
    except ImportError:
        print("pandas 版本  : 未安装，请运行 pip install -r requirements.txt")

    print("-" * 34)
    if in_venv:
        print("结论：环境正常，可以开始写代码了。")
    else:
        print("结论：当前用的是全局 Python，请先激活虚拟环境。")


if __name__ == "__main__":
    main()
