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

# Linux build: compile every UI, package TOML data, and exclude unused Qt modules.

set -euo pipefail

# 无论从哪个目录调用，都切换到仓库根目录。
cd "$(dirname "$0")/.."

echo "安裝 Nuitka 與 PySide6"
python -m pip install --upgrade pip
pip install nuitka==4.1.3 PySide6==6.11.1

echo "編譯全部 .ui 為 Python 模塊到 lib/ ..."
mkdir -p lib
for ui_file in ui/*.ui; do
  ui_name=$(basename "$ui_file" .ui | tr '[:upper:]' '[:lower:]')
  pyside6-uic "$ui_file" -o "lib/ui_${ui_name}.py"
done

echo "用 Nuitka 編譯項目"
nuitka \
  --standalone \
  --enable-plugin=pyside6 \
  --include-data-file=ui/randname1.png=ui/randname1.png \
  --include-data-file=ui/randname-start.png=ui/randname-start.png \
  --include-data-file=ui/background-example.png=ui/background-example.png \
  --include-data-file=.config.default.toml=.config.default.toml \
  --include-data-file=.name.default.toml=.name.default.toml \
  --include-data-dir=config=config \
  --include-data-dir=doc=doc \
  --output-dir=build \
  --output-filename=randname \
  --show-progress \
  --lto=yes \
  --assume-yes-for-downloads \
  --nofollow-import-to=PySide6.QtDesigner \
  --nofollow-import-to=PySide6.QtUiTools \
  --nofollow-import-to=PySide6.QtSql \
  --nofollow-import-to=PySide6.QtTest \
  --nofollow-import-to=PySide6.QtXml \
  main.py

echo "構建完成，輸出目錄：build/"
