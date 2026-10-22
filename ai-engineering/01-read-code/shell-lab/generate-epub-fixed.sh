#!/usr/bin/env bash
#
# 修复版：结构与行为都保持原样，只补上「出错要说话」这件事。
# 每处改动都标了序号，与 walkthrough_generate_epub.md 的问题清单一一对应。
#
# 与原版的差别只有 10 处，全部是"加防御"，没有改变成功路径的输出。

set -euo pipefail
#  ① -e 任何命令失败立即退出；-u 用了未定义变量就报错；-o pipefail 管道任一环失败即失败
#     这三条一加，原版那种"pandoc 挂了还报 Done!"就不可能发生了

readonly metadata_file="epub-metadata.yaml"
worktmp=""

cleanup() { rm -f "${worktmp:-}"; }
trap cleanup EXIT
#  ② 清理放进 trap，而不是依赖最后一行 rm。
#     ⚠️ 踩过的坑：worktmp 千万别写成 local —— EXIT 的 trap 在函数返回后才跑，
#        那时 local 变量已销毁，set -u 会报 unbound variable，rm 也跑不掉，临时文件残留。

require_pandoc() {
  command -v pandoc >/dev/null 2>&1 || {
    echo "Error: pandoc is not installed." >&2
    exit 1
  }
}
#  ③ 依赖检查写在主流程最前面，直接写死要检查什么；
#     原版搞了个 dependencies 数组，但数组在函数定义之后才赋值，靠"调用时机"才成立，很脆

generate_from_stdin() {
  local outfile=$1
  local language=$2
  #  ④ 入参用 local，别把 outfile/language 泄漏成全局变量

  echo "Generating '$language' ..."

  #  ⑤ 去掉 <&0：pandoc 不加 -i 时默认就读 stdin，<&0 是纯噪音。
  #     原版还配了个 `cat file | pandoc` 的无用管道，一个多余进程 + 一个多余重定向，互相抵消。
  #     变量加引号，文件名带空格也不会裂开。
  pandoc --metadata-file="$metadata_file" \
         --metadata="lang:$language" \
         --from=markdown \
         -o "$outfile"

  echo "Done! You can find the '$language' book at ./$outfile"
}

generate_with_solutions() {
  worktmp=$(mktemp "${TMPDIR:-/tmp}/system-design-primer-epub.XXXXXX")
  #  ⑥ 用 TMPDIR 兜底 /tmp，XXX 改成 XXXXXX（mktemp 的标准占位符）；
  #     顺手修掉原版的拼写错误 sytem -> system

  cat ./README.md >> "$worktmp"

  for dir in ./solutions/system_design/*/; do
    #  ⑦ glob 末尾加 /，让 shell 自己只匹配目录；下面的 [[ -d ]] 就成了双保险
    [[ -d "$dir" ]] || continue
    #  ⑧ 去掉原版那个冒号。原版写的是 `: [[ -d "$dir" ]] && (...)`，
    #     `:` 是"什么都不做"的内建命令，把 `[[ ... ]]` 当成自己的参数吃掉了，
    #     于是判断根本没执行、退出码永远是 0 —— 详见文档的实测
    case $dir in *template*) continue ;; esac

    if [[ ! -f "$dir/README.md" ]]; then
      #  ⑨ 缺文件时说清楚再跳过，而不是让 cat 报错后静默继续
      echo "warning: $dir has no README.md, skipped" >&2
      continue
    fi
    cat "$dir/README.md" >> "$worktmp"
    echo "" >> "$worktmp"
  done

  generate_from_stdin 'README.epub' 'en' < "$worktmp"
  #  ⑩ 直接重定向，不要 `cat file | cmd`
}

generate() {
  local name=$1
  local language=$2

  #  ⑪ 在源头拦住：原版靠 `cat 不存在的文件` 报错，但管道后面的 pandoc 收到 0 字节，
  #     会老老实实生成一本 0 字节的空书，还报 Done!
  [[ -f "$name.md" ]] || { echo "Error: $name.md not found." >&2; exit 1; }

  generate_from_stdin "$name.epub" "$language" < "$name.md"
}

require_pandoc
generate_with_solutions
generate README-ja ja
generate README-zh-Hans zh-Hans
generate README-zh-TW zh-TW
