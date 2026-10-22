"""用标准库 trace 测量 02-refactor/refactored 包的行覆盖率。

为什么不用 pytest-cov：它依赖 coverage 包，当前环境装不上。
覆盖率的原理其实很简单：在代码运行时记录「哪些行被执行过」，
执行行数 ÷ 可执行行数 = 覆盖率。trace 模块就是标准库里的现成实现。

可执行行数的判定用 ast：一条语句占一行（简单可靠，和 coverage.py
的算法相比会略少算多行语句的续行，但对这个练习足够了）。

用法：
    cd ai-engineering/04-pytest
    ../../../.venv/Scripts/python.exe -X utf8 measure_coverage.py
"""

from __future__ import annotations

import ast
import sys
import trace
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG_DIR = HERE.parent / "02-refactor"

# trace 会连 pytest 内部一起追踪，用 ignore 目录把它排除掉，
# 只统计我们自己的 refactored 包。
sys.path.insert(0, str(PKG_DIR))

import pytest  # noqa: E402
import refactored  # noqa: E402

PKG_ROOT = str(Path(refactored.__file__).resolve().parent)


def executable_lines(path: Path) -> set[int]:
    """用 ast 找出「可执行语句」所在的行号。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt):
            # docstring 是表达式语句，不算「必须被测到」的行
            if (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                continue
            lines.add(node.lineno)
    return lines


def main() -> None:
    tracer = trace.Trace(count=1, trace=0, ignoremods=(), ignoredirs=[sys.prefix, sys.exec_prefix])
    # 注意别把 ai_tests_to_review.py 算进来——那是给用户找茬用的，故意混着假测试
    code = (
        "import pytest; pytest.main(['-q', '--no-header', '-p', 'no:cacheprovider',"
        " 'test_report.py', 'test_loader.py', 'test_buggy_contract.py'])"
    )
    tracer.runctx(code, globals={"__name__": "__main__"}, locals={})

    counts = tracer.results().counts  # {(文件, 行号): 次数}
    executed_by_file: dict[str, set[int]] = {}
    for (fname, lineno) in counts:
        if fname.replace("\\\\", "/").startswith(PKG_ROOT) and fname.endswith(".py"):
            executed_by_file.setdefault(fname, set()).add(lineno)

    total_exec = total_hit = 0
    print(f"被测包：{PKG_ROOT}\n")
    print(f"{'文件':<28}{'可执行行':>8}{'命中':>6}{'覆盖率':>9}")
    for path in sorted(Path(PKG_ROOT).rglob("*.py")):
        if path.name == "__init__.py" and path.read_text(encoding="utf-8").strip() == "":
            continue  # 空文件没有可执行行，跳过
        all_lines = executable_lines(path)
        hit = all_lines & executed_by_file.get(str(path), set())
        n, h = len(all_lines), len(hit)
        total_exec += n
        total_hit += h
        pct = f"{h / n * 100:.0f}%" if n else "—"
        print(f"{path.relative_to(PKG_ROOT).as_posix():<28}{n:>8}{h:>6}{pct:>9}")

    pct = total_hit / total_exec * 100
    print(f"\n{'合计':<28}{total_exec:>8}{total_hit:>6}{pct:>8.0f}%")
    print(f"\n达标线 60%：{'✅ 达标' if pct >= 60 else '❌ 未达标，缺的是哪几块自己往下找'}")

    # 顺手列出完全没被测到的文件，方便定位缺口
    print("\n一行都没被执行的文件：")
    for path in sorted(Path(PKG_ROOT).rglob("*.py")):
        if str(path) not in executed_by_file and path.name != "__init__.py":
            print(f"  - {path.relative_to(PKG_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
