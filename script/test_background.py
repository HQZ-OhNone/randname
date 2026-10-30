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

"""背景主题与窗口颜色辅助函数测试。"""

import unittest
from pathlib import Path

from PySide6.QtGui import QColor

from lib import ThemeManager
from lib.WindowTheme import apply_titlebar, colorref, is_dark
from lib.BackgroundWidget import contain_target_rect, cover_source_rect


class BackgroundGeometryTests(unittest.TestCase):
    def test_cover_landscape_crops_width(self):
        rect = cover_source_rect(4000, 2000, 1000, 1000)
        self.assertEqual(rect.height(), 2000)
        self.assertEqual(rect.width(), 2000)
        self.assertEqual(rect.x(), 1000)
        self.assertEqual(rect.y(), 0)

    def test_cover_portrait_crops_height(self):
        rect = cover_source_rect(2000, 4000, 1000, 1000)
        self.assertEqual(rect.width(), 2000)
        self.assertEqual(rect.height(), 2000)
        self.assertEqual(rect.x(), 0)
        self.assertEqual(rect.y(), 1000)

    def test_contain_centers_image(self):
        rect = contain_target_rect(400, 200, 1000, 1000)
        self.assertEqual(rect.width(), 1000)
        self.assertEqual(rect.height(), 500)
        self.assertEqual(rect.y(), 250)


class ThemeBackgroundTests(unittest.TestCase):
    def test_default_theme_has_no_background(self):
        themes = ThemeManager.discover_themes()
        self.assertIsNone(ThemeManager.background_config(themes["randname-dark"]))

    def test_example_theme_defaults_to_uniform_blur(self):
        themes = ThemeManager.discover_themes()
        config = ThemeManager.background_config(themes["randname-bg-light"])
        self.assertIsNotNone(config)
        self.assertEqual(config["blur_direction"], "uniform")
        self.assertGreater(config["blur_radius"], 0)
        self.assertEqual(config["fit_mode"], "cover")

    def test_background_defaults_and_clamps(self):
        config = ThemeManager.background_config({"background": {"image": "x.png"}})
        self.assertEqual(config["blur_radius"], ThemeManager.BACKGROUND_DEFAULTS["blur_radius"])
        config = ThemeManager.background_config({
            "background": {
                "image": "x.png",
                "blur_radius": 999,
                "blur_direction": "unknown",
                "opacity": -1,
                "fit_mode": "stretch",
            }
        })
        self.assertEqual(config["blur_radius"], 80.0)
        self.assertEqual(config["blur_direction"], "uniform")
        self.assertEqual(config["opacity"], 0.0)
        self.assertEqual(config["fit_mode"], "cover")

    def test_background_requires_image(self):
        self.assertIsNone(ThemeManager.background_config({"background": {}}))
        self.assertIsNone(ThemeManager.background_config({}))

    def test_relative_background_uses_ui_directory(self):
        path = ThemeManager.resolve_background_image("x.png")
        self.assertEqual(path, ThemeManager.ROOT / "ui" / "x.png")
        absolute = Path("/tmp/x.png")
        self.assertEqual(ThemeManager.resolve_background_image(str(absolute)), absolute)


class ThemeColumnTests(unittest.TestCase):
    def test_neutral_themes_removed(self):
        themes = ThemeManager.discover_themes()
        self.assertNotIn("light-dark", themes)
        self.assertNotIn("light-light", themes)

    def test_theme_is_split_into_dark_and_light(self):
        themes = ThemeManager.discover_themes()
        light = {key for key, theme in themes.items() if ThemeManager.is_light_theme(theme)}
        self.assertEqual(
            light,
            {"amber-light", "blue-light", "dark-light", "green-light",
             "purple-light", "randname-light", "randname-bg-light"},
        )
        self.assertNotIn("randname-dark", light)
        self.assertNotIn("amber-dark", light)

    def test_every_theme_defines_output_colors(self):
        themes = ThemeManager.discover_themes()
        for key, theme in themes.items():
            with self.subTest(theme=key):
                output = ThemeManager.output_config(theme)
                self.assertIn("background", output)
                self.assertIn("foreground", output)
                self.assertIn("border", output)
                for value in output.values():
                    self.assertTrue(value.startswith("#"))

    def test_dark_themes_keep_existing_display_color(self):
        themes = ThemeManager.discover_themes()
        for key, theme in themes.items():
            if ThemeManager.is_light_theme(theme):
                continue
            with self.subTest(theme=key):
                output = ThemeManager.output_config(theme)
                self.assertEqual(output["background"], "#141414FF")
                self.assertEqual(output["foreground"], "#FFFFFFFF")
                self.assertEqual(output["border"], "#4A90E2FF")

    def test_output_config_falls_back_to_legacy_keys(self):
        output = ThemeManager.output_config({
            "colors": {
                "display_background": "#112233FF",
                "display_foreground": "#445566FF",
                "display_border": "#778899FF",
            }
        })
        self.assertEqual(output["background"], "#112233FF")
        self.assertEqual(output["foreground"], "#445566FF")
        self.assertEqual(output["border"], "#778899FF")

    def test_theme_file_has_no_legacy_display_keys(self):
        text = (ThemeManager.ROOT / "config" / "theme.toml").read_text(encoding="utf-8")
        active = [line for line in text.splitlines() if not line.lstrip().startswith("#")]
        for key in ("display_background", "display_foreground", "display_border"):
            self.assertFalse(any(line.startswith(key) for line in active))

    def test_output_stylesheet_uses_theme_colors(self):
        themes = ThemeManager.discover_themes()
        dark = ThemeManager._stylesheet(themes["randname-dark"])
        self.assertIn("rgba(20, 20, 20, 1.000)", dark)
        self.assertIn("border: 2px solid", dark)
        light = ThemeManager._stylesheet(themes["randname-light"])
        self.assertNotIn("rgba(20, 20, 20, 1.000)", light)


class WindowThemeTests(unittest.TestCase):
    def test_colorref_is_bgr(self):
        self.assertEqual(colorref(QColor(1, 2, 3)), 0x00030201)

    def test_dark_detection(self):
        self.assertTrue(is_dark(QColor("#000000")))
        self.assertFalse(is_dark(QColor("#FFFFFF")))

    def test_invalid_window_is_noop(self):
        self.assertFalse(apply_titlebar(0, QColor("#000000")))


if __name__ == "__main__":
    unittest.main()
