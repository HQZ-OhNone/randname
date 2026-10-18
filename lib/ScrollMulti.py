"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
"""
滚动多抽 (ScrollMulti) mode implementation.

Behavior:
- Reuses the Multi page layout: one large output box, a quantity spinner and a
  single large action button.
- Start: create ``n`` reels (n = selected quantity) and roll every reel with a
  shared timer. All reels are shown together in the single output box, one name
  per slot. The OutputView decides single-line / multi-line / font shrinking.
  The action button becomes "停止（n/n）".
- Every press stops the next rolling reel, fixing the name it currently shows.
  A name fixed this round is removed from the round pool, so no other reel can
  draw it again in this round. The button shows "停止（x/n）" with x the number
  of reels still rolling.
- When the last reel stops the round finishes, reports a Multi-compatible result
  to ``on_result`` and returns the button to its draw state.

Output example:
example = {"mode":"ScrollMulti",
           "time":"2026-03-15-12:30:23",
           "quantity":{"total":6,
                       "selected":3},
           "outdict":{"0":{"name":"李華","code":"1"},
                      "1":{"name":"周原","code":"0"},
                      "2":{"name":"珍瑞","code":"3"}}
           }
"""

import random
from datetime import datetime

from PySide6.QtCore import QTimer


def _interval_for_rate(rate) -> int:
    """Convert a ticks-per-second setting into a safe QTimer interval."""
    try:
        ticks = int(rate)
    except (TypeError, ValueError):
        ticks = 30
    return max(1, 1000 // max(1, ticks))


class ScrollMultiController:
    def __init__(self, view, button, names_dict, on_result=None, rate=30,
                 draw_text="抽取", stop_format="停止（{remaining}/{total}）",
                 reset_text="等待输入", on_warning=None, on_state_change=None):
        """view: OutputView that shows every reel inside one box
           button: QPushButton used to start and to stop reels one by one
           names_dict: dict of key->name
           on_result: callable(result_dict, meta_dict) when a round completes
           on_warning: callable(message) when a round cannot start
           on_state_change: callable() whenever the button state changes
        """
        self.view = view
        self.button = button
        self.names = names_dict.copy() if isinstance(names_dict, dict) else {}
        self.on_result = on_result
        self.on_warning = on_warning
        self.on_state_change = on_state_change
        self.draw_text = draw_text
        self.stop_format = stop_format
        self.reset_text = reset_text

        self.quantity = 1
        self.running = False
        self.pool = {}      # key -> name still available this round
        self.total = 0      # reels created for the current round
        self.reels = []     # list of reel state dicts

        self.timer = QTimer()
        self.timer.setInterval(_interval_for_rate(rate))
        self.timer.timeout.connect(self._tick)

        try:
            if self.button is not None:
                self.button.clicked.connect(self.handle_click)
        except Exception:
            pass
        self._set_button_text()
        self._show_placeholder()

    # ------------------------------------------------------------------ helpers
    def _now_str(self) -> str:
        return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    def _update_label(self) -> None:
        if self.view is None:
            return
        if not self.reels:
            self.view.set_message(str(self.reset_text))
            return
        self.view.set_names(reel["name"] for reel in self.reels)

    def _set_button_text(self) -> None:
        if self.button is None:
            return
        try:
            if self.running:
                remaining = self._remaining()
                self.button.setText(self.stop_format.format(remaining=remaining, total=self.total))
            else:
                self.button.setText(self.draw_text)
        except Exception:
            pass
        self._notify_state()

    def _notify_state(self) -> None:
        if self.on_state_change is not None:
            try:
                self.on_state_change()
            except Exception:
                pass

    def _remaining(self) -> int:
        return sum(1 for reel in self.reels if reel["active"])

    def _new_order(self):
        keys = list(self.pool.keys())
        random.shuffle(keys)
        return keys

    def _show_placeholder(self) -> None:
        self.reels = []
        self.total = 0
        self._update_label()

    # ------------------------------------------------------------------- public
    def set_quantity(self, quantity) -> None:
        try:
            value = int(quantity)
        except (TypeError, ValueError):
            value = 1
        new_quantity = max(1, value)
        if new_quantity != self.quantity and not self.running and self.view is not None:
            # 数量变化后，下一轮重新决定格子布局。
            self.view.clear_round()
        self.quantity = new_quantity

    def update_names(self, new_names: dict) -> None:
        updated = new_names.copy() if isinstance(new_names, dict) else {}
        if updated != self.names:
            self.names = updated
            self.reset()

    def update_rate(self, rate) -> int:
        interval = _interval_for_rate(rate)
        self.timer.setInterval(interval)
        return interval

    def set_button_texts(self, draw_text: str, stop_format: str, reset_text=None) -> None:
        self.draw_text = draw_text
        self.stop_format = stop_format
        if reset_text is not None:
            self.reset_text = reset_text
            # Only refresh the idle placeholder; never clobber a shown result.
            if not self.running and not self.reels:
                self._update_label()
        self._set_button_text()

    def handle_click(self):
        if self.running:
            return self.stop_next()
        return self.start()

    def start(self):
        if self.running:
            return None
        if not self.names:
            if self.on_warning is not None:
                try:
                    self.on_warning(len(self.names))
                except Exception:
                    pass
            return None

        requested = max(1, int(self.quantity))
        self.total = min(requested, len(self.names))
        if requested > len(self.names) and self.on_warning is not None:
            try:
                self.on_warning(len(self.names))
            except Exception:
                pass

        self.pool = dict(self.names)
        self.reels = [
            {
                "active": True,
                "order": self._new_order(),
                "index": 0,
                "key": None,
                "name": "",
            }
            for _ in range(self.total)
        ]

        if self.view is not None:
            self.view.begin_round(list(self.pool.values()), self.total)
        self.running = True
        self._tick()  # show a first name immediately instead of an empty box
        self.timer.start()
        self._set_button_text()
        return None

    def stop_next(self):
        if not self.running:
            return None
        reel = next((item for item in self.reels if item["active"]), None)
        if reel is None:
            self._finish()
            return None

        reel["active"] = False
        fixed_key = reel["key"]
        if fixed_key not in self.pool:
            # The displayed name may already be taken by an earlier stop (fast
            # clicks between ticks); draw a fresh name from the remaining pool.
            remaining_keys = list(self.pool.keys())
            fixed_key = random.choice(remaining_keys) if remaining_keys else None
        if fixed_key is None:
            reel["key"] = None
            reel["name"] = self.reset_text
        else:
            reel["key"] = fixed_key
            reel["name"] = self.pool[fixed_key]
            self.pool.pop(fixed_key, None)
        # Rebuild the remaining reels' orders so they never land on a fixed name.
        for item in self.reels:
            if item["active"]:
                item["order"] = self._new_order()
                item["index"] = 0
        self._update_label()

        if self._remaining() == 0:
            self._finish()
        else:
            self._set_button_text()
        return reel["name"]

    def _finish(self) -> None:
        self.timer.stop()
        self.running = False
        result = self._build_result()
        self._set_button_text()
        if self.on_result is not None:
            try:
                self.on_result(result, {"time": self._now_str(), "mode": "ScrollMulti"})
            except Exception:
                pass

    def _build_result(self) -> dict:
        outdict = {}
        for index, reel in enumerate(self.reels):
            if reel["key"] is not None:
                outdict[str(index)] = {"code": reel["key"], "name": reel["name"]}
        return {
            "mode": "ScrollMulti",
            "time": self._now_str(),
            "quantity": {"total": len(self.names), "selected": self.total},
            "outdict": outdict,
        }

    def reset(self) -> None:
        self.timer.stop()
        self.running = False
        self.pool = {}
        if self.view is not None:
            self.view.clear_round()
        self._show_placeholder()
        self._set_button_text()

    def show_result(self, result) -> None:
        """Display a stored ScrollMulti result in the output box (memory import)."""
        if not isinstance(result, dict):
            return
        outdict = result.get("outdict", {})
        if not isinstance(outdict, dict) or not outdict:
            return
        reels = []
        for value in outdict.values():
            if not isinstance(value, dict):
                continue
            if "name" in value:
                reels.append({"active": False, "order": [], "index": 0,
                              "key": value.get("code"), "name": value.get("name")})
            elif len(value) == 1:
                key, name = next(iter(value.items()))
                reels.append({"active": False, "order": [], "index": 0, "key": key, "name": name})
        if not reels:
            return
        self.timer.stop()
        self.running = False
        self.pool = {}
        self.total = len(reels)
        self.reels = reels
        if self.view is not None:
            self.view.clear_round()
        self._update_label()
        self._set_button_text()

    # ------------------------------------------------------------------ internal
    def _tick(self) -> None:
        if not self.pool:
            return
        for reel in self.reels:
            if not reel["active"]:
                continue
            if reel["index"] >= len(reel["order"]):
                reel["order"] = self._new_order()
                reel["index"] = 0
            if not reel["order"]:
                continue
            key = reel["order"][reel["index"]]
            reel["index"] += 1
            # Guard against a stale key left over from a previous pool.
            if key not in self.pool:
                reel["order"] = self._new_order()
                reel["index"] = 0
                if not reel["order"]:
                    continue
                key = reel["order"][reel["index"]]
                reel["index"] += 1
            reel["key"] = key
            reel["name"] = self.pool[key]
        self._update_label()
