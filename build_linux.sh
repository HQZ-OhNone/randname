#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Linux 下的自動化構建腳本：
# 1) 使用 pyside6-uic 將 ui/*.ui 編譯爲 Python 模塊，放在 lib/ 目錄
# 2) 使用 Nuitka 編譯整個項目（不再包含 ui/ 目錄作為數據）

set -euo pipefail

echo "編譯 .ui 為 Python 模塊到 lib/ ..."
mkdir -p lib
pyside6-uic ui/Main.ui -o lib/ui_main.py
pyside6-uic ui/WidgetSingle.ui -o lib/ui_widgetsingle.py
pyside6-uic ui/WidgetMulti.ui -o lib/ui_widgetmulti.py
pyside6-uic ui/WidgetLift.ui -o lib/ui_widgetlift.py

echo "安裝或更新 Nuitka 與 PySide6(可選)..."
python -m pip install --upgrade pip
pip install --upgrade nuitka PySide6 || true

echo "用 Nuitka 編譯項目"
# 注意：自 3.3.0 后不再包含 --include-data-dir=ui=ui
nuitka \
  --standalone \
  --enable-plugin=pyside6 \
  --include-data-dir=config=config \
  --include-data-dir=doc=doc \
  --output-dir=build \
  --output-filename=randname \
  --show-progress \
  --lto=yes \
  --assume-yes-for-downloads \
  main.py

echo "構建完成，輸出目錄：build/"
