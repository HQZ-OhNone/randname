"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
import sys
import random
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from lib.importnames import names

class RandomPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("隨機抽人小工具")
        self.setGeometry(200, 200, 300, 150)

        # 顯示結果的 Label
        self.result_label = QLabel("等待抽取...", self)
        self.result_label.setStyleSheet("font-size: 18px;")

        # 按鈕
        self.btn = QPushButton("開始抽人", self)
        self.btn.clicked.connect(self.pick_student)

        # 佈局
        layout = QVBoxLayout()
        layout.addWidget(self.result_label)
        layout.addWidget(self.btn)
        self.setLayout(layout)

    def pick_student(self):
        namecode = random.randint(0, len(names) - 1)
        print(f"抽到的編號：{namecode}")
        name = names[str(namecode)]
        print(f"抽到的名字：{name}")
        self.result_label.setText(f"抽到：{name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RandomPicker()
    window.show()
    sys.exit(app.exec())
