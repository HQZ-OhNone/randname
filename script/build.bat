@echo off
REM Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>
REM
REM This program is free software: you can redistribute it and/or modify it
REM under the terms of the GNU General Public License as published by the
REM Free Software Foundation, either version 3 of the License, or (at your
REM option) any later version.
REM
REM This program is distributed in the hope that it will be useful, but
REM WITHOUT ANY WARRANTY; without even the implied warranty of
REM MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
REM General Public License for more details.
REM
REM You should have received a copy of the GNU General Public License
REM along with this program. If not, see <https://www.gnu.org/licenses/>.

REM Windows build: compile every UI, package TOML data, and exclude unused Qt modules.

REM 无论从哪个目录调用，都切换到仓库根目录。
cd /d "%~dp0.."

echo 編譯全部 .ui 為 Python 模塊到 lib\ ...
if not exist lib mkdir lib
python -c "import pathlib, subprocess; [subprocess.run(['pyside6-uic', str(p), '-o', 'lib/ui_' + p.stem.lower() + '.py'], check=True) for p in sorted(pathlib.Path('ui').glob('*.ui'))]"

echo 安裝 Nuitka 與 PySide6
python -m pip install --upgrade pip
pip install nuitka==4.1.3 PySide6==6.11.1 || echo "pip install failed, please install dependencies manually"

echo 用 Nuitka 編譯項目
nuitka ^
  --standalone ^
  --enable-plugin=pyside6 ^
  --include-data-file=ui\randname1.png=ui\randname1.png ^
  --include-data-file=ui\randname-start.png=ui\randname-start.png ^
  --include-data-file=.config.default.toml=.config.default.toml ^
  --include-data-file=.name.default.toml=.name.default.toml ^
  --include-data-dir=config=config ^
  --include-data-dir=doc=doc ^
  --output-dir=build ^
  --output-filename=randname.exe ^
  --show-progress ^
  --windows-icon-from-ico=ui\randname1.ico ^
  --lto=yes ^
  --assume-yes-for-downloads ^
  --windows-disable-console ^
  --nofollow-import-to=PySide6.QtDesigner ^
  --nofollow-import-to=PySide6.QtUiTools ^
  --nofollow-import-to=PySide6.QtSql ^
  --nofollow-import-to=PySide6.QtTest ^
  --nofollow-import-to=PySide6.QtXml ^
  main.py

echo 構建完成，輸出目錄：build\
pause
