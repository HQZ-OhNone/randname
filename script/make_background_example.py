"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>.
"""

"""从 ui/randname-start.png 生成背景示例图，保持 cover 裁切。"""

import argparse
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QImage

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT / "ui" / "randname-start.png"
DEFAULT_OUTPUT = ROOT / "ui" / "background-example.png"


def make_cover(source: Path, output: Path, width: int, height: int) -> Path:
    image = QImage(str(source))
    if image.isNull():
        raise ValueError(f"无法读取图片: {source}")
    scaled = image.scaled(
        width,
        height,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    x = max(0, (scaled.width() - width) // 2)
    y = max(0, (scaled.height() - height) // 2)
    cropped = scaled.copy(x, y, width, height)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not cropped.save(str(output), "PNG"):
        raise OSError(f"无法写入图片: {output}")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    args = parser.parse_args()
    app = QGuiApplication.instance() or QGuiApplication([])  # noqa: F841
    result = make_cover(args.source, args.output, args.width, args.height)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
