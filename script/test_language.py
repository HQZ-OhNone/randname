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

"""简体/繁体语言备援测试。"""

import tempfile
import unittest
from pathlib import Path

from lib.LanguageManager import (
    ENGLISH,
    SIBLING_LANGUAGES,
    load_languages,
    localized_name,
    resolve_language,
    translate,
)


def make_languages():
    return {
        "en_US": {
            "display_name": "English",
            "text": dict(ENGLISH),
            "own": dict(ENGLISH),
        },
        "zh_CN": {
            "display_name": "简体",
            "text": {**ENGLISH, "only.simple": "只有简体"},
            "own": {"only.simple": "只有简体"},
        },
        "zh_TW": {
            "display_name": "繁體",
            "text": {**ENGLISH, "only.traditional": "只有繁體"},
            "own": {"only.traditional": "只有繁體"},
        },
    }


class SiblingFallbackTests(unittest.TestCase):
    def test_missing_key_uses_sibling_language(self):
        languages = make_languages()
        self.assertEqual(
            translate(languages, "zh_CN", "only.traditional"), "只有繁體"
        )
        self.assertEqual(translate(languages, "zh_TW", "only.simple"), "只有简体")

    def test_unknown_key_falls_back_to_english(self):
        self.assertEqual(
            translate(make_languages(), "zh_CN", "menu.file"), ENGLISH["menu.file"]
        )

    def test_localized_name_uses_sibling(self):
        languages = make_languages()
        names = {"zh_TW": "繁體名"}
        self.assertEqual(localized_name(names, "zh_CN", languages), "繁體名")
        self.assertEqual(localized_name(names, "en_US", languages), "繁體名")

    def test_resolve_language_uses_sibling(self):
        languages = make_languages()
        del languages["zh_TW"]
        self.assertEqual(resolve_language("zh_TW", languages), "zh_CN")

    def test_missing_pack_is_synthesized(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "language.toml"
            path.write_text(
                'preferred = "zh_TW"\n'
                '[languages.zh_TW]\n'
                'display_name = "繁體中文"\n'
                '[languages.zh_TW.text]\n'
                '"menu.file" = "檔案"\n',
                encoding="utf-8",
            )
            languages, preferred, warning = load_languages(path)
        self.assertEqual(preferred, "zh_TW")
        self.assertIsNone(warning)
        self.assertIn("zh_CN", languages)
        self.assertEqual(languages["zh_CN"]["fallback_from"], "zh_TW")
        self.assertEqual(translate(languages, "zh_CN", "menu.file"), "檔案")
        self.assertIn("zh_CN", SIBLING_LANGUAGES)

    def test_missing_pack_keeps_english(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "language.toml"
            path.write_text('[languages.en_US]\ndisplay_name = "English"\n', encoding="utf-8")
            languages, _, _ = load_languages(path)
        self.assertEqual(resolve_language("zh_CN", languages), "en_US")
        self.assertEqual(translate(languages, "zh_CN", "menu.file"), "File")


if __name__ == "__main__":
    unittest.main()
