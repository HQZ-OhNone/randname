#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# 用法：script/last-history-reader.sh [-n 数量] [-o 输出文件]
# 作用：截取 doc/history.md 最新若干条记录到 /tmp，供 agent 快速了解
#       变更历史的语言风格；终端只输出路径与标题，不打印正文。

set -euo pipefail

# 无论从哪个目录调用，都切换到仓库根目录。
cd "$(dirname "$0")/.."

COUNT=3
OUT="/tmp/randname-history-latest.md"
HISTORY="doc/history.md"

usage() {
  cat <<'EOF'
用法: script/last-history-reader.sh [-n 数量] [-o 输出文件]

  -n  截取最新的记录条数（默认 3）
  -o  输出文件路径（默认 /tmp/randname-history-latest.md）
  -h  显示帮助

说明: 只把最新记录写入输出文件，终端仅显示输出路径、行数与标题。
EOF
}

while getopts "n:o:h" opt; do
  case "$opt" in
    n) COUNT="$OPTARG" ;;
    o) OUT="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

if ! [[ "$COUNT" =~ ^[1-9][0-9]*$ ]]; then
  echo "错误: -n 必须是正整数，收到 '$COUNT'" >&2
  exit 2
fi

if [[ ! -f "$HISTORY" ]]; then
  echo "错误: 找不到 $HISTORY" >&2
  exit 1
fi

# 从第一个二级标题开始截取，取满 COUNT 条后遇到下一条标题即停止。
awk -v limit="$COUNT" '
  /^## / {
    section++
    if (section > limit) exit
  }
  section >= 1 { print }
' "$HISTORY" > "$OUT"

if [[ ! -s "$OUT" ]]; then
  echo "错误: $HISTORY 中未找到 '## ' 格式的记录" >&2
  exit 1
fi

echo "输出文件: $OUT"
echo "记录条数: $COUNT"
echo "行数: $(wc -l < "$OUT")"
echo "标题:"
grep '^## ' "$OUT" | sed 's/^/  /'
