"""等价性校验：重构有没有把原来的行为改坏。

两件事：

  A. 回归等价 —— 在**干净数据**上，新旧两版输出必须逐字节相同。
     这是重构的安全网：如果这里不一致，说明改动影响了正常逻辑。

  B. 差异审计 —— 在**脏数据**上，两版输出必须不同，而且每一处差异
     都要能对应到 REFACTOR-NOTES.md 里列出的某个已修 bug。
     如果脏数据上也完全一样，说明号称「修了 bug」其实没修。

跑法：
    cd ai-engineering/02-refactor
    ../../.venv/Scripts/python.exe -X utf8 check_equivalence.py
"""

from __future__ import annotations

import difflib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PY, "-X", "utf8", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def run_legacy(csv_name: str) -> str:
    proc = _run(["legacy_sales_report.py", csv_name])
    if proc.returncode != 0:
        raise SystemExit(f"legacy 跑挂了：\n{proc.stderr}")
    legacy_out = ROOT / "report_legacy.txt"
    if legacy_out.exists():
        legacy_out.unlink()  # 原版会顺手写文件，这里清掉，避免污染工作区
    return proc.stdout


def run_new(csv_name: str, out_name: str) -> tuple[str, str]:
    proc = _run(["-m", "refactored.cli", csv_name, "--out", out_name])
    if proc.returncode != 0:
        raise SystemExit(f"refactored 跑挂了：\n{proc.stderr}")
    written = ROOT / out_name
    if written.exists():
        written.unlink()
    return proc.stdout, proc.stderr


def diff_lines(old: str, new: str) -> list[str]:
    return list(
        difflib.unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile="legacy",
            tofile="refactored",
            lineterm="",
        )
    )


def main() -> int:
    failures: list[str] = []

    # ---------------- A. 干净数据：必须完全一致 ----------------
    print("=" * 64)
    print("A. 干净数据（data/sales_clean.csv）—— 期望：逐字节相同")
    print("=" * 64)
    old = run_legacy("data/sales_clean.csv")
    new, new_err = run_new("data/sales_clean.csv", "report_new_clean.txt")
    print(new.rstrip("\n"))
    if new_err.strip():
        print(f"\n（新版还打了警告，干净数据不该有：{new_err.strip()}）")
        failures.append("干净数据上出现了不该有的警告")
    # 原版是 print(s)，而 s 自己以 \n 结尾 → stdout 末尾多一个空行。
    # 重构版用 print(text, end="") 修掉了这个多余空行。这是唯一允许的差异，
    # 所以比较前先把两侧的尾部空行去掉，其余内容必须一字不差。
    if old.rstrip("\n") == new.rstrip("\n"):
        print("\n[PASS] 去掉尾部空行后完全一致（原版多打的那一个空行是 print(s) 的副作用）")
    else:
        print("\n[FAIL] 干净数据上就不一致了，这是真回归：")
        print("\n".join(diff_lines(old.rstrip("\n"), new.rstrip("\n"))))
        failures.append("干净数据上输出不一致")

    # ---------------- B. 脏数据：必须不同，且差异可解释 ----------------
    print()
    print("=" * 64)
    print("B. 脏数据（data/sales_dirty.csv）—— 期望：不同，差异全部可解释")
    print("=" * 64)
    old_d = run_legacy("data/sales_dirty.csv")
    new_d, err_d = run_new("data/sales_dirty.csv", "report_new_dirty.txt")

    print("--- 原版（legacy）---")
    print(old_d.rstrip("\n"))
    print("--- 新版（refactored）---")
    print(new_d.rstrip("\n"))

    changes = diff_lines(old_d.rstrip("\n"), new_d.rstrip("\n"))
    print("\n--- 差异 ---")
    print("\n".join(changes) if changes else "（没有差异 —— 那 3 个 bug 到底修了没有？）")

    print("\n--- 新版给出的警告（原版一条都没有）---")
    warns = [ln for ln in err_d.splitlines() if ln.strip()]
    print("\n".join(warns) if warns else "（无）")

    if old_d == new_d:
        failures.append("脏数据上也完全一致，所谓的 bug 修复没生效")
    if len(warns) < 2:
        failures.append(f"警告只有 {len(warns)} 条，至少该有 2 条（空金额 / 重复订单号）")

    # 变动行数写死在这里：改数据或改逻辑后，这个数字变了就说明行为又动了。
    # 计数方式：diff 里每一处变动会产生「一行 -、一行 +」，所以要除 2。
    # 当前期望 8 行 → 4 处变动：East / North / South 三个区域的金额 + TOTAL（West 全程未受影响）
    expected_diff_lines = 8
    changed = [
        ln
        for ln in changes
        if ln.startswith(("-", "+")) and not ln.startswith(("---", "+++"))
    ]
    print(f"\ndiff 变动行数：{len(changed)}（= {len(changed) // 2} 处），期望：{expected_diff_lines}（= 4 处）")
    if len(changed) != expected_diff_lines:
        failures.append(f"diff 变动行数是 {len(changed)}，与预期的 {expected_diff_lines} 不符")

    print()
    print("=" * 64)
    if failures:
        print(f"[FAIL] {len(failures)} 项没过：")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("[PASS] 干净数据行为不变，脏数据差异全部可解释，警告齐备")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
