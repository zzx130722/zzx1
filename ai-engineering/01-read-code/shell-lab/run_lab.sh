#!/usr/bin/env bash
#
# 一键复现：同一个失败场景，原版说「成功」，修复版说「失败」。
#
#   bash run_lab.sh            # 跑全部
#   bash run_lab.sh colon      # 只跑冒号那一行的小实验
#
# 不会碰你的真实数据：所有东西都在临时目录里造，退出时删掉。
# 不需要装 pandoc —— 这里用一个「假 pandoc」精确控制它成功还是失败。

set -uo pipefail          # 故意不加 -e：本脚本要跑会失败的命令，跑完还得继续

here=$(cd "$(dirname "$0")" && pwd)
# 用 POSIX 风格的 /tmp：本环境的 mktemp 在 TMPDIR 是 Windows 路径时会返回 C:\... ，
# 而 rm 的安全包装不接受带盘符的路径，导致临时目录删不掉。
if [ -d /tmp ]; then tmpbase=/tmp; else tmpbase=${TMPDIR:-/tmp}; fi
work=$(mktemp -d "$tmpbase/epub-lab.XXXXXX")
cleanup() {
  cd / 2>/dev/null || cd "$HOME"     # 先离开：rm -rf 删不掉「自己的当前目录」（Windows 会报 busy）
  rm -rf "${work:-}"
}
trap cleanup EXIT

# ---------------------------------------------------------------- 造最小仓库
make_fixture() {
  mkdir -p "$work/repo/solutions/system_design"/{design_a,design_b,template_thing}
  cd "$work/repo" || exit 1
  printf '# System Design Primer\n\nintro text\n'   > README.md
  printf '# Design A\n\nA content\n'                > solutions/system_design/design_a/README.md
  printf '# Design B\n\nB content\n'                > solutions/system_design/design_b/README.md
  printf '# Template\n\nshould be skipped\n'        > solutions/system_design/template_thing/README.md
  printf 'this is a file, not a directory\n'        > solutions/system_design/noise.txt
  printf 'title: T\ncreator: C\ndate: 2026\n'       > epub-metadata.yaml
  mkdir -p bin
}

# 假 pandoc：moku=ok 就成功（把 stdin 字节数写进产物），moku=fail 就失败
make_pandoc() {
  local mode=$1
  cat > bin/pandoc <<EOF
#!/usr/bin/env bash
out=""
while [ \$# -gt 0 ]; do [ "\$1" = "-o" ] && { out="\$2"; shift; }; shift; done
n=\$(wc -c)
if [ "$mode" = "fail" ]; then
  echo "[fake pandoc] 我失败了（exit 1）" >&2
  exit 1
fi
printf 'FAKE-EPUB(%s bytes)\n' "\$n" > "\$out"
exit 0
EOF
  chmod +x bin/pandoc
}

list_products() {
  local f
  shopt -s nullglob
  local files=( *.epub )
  shopt -u nullglob
  if [ ${#files[@]} -eq 0 ]; then
    echo "      产物：一个 .epub 都没有"
  else
    for f in "${files[@]}"; do
      printf '      产物：%-20s %s\n' "$f" "$(cat "$f" 2>/dev/null)"
    done
  fi
}

run_pair() {
  local title=$1 mode=$2
  echo
  echo "════════════════════════════════════════════════════════════════"
  echo " $title"
  echo "════════════════════════════════════════════════════════════════"
  make_pandoc "$mode"

  echo
  echo "── 原版 generate-epub.sh ──"
  rm -f ./*.epub
  PATH="$work/repo/bin:$PATH" bash "$here/generate-epub.sh" 2>"$work/err_old.txt"
  local code=$?
  echo "      退出码：$code   $([ $code -eq 0 ] && echo '← 它说"一切正常"' || echo '← 它认错了')"
  list_products
  local n
  n=$(grep -c . "$work/err_old.txt" 2>/dev/null || echo 0)
  [ "$n" -gt 0 ] && sed 's/^/      stderr: /' "$work/err_old.txt"

  echo
  echo "── 修复版 generate-epub-fixed.sh ──"
  rm -f ./*.epub
  PATH="$work/repo/bin:$PATH" bash "$here/generate-epub-fixed.sh" 2>"$work/err_new.txt"
  code=$?
  echo "      退出码：$code   $([ $code -eq 0 ] && echo '← 它说"一切正常"' || echo '← 它认错了（这次它是真的没错）')"
  list_products
  n=$(grep -c . "$work/err_new.txt" 2>/dev/null || echo 0)
  [ "$n" -gt 0 ] && sed 's/^/      stderr: /' "$work/err_new.txt"
}

colon_lab() {
  echo "════════════════════════════════════════════════════════════════"
  echo " 单独看第 22 行那个冒号：: [[ -d \"\$dir\" ]] && ..."
  echo "════════════════════════════════════════════════════════════════"
  mkdir -p "$work/colon/realdir" "$work/colon"
  printf 'x\n' > "$work/colon/realdir/README.md"
  printf 'x\n' > "$work/colon/notadir.txt"
  cd "$work/colon" || exit 1

  echo
  local d a b
  for d in ./nonexistent ./notadir.txt ./realdir; do
    a=$( : [[ -d "$d" ]] && echo "判定为目录，执行 cd" )
    b=$( [[ -d "$d" ]] && echo "判定为目录，执行 cd" )
    printf '  目标 %-14s\n' "$d"
    printf '      原版（带冒号）：%s\n' "${a:-跳过}"
    printf '      正确（无冒号）：%s\n' "${b:-跳过}"
    echo
  done
  echo "  看到没：带冒号时，不存在的路径和普通文件都被当成目录了。"
  echo "  原因：\`:\` 是内建命令，把 [[ -d \"\$dir\" ]] 当成自己的参数吃掉了，"
  echo "        它永远返回 0，所以 && 后面永远执行。"
  echo "  在真实仓库里为什么没炸：那个目录下恰好只有子目录，__init__.py 被 case 排除了。"
  echo "  但只要有人往里放一个 .md 或 .txt，每次构建就会多一条 stderr 报错。"
}

echo "实验目录：$work"
make_fixture

if [ "${1:-}" = "colon" ]; then
  colon_lab
  exit 0
fi

run_pair "场景 A：pandoc 每次都失败（比如磁盘满 / 参数不兼容）" fail
run_pair "场景 B：pandoc 正常，但仓库里缺 README-ja.md 等译文" ok
colon_lab

echo
echo "════════════════════════════════════════════════════════════════"
echo " 结论"
echo "════════════════════════════════════════════════════════════════"
echo " 场景 A：原版 4 次 'Done!' + 退出码 0，一本都没生成；修复版第 1 次就停。"
echo " 场景 B：原版生成 3 本 0 字节空书并报成功；修复版在前面就报 Error。"
echo " 这就是「脚本能跑」和「脚本可信」的区别。"
