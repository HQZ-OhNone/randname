# randname Business Logic (English)

Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; see the GNU General Public License for more details.

This document records the actual behaviour, hidden mechanisms, and edge cases
of randname 3.8.2. Simplified Chinese: `logic_zh_CN.md`. Traditional Chinese:
`logic_zh_TW.md`.

## 1. Terms and modes

| Internal ID | English UI | Simplified Chinese | Traditional Chinese | Page |
| --- | --- | --- | --- | --- |
| `Multi` | Multi | 多抽 | 多抽 | Multi page |
| `Single` | Single | 单抽 | 單抽 | Multi page (quantity 1) |
| `Lift` | Elimination | 减量抽 | 減量抽 | Elimination page |
| `ScrollMulti` | Rolling Multi | 滚动多抽 | 滾動多抽 | Rolling Multi page |
| `ScrollSingle` | Rolling Single | 滚动单抽 | 滾動單抽 | Rolling Multi page (quantity 1) |
| `ScrollLift` | Rolling Elimination | 滚动减量抽 | 滾動減量抽 | Rolling Elimination page |

- Single and Rolling Single are menu shortcuts only. They do not create a
  separate page or controller.
- Result/log/memory `mode` fields still use `Multi`, `Lift`, `ScrollMulti`, and
  `ScrollLift`.
- User-visible text never exposes raw internal identifiers such as `ScrollMulti`.

## 2. Files

| Path | Responsibility |
| --- | --- |
| `main.py` | Startup, main window, menus, status bar, page switching, memory restore |
| `lib/version.py` | `APP_VERSION = "3.8.2"` |
| `lib/Multi.py` | Multi draw algorithm |
| `lib/Lift.py` | Elimination draw algorithm |
| `lib/ScrollMulti.py` | Rolling Multi controller |
| `lib/ScrollLift.py` | Rolling Elimination controller (extends ScrollMultiController) |
| `lib/OutputView.py` | Single-line / multi-line / shrink-to-fit output |
| `lib/TextViewer.py` | Read-only live viewer for help, license, and logs |
| `lib/StateManager.py` | Configuration, memory, preferences, logging |
| `lib/importnames.py` | Roster loading |
| `lib/ThemeManager.py` | Theme loading and QSS |
| `lib/LanguageManager.py` | Language packs and fallbacks |
| `ui/*.ui` | Qt Designer sources |
| `lib/ui_*.py` | `pyside6-uic` output; regenerated before builds |
| `config/*.toml` | Configuration, roster, theme, language |
| `doc/memory.json` | Preferences, window size, recent results |
| `doc/log.log` | Persistent log |

## 3. Startup

1. Print the GPL banner.
2. Create `QApplication`.
3. `_bootstrap_config()` reads `config/config.toml`, then
   `.config.default.toml`, then the built-in configuration.
4. Load the icon and create the splash screen.
5. Scale the splash according to `[splash]`, keeping the image aspect ratio.
6. `_draw_splash_version()` draws `v3.8.2` in the bottom-right corner.
   `version_font_size = 0` selects an automatic size; `version_color` controls
   the text colour.
7. `_startup_file_check()` collects recoverable-file warnings. `required` is
   currently always empty, so the fatal startup-check branch is unreachable.
8. Import `lib` modules.
9. `StateManager.configure_paths()` applies `[paths]`.
10. Read the remembered theme, roster, and log level unless
    `[app].remember_preferences = false`. Window size is controlled separately
    by `[window].remember_size`.
11. Log level: remembered valid value > `[logging].level` > `INFO`.
12. Theme: remembered valid value > `theme.toml` `default` >
    `config.toml` `app.theme` > first theme.
13. Language: `language.toml` `preferred` > `config.toml` `app.language` >
    system language > `en_US`.
14. Roster: remembered valid value > `config.toml` `app.roster` > first roster.
15. Mode: `config.toml` `app.default_mode` > `Multi`.
16. Create `MainWindow` and apply the theme; whether the window is shown
    immediately depends on `[splash].mode`.
17. With `[splash].mode = 1`, only the splash is shown until the remaining time
    elapses, then the main window appears and the splash closes. Other modes
    show the window and close the splash as soon as the window is ready.

## 4. Configuration precedence

Theme:

```
memory preferences.theme (valid)
  > theme.toml default (valid)
  > config.toml [app].theme (legacy)
  > first theme
```

Language:

```
language.toml preferred (valid)
  > config.toml [app].language (legacy)
  > system language
  > en_US
```

Other values:

- Roster: memory `preferences.roster` > `[app].roster` > first roster.
- Mode: `[app].default_mode` > `Multi` (memory is not read).
- Log level: memory `preferences.log_level` > `[logging].level` > `INFO`.
- Quantities: always start from 1 (memory is not read).
- Window: `[window]` computes the initial size; a valid remembered size
  overrides it when `remember_size = true`.

`[app].remember_preferences = false` ignores the remembered theme, roster, and
log level, but does not affect `[window].remember_size`.

`[app].remember_preferences = false` ignores application preferences at
startup. `[window].remember_size` is independent.

## 5. Window and status bar

### Initial size

`_configured_size(section, screen_width, screen_height)`:

1. If `size_mode = "fixed"` and `width`/`height` are positive, use them.
2. Otherwise read `screen_ratio` (default 0.75, clamped to 0.05–1.0) and
   `aspect_ratio` (default 1.5).
3. `width = screen_width * screen_ratio`.
4. `height = width / aspect_ratio`.
5. If `height > screen_height * screen_ratio`, set
   `height = screen_height * screen_ratio` and `width = height * aspect_ratio`.
6. Return integer sizes, at least 1.

The splash uses the same algorithm with `screen_ratio = 0.25` and
`aspect_ratio = 2.0` by default.

`[splash].mode` controls when the splash closes:

- `mode = 0`: show the main window and close the splash as soon as the window
  is ready.
- `mode = 1`: keep only the splash visible, then call `window.show()` and
  `splash.finish(window)` after `duration_ms - splash_timer.elapsed()`.
- Delaying the main window avoids Wayland: `QSplashScreen` cannot stay on top
  there, so an early main window would completely cover the splash.
- `_splash_wait_ms(mode, duration_ms, elapsed_ms)` computes the remaining
  milliseconds and returns 0 for every other mode.

### Resizing and persistence

- `resizable = true` allows edge dragging; minimum size is 640×480.
- `resizable = false` uses `setFixedSize()`.
- Content changes never resize the window.
- `resizeEvent` starts a 450 ms single-shot save timer.
- Window state changes (maximize/restore) also save.
- Closing the window saves again.
- When maximized, `normalGeometry()` is stored together with
  `maximized: true`; otherwise the current size and `maximized: false` are
  stored.
- Remembered sizes are clamped to the current available screen.
- Refresh application data keeps the current window size.

### Status bar

- The left side shows temporary `showMessage()` text.
- The right side permanently shows mode, roster, quantity, theme, language,
  log level, and version, separated by `|`.
- `[statusbar].show_*` controls each item.
- `_update_status_info()` runs after mode, roster, quantity, theme, language,
  log-level, or configuration changes.
- The version comes from `lib/version.py`.

## 6. Output auto-fit (all modes)

`lib/OutputView.py` wraps a `QLabel`:

1. `setSizePolicy(Ignored, Ignored)` and `setMinimumSize(0, 0)` prevent the
   label size hint from enlarging the window.
2. Base font: `[ui].display_font_size`; minimum:
   `display_min_font_size`; step: `display_font_step`; line spacing:
   `display_line_spacing`; padding: `display_padding`.
3. Names are packed greedily into lines by rendered width, separated by two
   spaces, never split in the middle of a name.
4. Try one line at the base size; if it does not fit and there is enough
   height, wrap to multiple lines; if it still does not fit, reduce the font.
5. If even the minimum font cannot fit one extreme name, Qt may wrap inside
   the name so that content remains visible.
6. Rolling modes call `begin_round(pool_names, quantity)`:
   - measure the `quantity` widest names in the pool;
   - compute and lock a font size that fits the worst case;
   - reuse the locked size for every tick in the round;
   - restore automatic sizing after the result/reset.
7. `set_message()` is used for "Ready", "No result", etc. and always uses the
   base font.
8. `resizeEvent` re-runs layout, so user resizing is handled.

## 7. Multi

`Multi.Multi(alllist, quantity)`:

1. If `quantity > len(alllist)`, return `outdict = {}`.
2. Otherwise sample without replacement from the full roster.
3. Re-index `outdict` as `"0"`, `"1"`, ... with
   `{"code": key, "name": name}`.
4. Time format: `%Y-%m-%d-%H:%M:%S`.
5. Every draw starts from the full roster.

Result:

```json
{
  "mode": "Multi",
  "quantity": {"total": 9, "selected": 3},
  "time": "2026-10-18-12:00:00",
  "outdict": {
    "0": {"code": "1", "name": "Alex"}
  }
}
```

## 8. Elimination

`Lift.Lift(alllist, Liftdict, quantity)`:

1. `Liftdict` is the current remaining pool. `MainWindow` passes the full
   roster on the first draw.
2. If `Liftdict` is empty or `quantity > len(Liftdict)`, return
   `outdict = {}` and the original `Liftdict`.
3. Otherwise sample without replacement; each `outdict` entry is a single-key
   object `{key: name}` (different from Multi).
4. `Liftdict` becomes the unselected remaining people.
5. Quantity fields:
   - `total`: full roster size;
   - `wasted`: `total - len(Liftdict before draw)`;
   - `selected`: number drawn this round;
   - `Lift`: `len(Liftdict before draw) - selected`, i.e. people remaining
     after this round (the name is easy to misread).
6. `alllist` references the full roster and is written to memory.
7. Reset clears `lift_current_dict`; the quantity stays unchanged.
8. Changing rosters or refreshing changed roster data clears the state.

## 9. Rolling Multi

`ScrollMultiController`:

- Copies the roster; `quantity` defaults to 1; timer interval is
  `max(1, 1000 // rate)`.
- `start()`:
  1. Warn and return when the roster is empty.
  2. `total = min(quantity, len(names))`; warn when the requested count is
     larger.
  3. `pool = dict(names)` for this round.
  4. Create `total` reels, each with its own random order and index.
  5. Call `view.begin_round(pool.values(), total)`.
  6. Tick immediately, then start the timer.
- `_tick()` advances each active reel, reshuffles exhausted orders, and
  guards against stale keys that were already fixed by an earlier stop.
- `stop_next()`:
  1. Pick the first active reel.
  2. Mark it inactive.
  3. If its current key was already taken, draw a fresh key from the remaining
     pool.
  4. Remove the key from the pool.
  5. Rebuild all active reel orders so fixed names cannot appear again.
  6. Refresh the view.
  7. Finish when no active reel remains.
- Button text: `Stop (remaining/total)` while running, `Draw` when idle.
- `_finish()` stops the timer, builds the result, restores the button, and calls
  `on_result(result, meta)`.
- Result: `mode = "ScrollMulti"`, hyphenated time,
  `quantity.total = len(names)`, `quantity.selected = total`, and `outdict`
  keyed by stop order. Codes are unique within the round.
- `show_result()` restores a remembered result without rolling.
- `update_names()` resets on roster changes; `update_rate()` only changes the
  interval.

## 10. Rolling Elimination

`ScrollLiftController` extends `ScrollMultiController` and adds a persistent
remaining pool:

- `lift_pool` starts as the full roster.
- `start()`:
  1. Warn and return when `lift_pool` is empty; the status bar shows
     "No names remain; reset to restore the roster".
  2. `available = len(lift_pool)`; `total = min(quantity, available)`.
  3. Store `round_available = available`.
  4. `pool = dict(lift_pool)`.
  5. Create reels, lock the font, and start the timer.
- Stop logic is inherited; fixed names are removed from `pool`.
- `_finish()` sets `lift_pool = dict(pool)` before the parent finish logic.
- Result:
  - `mode = "ScrollLift"`;
  - `quantity.total = len(names)`;
  - `quantity.wasted = total - round_available`;
  - `quantity.selected = total`;
  - `quantity.Lift = round_available - total`;
  - `outdict`: names drawn this round;
  - `alllist`: full roster;
  - `Liftdict`: remaining names after this round.
- `reset()` restores `lift_pool = dict(names)`, clears the output, and keeps
  the quantity.
- `show_result()` restores `Liftdict`; old memories without `Liftdict` are
  reconstructed by subtracting `outdict` codes from the full roster.
- Importing memory restores the result and remaining pool but does not switch
  the current theme/language.

## 11. Single and Rolling Single aliases

- Mode > Single calls `_show_single_page()`: set Multi quantity to 1, update
  the label, switch to the Multi page, save mode `Multi`.
- Mode > Rolling Single calls `_show_scrollsingle_page()`: set Rolling Multi
  quantity to 1, update the controller, switch to the Rolling Multi page, save
  mode `ScrollMulti`.
- `default_mode` compatibility: `Single` → Multi quantity 1;
  `ScrollSingle` → Rolling Multi quantity 1; any invalid value → Multi.
- No `Single.py`, `ScrollSingle.py`, `WidgetScrollSingle.ui`, or separate page
  exists.

## 12. Memory file

```json
{
  "preferences": {
    "theme": "randname-dark",
    "language": "en_US",
    "roster": "class_1",
    "mode": "ScrollMulti",
    "log_level": "INFO",
    "quantities": {
      "multi": 1,
      "lift": 1,
      "scroll_multi": 3,
      "scroll_lift": 1
    },
    "window": {"width": 1200, "height": 760, "maximized": false}
  },
  "last_results": {
    "Multi": null,
    "Lift": null,
    "ScrollMulti": null,
    "ScrollLift": null
  },
  "loaded_config": null
}
```

- Runtime result entries are usually `{"result": ..., "meta": ...}`; Multi and
  Elimination use `{"result": ..., "time": ...}`.
- JSON is written as UTF-8 with `ensure_ascii=False, indent=2`.
- `save_memory()` writes a `.tmp` file and replaces the target atomically.
- `_normalize_memory()` fills missing fields, discards invalid values, and
  supports the legacy `loaded_config`.
- Legacy `ScrollSingle` entries are ignored.
- Startup uses only `preferences.theme`, `preferences.roster`,
  `preferences.log_level`, and `preferences.window`; `language`, `mode`, and
  `quantities` are ignored even if an old memory file still contains them, and
  the program no longer updates those keys.
- Preferences are saved immediately after theme, roster, or log-level changes.
- Language, mode, and quantity changes are no longer persisted; the next
  startup uses `language.toml`, `[app].default_mode`, and 1 respectively.
- Window size is saved after a 450 ms debounce, on close, and on
  maximize/restore.
- Draw results are saved after each completed draw/round.
- Import/export never writes to `config/`.
- Import without `preferences` keeps the current preferences; imported
  preferences take effect on the next startup, not immediately.
- `remember_preferences = false` disables remembered theme, roster, and log
  level, but `remember_size` still works independently.

## 13. Logging

- `StateManager.configure_logging()` sets the root logger and installs
  `_SessionLogHandler`.
- The handler appends Python log records to `[paths].log_file` and stores them
  in `SESSION_LOG_RECORDS`.
- `StateManager.log()` writes concise single-line records:

```
time=2026-10-18 12:00:00 level=INFO action=Multi result=(...)
```

- Field order: `time` → `level` → `action` → `result` → `error`.
- `_log_value()` replaces newlines/tabs with spaces and `{}[]` with `()`, so
  every record stays on one line.
- Records below the current level are dropped.
- About > Program log reads the log file, not only the in-memory session list.
- The viewer polls file modification time/size every `[viewer].refresh_ms`.

## 14. Internal text viewer

`lib/TextViewer.py`:

- Help/license: `QTextBrowser` + `setMarkdown()`.
- Log: `QPlainTextEdit` + `setPlainText()`.
- Read-only; undo/redo disabled.
- Non-modal, so the main program can keep running.
- `QFileSystemWatcher` watches the file and parent directory; a `QTimer`
  provides a fallback.
- Scroll position is preserved; if the user was at the bottom, the viewer
  follows new content; if the user scrolled up, it does not jump.
- Size: based on the parent screen's `availableGeometry()`; at most
  `max_screen_ratio` of the available area minus 24 px margins, capped at
  900×680, and shrunk on small screens.
- Touch: `QScroller` left-mouse gesture, 22 px scrollbars, 40 px close button.
- Reopening the same path activates the existing window.
- Help/license files refresh live when edited.

## 15. Themes and languages

### Themes

- `config/theme.toml` contains `default` and `[themes.<key>]`.
- Each theme has `color_format`, localized `name`, and `colors`.
- Supported formats: `HexA`, `Hex`, `RGBA`, `RGB`.
- `_stylesheet()` covers page/widget backgrounds, output labels by object name
  (`label_MultiOutput`, `label_LiftOutput`, `label_ScrollMultiOutput`,
  `label_ScrollLiftOutput`), buttons, menu selection, and the status bar.
- ID selectors override the inline `QLabel` element styles from `.ui` files.
- Theme names fall back through current language, system language, English,
  and the key.

### Languages

- `language.toml` `preferred` is the first-startup language; memory preferences
  win.
- `LanguageManager.ENGLISH` is the built-in fallback.
- Missing translation keys fall back to English, then the key itself.
- Placeholders such as `{count}` and `{name}` must be preserved.
- Switching language refreshes menus, buttons, placeholders, and the status bar
  immediately; current results are kept.

## 16. UI and menus

- Main window: `ui/Main.ui` → `lib/ui_main.py`.
- Pages: Multi, Elimination, Rolling Multi, Rolling Elimination.
- Mode menu order: Single, Multi, Elimination, separator, Rolling Single,
  Rolling Multi, Rolling Elimination.
- About menu: Help, Program log, Log level, separator, License, Source
  repository, Feedback.
- Repository and feedback URLs are hard-coded in `main.py`
  (`REPOSITORY_URL`, `FEEDBACK_URL`); they are not configuration options.
- Mode actions are not in a `QActionGroup`; `current_mode` and the visible page
  are authoritative.

## 17. Build and release

1. Compile with `pyside6-uic`:
   - `Main.ui` → `ui_main.py`
   - `WidgetMulti.ui` → `ui_widgetmulti.py`
   - `WidgetLift.ui` → `ui_widgetlift.py`
   - `WidgetScrollMulti.ui` → `ui_widgetscrollmulti.py`
   - `WidgetScrollLift.ui` → `ui_widgetscrolllift.py`
2. Nuitka includes `ui/randname1.png`, `ui/randname-start.png`,
   `.config.default.toml`, `.name.default.toml`, `config/`, and `doc/`.
3. Removed files: `WidgetScrollSingle.ui`, `ui_widgetscrollsingle.py`,
   `ScrollSingle.py`, `randname-start_v3.6.png`, `randname-start_v3.7.png`.
4. Version lives in `lib/version.py`; use `3.8.2[upgrade]_...` in the commit
   message to trigger the release workflow.

## 18. Hidden mechanisms and edge cases

### Output and window

- The `Ignored` size policy is essential; do not revert it to `Expanding`.
- `setMinimumSize(0, 0)` plus manual line packing prevents layout minimums
  from enlarging the window.
- Rolling modes lock the font size at round start to avoid jitter.
- Resizing the window re-runs layout; content never resizes the window.
- Extremely long names may still wrap inside a name at the minimum font.

### Rolling

- `ScrollMulti.pool` is per-round and rebuilt from the full roster on start.
- Fast clicks between ticks are handled by checking whether the displayed key
  is still available.
- Active reel orders are rebuilt after every stop so fixed names cannot repeat.
- `quantity.total` is the full roster size; `quantity.selected` is the actual
  count for the round.
- `ScrollLift.lift_pool` persists across rounds; `quantity.wasted` is the
  number eliminated before this round.
- An empty `ScrollLift` pool does not reset automatically; the user must press
  Reset.
- Importing a `ScrollLift` memory restores `Liftdict` so drawing can continue.

### Elimination

- Quantity upper bound is the full roster size, not the remaining size. If too
  many remain unavailable, the draw returns an empty `outdict` and the UI shows
  "No result"; reduce the quantity or reset.
- `quantity.Lift` means "remaining after this round", not "already lifted".
- Importing memory does not restore `lift_current_dict`.

### Memory

- `loaded_config` is a legacy configuration snapshot; new preferences use
  `preferences`.
- Import never writes `config/`, never changes the roster, and does not switch
  the current theme/language.
- Corrupt memory falls back to the default structure without blocking startup.
- `save_memory()` uses atomic replacement; do not write `memory.json` directly.
- Legacy `ScrollSingle` entries are ignored.

### Logs and viewer

- The log path is shared between the writer and viewer.
- The viewer closes with the main window.
- If the file is deleted, the viewer shows "No log entries" and keeps watching
  the parent directory.
- Touch behaviour depends on platform; verify on real hardware.

### Security

- No network access except user-initiated repository/feedback links.
- No secrets, tokens, telemetry, or uploads.
- `config/` is read-only; only the configured memory and log files are written.
- `doc/memory.json` and `doc/log.log` are git-ignored.

## 19. Tests

- `tests/test_output_fit.py`
- `tests/test_memory.py`
- `tests/test_scroll_lift.py`
- `tests/test_config.py` (including splash wait and preference filtering)

Run: `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests`.

## 20. Version

Current version: **3.8.2**.

Main changes in this release:

- Fixed rolling-multi window flicker.
- Fixed memory-import window widening and raw dictionary output.
- Shared auto-fit output across all modes.
- Resizable, persisted window size.
- Expanded status bar.
- Memory preferences and window size.
- Single / Rolling Single aliases.
- New Rolling Elimination mode.
- Live read-only text viewer.
- New splash image with dynamic version.
- Documented, simplified configuration.
- Multilingual business-logic documentation.

## 21. 3.8.1 additions

- `OutputView` now uses an `Expanding` size policy and preserves the 160
  horizontal stretch from the `.ui` file. The previous `Ignored` policy let the
  grid give most width to the left/right spacers, leaving the output box only a
  few dozen pixels wide.
- `OutputView` keeps `wordWrap = True`. Manual line packing is still performed by
  `pack_names()`; `wordWrap` only keeps `QLabel.minimumSizeHint()` small so long
  names cannot enlarge the window.
- The status bar is now a full-width `QWidget` container with a `QHBoxLayout`
  that left-aligns the temporary message and all information labels. It no
  longer uses `QStatusBar.showMessage()`, which would hide normal widgets.
- Temporary messages go through `_show_status_message()` into
  `status_message_label`; configuration refresh saves/restores that label text.
- About > Feedback is now a submenu:
  - `GitHub Issues`: opens `https://github.com/HQZ-OhNone/randname/issues`;
  - `Email`: opens the system mail client for `ohnone_hqz@outlook.com`;
  - if no mail client can be opened, an information dialog shows the address.
- `EMAIL_ADDRESS` is hard-coded in `main.py`, like the repository/feedback URLs.
- Version is now `3.8.1`.

## 22. 3.8.2 additions

- With `mode = 1`, the splash no longer shows the main window early;
  `reveal_window()` waits for the remaining time, then calls `window.show()`
  and closes the splash. This fixes the splash being completely covered by the
  main window and appearing to "flash by" on Wayland.
- Added `_splash_wait_ms()` to compute the remaining splash time; `mode = 0`
  and other modes return 0 and keep the close-as-soon-as-ready behaviour.
- Memory preferences now keep only theme, roster, log level, and window size.
  `_startup_preferences()` filters old memory on startup, and
  `_current_preferences()` no longer writes language, mode, or quantities.
- Startup language comes from `language.toml` `preferred`, mode from
  `[app].default_mode`, and quantities start at 1.
- Old `language`, `mode`, and `quantities` keys remain in the memory file but
  are ignored.
- Version is now `3.8.2`.
