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

"""基础配置辅助函数测试。"""

import unittest

import main


class ConfigHelperTests(unittest.TestCase):
    def test_fixed_size(self):
        width, height = main._configured_size({"size_mode": "fixed", "width": 800, "height": 600}, 1920, 1080)
        self.assertEqual((width, height), (800, 600))

    def test_ratio_size_respects_aspect(self):
        width, height = main._configured_size(
            {"size_mode": "screen_ratio", "screen_ratio": 0.5, "aspect_ratio": 2.0},
            1600,
            900,
        )
        self.assertEqual(width, 800)
        self.assertEqual(height, 400)

    def test_rate_uses_scroll_section(self):
        self.assertEqual(main._rate_from_config({"scroll": {"rate": 45}}), 45)

    def test_rate_accepts_legacy_section(self):
        self.assertEqual(main._rate_from_config({"scroll_multi": {"rate": 12}}), 12)

    def test_mode_aliases(self):
        self.assertEqual(main.MainWindow._normalize_mode("Single"), ("Multi", 1))
        self.assertEqual(main.MainWindow._normalize_mode("ScrollSingle"), ("ScrollMulti", 1))
        self.assertEqual(main.MainWindow._normalize_mode("ScrollLift"), ("ScrollLift", None))
        self.assertEqual(main.MainWindow._normalize_mode("unknown"), ("Multi", None))

    def test_feedback_targets_are_hardcoded(self):
        self.assertEqual(main.EMAIL_ADDRESS, "ohnone_hqz@outlook.com")
        self.assertTrue(main.FEEDBACK_URL.endswith("/issues"))


if __name__ == "__main__":
    unittest.main()
