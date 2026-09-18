@echo off
REM Windows build: compile every UI, package TOML data, and exclude unused Qt modules.

echo 編譯 .ui 為 Python 模塊到 lib\ ...
if not exist lib mkdir lib
pyside6-uic ui\Main.ui -o lib\ui_main.py
pyside6-uic ui\WidgetSingle.ui -o lib\ui_widgetsingle.py
pyside6-uic ui\WidgetMulti.ui -o lib\ui_widgetmulti.py
pyside6-uic ui\WidgetLift.ui -o lib\ui_widgetlift.py
pyside6-uic ui\WidgetScrollSingle.ui -o lib\ui_widgetscrollsingle.py

echo 安裝或更新 Nuitka 與 PySide6
python -m pip install --upgrade pip
pip install --upgrade nuitka PySide6 || echo "pip install failed, please install dependencies manually"

echo 用 Nuitka 編譯項目
nuitka ^
  --standalone ^
  --enable-plugin=pyside6 ^
  --include-data-file=.config.default.toml=.config.default.toml ^
  --include-data-dir=doc=doc ^
  --include-data-dir=theme=theme ^
  --output-dir=build ^
  --output-filename=randname.exe ^
  --lto=yes ^
  --assume-yes-for-downloads ^
  --windows-disable-console ^
  --nofollow-import-to=PySide6.QtDesigner ^
  --nofollow-import-to=PySide6.QtUiTools ^
  --nofollow-import-to=PySide6.QtNetwork ^
  --nofollow-import-to=PySide6.QtSql ^
  --nofollow-import-to=PySide6.QtTest ^
  --nofollow-import-to=PySide6.QtXml ^
  main.py

echo 構建完成，輸出目錄：build\
pause
