"""
ScrollSingle mode implementation.

Behavior:
- Uses ui_widgetsingle layout (label + button) as the widget
- Start: begin cycling through names rapidly (QTimer); every full cycle shuffle the name order
- Stop: stop timer and current name is the result
- Each start creates a new randomized order based on the initially loaded names
- Exposes a simple API: ScrollController(widget, names, on_result_callback)

All functionality lives here; UI wiring is done in main.py
"""

from PySide6.QtCore import QTimer
import random
from datetime import datetime

class ScrollController:
    def __init__(self, label_widget, button_widget, names_dict, on_result=None):
        """label_widget: QLabel to show name
           button_widget: QPushButton to toggle start/stop
           names_dict: dict of key->name
           on_result: callable(result_str, meta_dict)
        """
        self.label = label_widget
        self.button = button_widget
        self.names = names_dict.copy() if isinstance(names_dict, dict) else {}
        self.on_result = on_result

        self.timer = QTimer()
        self.timer.setInterval(80)  # 80ms 约等于每秒约12次切换
        self.timer.timeout.connect(self._tick)

        self.running = False
        self.current_order = []
        self.index = 0

        # 按钮绑定
        try:
            self.button.clicked.connect(self.toggle)
        except Exception:
            pass

    def _now_str(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _prepare_new_order(self):
        keys = list(self.names.keys())
        random.shuffle(keys)
        # build order as list of names
        self.current_order = [self.names[k] for k in keys]
        self.index = 0

    def _tick(self):
        if not self.current_order:
            self._prepare_new_order()
        # 显示当前名字并递增索引
        if self.label is not None:
            self.label.setText(str(self.current_order[self.index]))
        self.index += 1
        # If completed one full loop, reshuffle and restart index
        if self.index >= len(self.current_order):
            self._prepare_new_order()

    def start(self):
        if self.running:
            return
        self.running = True
        self._prepare_new_order()
        self.timer.start()
        if self.button is not None:
            self.button.setText("停止")

    def stop(self):
        if not self.running:
            return
        self.timer.stop()
        self.running = False
        if self.button is not None:
            self.button.setText("开始")
        # current displayed name is the result
        result = self.label.text() if self.label is not None else None
        meta = {"time": self._now_str(), "mode": "scrollsingle"}
        if self.on_result is not None:
            try:
                self.on_result(result, meta)
            except Exception:
                pass
        return result

    def toggle(self):
        if self.running:
            return self.stop()
        else:
            return self.start()

    def update_names(self, new_names: dict):
        """更新可抽取的名字（不会重置按钮状态），保持现有running状态"""
        self.names = new_names.copy() if isinstance(new_names, dict) else {}
        # 如果没有顺序或顺序超过名字数，重新准备
        if not self.current_order or len(self.current_order) != len(self.names):
            self._prepare_new_order()

