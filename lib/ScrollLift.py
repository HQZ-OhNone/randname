"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

"""滚动减量抽（ScrollLift）。

行为：
- “滚动”部分与 ScrollMulti 相同：多个转盘同时轮播，逐个停止；
- “减量”部分与 Lift 相同：本轮已抽中的姓名从剩余池移除，下一轮不再出现；
- “重置”恢复完整名单；
- 结果同时包含 outdict（本轮抽中）和 Liftdict（本轮之后剩余），
  因此导入记忆后可以恢复剩余池继续抽取。
"""

from .ScrollMulti import ScrollMultiController


class ScrollLiftController(ScrollMultiController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lift_pool = dict(self.names)
        self.round_available = 0

    def start(self):
        if self.running:
            return None
        if not self.lift_pool:
            if self.on_warning is not None:
                try:
                    self.on_warning(0)
                except Exception:
                    pass
            return None

        requested = max(1, int(self.quantity))
        available = len(self.lift_pool)
        self.total = min(requested, available)
        if requested > available and self.on_warning is not None:
            try:
                self.on_warning(available)
            except Exception:
                pass

        self.round_available = available
        self.pool = dict(self.lift_pool)
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
        self._tick()
        self.timer.start()
        self._set_button_text()
        return None

    def _finish(self) -> None:
        # 本轮停止后，pool 中剩下的就是下一轮可用的剩余名单。
        self.lift_pool = dict(self.pool)
        super()._finish()

    def _build_result(self) -> dict:
        return {
            "mode": "ScrollLift",
            "time": self._now_str(),
            "quantity": {
                "total": len(self.names),
                "wasted": max(0, len(self.names) - self.round_available),
                "selected": self.total,
                "Lift": max(0, self.round_available - self.total),
            },
            "alllist": dict(self.names),
            "outdict": {
                str(index): {"code": reel["key"], "name": reel["name"]}
                for index, reel in enumerate(self.reels)
                if reel["key"] is not None
            },
            "Liftdict": dict(self.pool),
        }

    def reset(self) -> None:
        super().reset()
        self.lift_pool = dict(self.names)
        self.round_available = 0

    def show_result(self, result) -> None:
        """显示记忆中的 ScrollLift 结果，并恢复剩余名单。"""
        if not isinstance(result, dict):
            return
        super().show_result(result)
        remaining = result.get("Liftdict")
        if isinstance(remaining, dict):
            self.lift_pool = dict(remaining)
        else:
            # 旧记忆没有 Liftdict 时，用完整名单减去本轮抽中者恢复。
            outdict = result.get("outdict", {})
            selected = set()
            if isinstance(outdict, dict):
                for value in outdict.values():
                    if isinstance(value, dict):
                        if "code" in value:
                            selected.add(value["code"])
                        elif len(value) == 1:
                            selected.add(next(iter(value)))
            self.lift_pool = {
                key: name for key, name in self.names.items() if key not in selected
            }
        self.round_available = len(self.lift_pool) + self.total


__all__ = ["ScrollLiftController"]
