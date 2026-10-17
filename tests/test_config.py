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

    def test_splash_wait_respects_mode_and_duration(self):
        self.assertEqual(main._splash_wait_ms(0, 4000, 500), 0)
        self.assertEqual(main._splash_wait_ms(1, 4000, 500), 3500)
        self.assertEqual(main._splash_wait_ms(1, 4000, 4500), 0)
        self.assertEqual(main._splash_wait_ms("fixed", 1000, 1000), 0)

    def test_splash_version_pixel_size_scales_with_width(self):
        self.assertEqual(main._splash_version_pixel_size(300, 333), 111)
        self.assertEqual(main._splash_version_pixel_size(300, 500), 167)
        self.assertEqual(main._splash_version_pixel_size(300, 333, 50), 56)

    def test_splash_version_pixel_size_rejects_invalid_values(self):
        self.assertEqual(main._splash_version_pixel_size(0, 333), 1)
        self.assertEqual(main._splash_version_pixel_size(300, 0), 1)
        self.assertEqual(main._splash_version_pixel_size(-1, 333), 1)

    def test_startup_preferences_keep_only_remembered_items(self):
        all_preferences = {
            "theme": "randname-dark",
            "language": "zh_CN",
            "roster": "class_1",
            "mode": "Lift",
            "log_level": "DEBUG",
            "quantities": {"multi": 4},
            "window": {"width": 1000, "height": 700, "maximized": False},
        }
        preferences = main._startup_preferences(all_preferences, True)
        self.assertEqual(preferences["theme"], "randname-dark")
        self.assertEqual(preferences["roster"], "class_1")
        self.assertEqual(preferences["log_level"], "DEBUG")
        self.assertEqual(preferences["window"]["width"], 1000)
        self.assertNotIn("language", preferences)
        self.assertNotIn("mode", preferences)
        self.assertNotIn("quantities", preferences)

    def test_startup_preferences_master_switch(self):
        preferences = main._startup_preferences(
            {"theme": "randname-dark", "window": {"width": 1, "height": 1}}, False
        )
        self.assertNotIn("theme", preferences)
        self.assertIn("window", preferences)


if __name__ == "__main__":
    unittest.main()
