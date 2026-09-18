#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Linux build: compile every UI, package TOML data, and exclude unused Qt modules.

set -euo pipefail

echo "安裝 Nuitka 與 PySide6"
python -m pip install --upgrade pip
pip install nuitka==4.1.3 PySide6==6.11.1

echo "編譯 .ui 為 Python 模塊到 lib/ ..."
mkdir -p lib
pyside6-uic ui/Main.ui -o lib/ui_main.py
pyside6-uic ui/WidgetSingle.ui -o lib/ui_widgetsingle.py
pyside6-uic ui/WidgetMulti.ui -o lib/ui_widgetmulti.py
pyside6-uic ui/WidgetLift.ui -o lib/ui_widgetlift.py
pyside6-uic ui/WidgetScrollSingle.ui -o lib/ui_widgetscrollsingle.py

echo "用 Nuitka 編譯項目"
nuitka \
  --standalone \
  --enable-plugin=pyside6 \
  --include-data-file=.config.default.toml=.config.default.toml \
  --include-data-dir=doc=doc \
  --include-data-dir=theme=theme \
  --output-dir=build \
  --output-filename=randname \
  --show-progress \
  --lto=yes \
  --assume-yes-for-downloads \
  --nofollow-import-to=PySide6.QtDesigner \
  --nofollow-import-to=PySide6.QtUiTools \
  --nofollow-import-to=PySide6.QtNetwork \
  --nofollow-import-to=PySide6.QtSql \
  --nofollow-import-to=PySide6.QtTest \
  --nofollow-import-to=PySide6.QtXml \
  main.py

echo "構建完成，輸出目錄：build/"
