#!/usr/bin/env bash
set -euo pipefail

# Compile every UI file used by the application.
mkdir -p lib
pyside6-uic ui/Main.ui -o lib/ui_main.py
pyside6-uic ui/WidgetSingle.ui -o lib/ui_widgetsingle.py
pyside6-uic ui/WidgetMulti.ui -o lib/ui_widgetmulti.py
pyside6-uic ui/WidgetLift.ui -o lib/ui_widgetlift.py

# Keep build tools reproducible across local and CI builds.
python -m pip install --upgrade pip
python -m pip install "nuitka==4.1.3" "PySide6==6.11.1"

# UI source files and unused Qt modules are not included in the distribution.
nuitka \
  --standalone \
  --enable-plugin=pyside6 \
  --include-data-file=config.default.json=config.default.json \
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
