# randname Business Logic (English)

Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; see the GNU General Public License for more details.

This document records the actual behaviour, hidden mechanisms, and edge cases
of randname 3.10.3. Simplified Chinese: `logic_zh_CN.md`. Traditional Chinese:
`logic_zh_TW.md`.

## 1. Terms and modes

| Internal ID | English UI | Simplified Chinese | Traditional Chinese | Page |
| --- | --- | --- | --- | --- |
| `Multi` | Multi | 多抽 | 多抽 | Multi page |
| `Single` | Single | 单抽 | 單抽 | Multi page (quantity 1) |
| `Lift` | Lift | 减量抽 | 減量抽 | Lift page |
| `ScrollMulti` | ScrollMulti | 滚动多抽 | 滾動多抽 | ScrollMulti page |
| `ScrollSingle` | ScrollSingle | 滚动单抽 | 滾動單抽 | ScrollMulti page (quantity 1) |
| `ScrollLift` | ScrollLift | 滚动减量抽 | 滾動減量抽 | ScrollLift page |

- Single and ScrollSingle are menu shortcuts only. They do not create a
  separate page or controller.
- Result/log/memory `mode` fields still use `Multi`, `Lift`, `ScrollMulti`, and
  `ScrollLift`.
- User-visible text never exposes raw internal identifiers such as `ScrollMulti`.

## 2. Files

| Path | Responsibility |
| --- | --- |
| `main.py` | Startup, main window, menus, status bar, page switching, memory restore |
| `lib/version.py` | `APP_VERSION = "3.10.3"` |
| `lib/Multi.py` | Multi draw algorithm |
| `lib/Lift.py` | Lift draw algorithm |
| `lib/ScrollMulti.py` | ScrollMulti controller |
| `lib/ScrollLift.py` | ScrollLift controller (extends ScrollMultiController) |
| `lib/OutputView.py` | Auto-fit output; fixed-slot `SlotOutputView` for rolling modes |
| `lib/TextViewer.py` | Read-only live viewer for help, license, and logs |
| `lib/UpdateDialog.py` | Update dialog, GitHub Releases request, version comparison |
| `lib/StateManager.py` | Configuration, memory results, logging |
| `lib/importnames.py` | Roster loading |
| `lib/ThemeManager.py` | Theme loading and QSS |
| `lib/BackgroundWidget.py` | Theme background image, fitting, gradient blur, shadows |
| `lib/WindowTheme.py` | Windows title-bar colours |
| `lib/LanguageManager.py` | Language packs and fallbacks |
| `ui/*.ui` | Qt Designer sources |
| `lib/ui_*.py` | `pyside6-uic` output; regenerated before builds |
| `config/*.toml` | Configuration, roster, theme, language |
| `doc/memory.json` | Recent results per mode (export/import only) |
| `doc/log.log` | Persistent log |

## 3. Startup

1. Print the GPL banner.
2. Create `QApplication`.
3. `_bootstrap_config()` reads `config/config.toml`, then
   `.config.default.toml`, then the built-in configuration.
4. Load the icon and create the splash screen.
5. Scale the splash according to `[splash]`, keeping the image aspect ratio.
6. `_draw_splash_version()` draws `v3.10.3` in the bottom-right corner. The
   font size always scales with the image width to one third of that width;
   the text is always pure white and has no size or colour configuration.
7. `_startup_file_check()` collects recoverable-file warnings. `required` is
   currently always empty, so the fatal startup-check branch is unreachable.
8. Import `lib` modules.
9. Asset, help, license, log, and memory paths are fixed in code; there is no
   configurable path section.
10. Memory preferences are not read; every startup reads the configuration and
    dedicated theme/language files.
11. Log level: `[logging].level` > `INFO`; it controls file writes only.
12. Theme: `theme.toml` `default` > `config.toml` `app.theme` (legacy) >
    first theme.
13. Language: `language.toml` `preferred` > `config.toml` `app.language`
    (legacy) > system language > `en_US`.
14. Roster: `config.toml` `app.roster` > first roster.
15. Mode: `config.toml` `app.default_mode` > `Multi`; quantities start at 1.
16. Create `MainWindow` and apply the theme; whether the window is shown
    immediately depends on `[splash].mode`.
17. With `[splash].mode = 1`, only the splash is shown until the remaining time
    elapses, then the main window appears and the splash closes. Other modes
    show the window and close the splash as soon as the window is ready.

## 4. Configuration precedence

Theme:

```
theme.toml default (valid)
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

- Roster: `[app].roster` > first roster.
- Mode: `[app].default_mode` > `Multi`.
- Log level: `[logging].level` > `INFO`.
- Quantities: always start from 1.
- Window: `[window]` computes the initial size on every startup; no remembered
  size is read.

Startup never restores the theme, roster, log level, mode, language, quantity,
or window size from the memory file.

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

With `size_mode = "maximum"`, `_window_is_maximized()` skips this calculation,
applies only a minimum size, and `reveal_window()` calls `showMaximized()`. A
reload also maximises a visible window.

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
- The resized size is not saved; the next startup uses the configured initial
  size again.
- Refresh application data keeps the current window size.

### Status bar

- The left side shows temporary `showMessage()` text.
- The right side permanently shows mode, roster, quantity, theme, language,
  log level, and version, separated by `|`.
- `[statusbar].show_*` controls each item.
- `_update_status_info()` runs after mode, roster, quantity, theme, language,
  log-level, or configuration changes.
- The version comes from `lib/version.py`.

## 6. Output auto-fit

### 6.1 Non-rolling modes (OutputView)

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
6. `set_message()` is used for "Ready", "No result", etc. and always uses the
   base font.
7. `resizeEvent` re-runs layout, so user resizing is handled.

### 6.2 Rolling modes (SlotOutputView)

`SlotOutputView` reuses the original output `QLabel` as a background container
and places child `QLabel`s with `_SlotGrid`:

1. `begin_round(pool, quantity)` creates `quantity` fixed slots.
2. The first `set_names()` computes and locks the layout. The target row count
   is estimated as `round(sqrt(N * H / W))`; every column count is compared,
   preferring the largest font and, on a tie, the layout closest to the target
   row count. Six names in a wide box usually become 2 rows × 3 columns.
3. Cells are equal-sized and centre their text horizontally and vertically;
   an incomplete last row is centred as a row.
4. After locking, every tick only changes text. Slot geometry is stable, so
   names already fixed do not move.
5. If a current name cannot fit its locked slot, the column/row/font
   calculation runs again and the new layout is locked.
6. `clear_round()`, the next `start()`, a quantity change, reset, or result
   import clears the lock so the next draw re-lays out.
7. Imported results create slots from the result count and lock one layout.
8. ScrollMulti and ScrollLift share this view.

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

## 8. Lift

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

## 9. ScrollMulti

`ScrollMultiController`:

- Copies the roster; `quantity` defaults to 1; timer interval is
  `max(1, 1000 // rate)`.
- `start()`:
  1. Warn and return when the roster is empty.
  2. `total = min(quantity, len(names))`; warn when the requested count is
     larger.
  3. `pool = dict(names)` for this round.
  4. Create `total` reels, each with its own random order and index.
  5. Call `view.begin_round(pool.values(), total)` to create fixed slots; the
     first tick locks this round's layout and font size.
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
  timer interval; `set_quantity()` clears the layout lock while idle so the
  next round re-lays out.

## 10. ScrollLift

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

## 11. Single and ScrollSingle aliases

- Mode > Single calls `_show_single_page()`: set Multi quantity to 1, update
  the label, and switch to the Multi page.
- Mode > ScrollSingle calls `_show_scroll_single_page()`: set ScrollMulti
  quantity to 1, update the controller, and switch to the ScrollMulti page.
- `default_mode` compatibility: `Single` → Multi quantity 1;
  `ScrollSingle` → ScrollMulti quantity 1; any invalid value → Multi.
- No `Single.py`, `ScrollSingle.py`, `WidgetScrollSingle.ui`, or separate page
  exists.

## 12. Memory file

```json
{
  "last_results": {
    "Multi": null,
    "Lift": null,
    "ScrollMulti": null,
    "ScrollLift": null
  }
}
```

- The memory file stores only each mode's most recent result. It no longer
  stores theme, roster, mode, language, log level, quantities, or window size.
- Runtime result entries are usually `{"result": ..., "meta": ...}`; Multi and
  Lift use `{"result": ..., "time": ...}`.
- JSON is written as UTF-8 with `ensure_ascii=False, indent=2`.
- `save_memory()` writes a `.tmp` file and replaces the target atomically.
- `_normalize_memory()` keeps only `last_results` and drops legacy
  `preferences` and `loaded_config`.
- Legacy `ScrollSingle` entries are ignored.
- Draw results are saved after each completed draw/round.
- Theme, roster, language, log-level, mode, quantity, and window-size changes
  are never written to the memory file.
- Import/export never writes to `config/` or changes the current interface
  state.
- Importing an old memory file restores only `last_results`; its `preferences`
  and `loaded_config` are ignored.
- A corrupt memory file falls back to the result-only default structure and
  does not block startup.

## 13. Logging

- `StateManager.configure_logging()` sets the root logger to DEBUG and installs
  `_SessionLogHandler`.
- The handler always stores Python log records in `SESSION_LOG_RECORDS`, then
  writes only records at or above the selected level to `doc/log.log`.
- `StateManager.log()` writes concise single-line records:

```
time=2026-10-18 12:00:00 level=INFO action=Multi result=(...)
```

- Field order: `time` → `level` → `action` → `result` → `error`.
- `StateManager.log()` also appends to `SESSION_LOG_RECORDS` before the file
  level check, so the program log window always shows the full current session.
- The log viewer renders the session buffer as HTML and colours the
  `level=...` or `[INFO]` tag at the start of each line.
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

- `language.toml` `preferred` is the first-startup language; legacy
  `app.language` is only a fallback.
- `LanguageManager.ENGLISH` is the built-in fallback.
- Missing translation keys fall back to English, then the key itself.
- Placeholders such as `{count}` and `{name}` must be preserved.
- Switching language refreshes menus, buttons, placeholders, and the status bar
  immediately; current results are kept.

## 16. UI and menus

- Main window: `ui/Main.ui` → `lib/ui_main.py`.
- Pages: Multi, Lift, ScrollMulti, ScrollLift.
- Every quantity page has a vertical `QSlider` to the right of the quantity
  column. `_prepare_quantity_slider()` installs the touch filter, and
  `_set_quantity()` synchronises value, label, slider, and rolling controller.
- Text viewer: `ui/TextViewer.ui`; update dialog: `ui/Update.ui`.
- Mode menu order: Single, Multi, Lift, separator, ScrollSingle,
  ScrollMulti, ScrollLift.
- About menu: Help, Program log, Check for updates, Log level, separator,
  License, Source repository, Feedback.
- Repository and feedback URLs are hard-coded in `main.py`
  (`REPOSITORY_URL`, `FEEDBACK_URL`); they are not configuration options.
- Mode actions are not in a `QActionGroup`; `current_mode` and the visible page
  are authoritative.

## 17. Build and release

1. Compile every `ui/*.ui` with `pyside6-uic`, lowercasing the name into
   `lib/ui_<name>.py`. New `.ui` files need no build-script change.
2. Nuitka includes `ui/randname1.png`, `ui/randname-start.png`,
   `.config.default.toml`, `.name.default.toml`, `config/`, and `doc/`.
3. Removed files: `WidgetScrollSingle.ui`, `ui_widgetscrollsingle.py`,
   `ScrollSingle.py`, `randname-start_v3.6.png`, `randname-start_v3.7.png`.
4. Version lives in `lib/version.py`; use `3.10.1[upgrade]_...` in the commit
   message to trigger the release workflow. Update checks use QtNetwork, so
   `PySide6.QtNetwork` is no longer excluded.

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

### Lift

- Quantity upper bound is the full roster size, not the remaining size. If too
  many remain unavailable, the draw returns an empty `outdict` and the UI shows
  "No result"; reduce the quantity or reset.
- `quantity.Lift` means "remaining after this round", not "already lifted".
- Importing memory does not restore `lift_current_dict`.

### Memory

- The memory file stores only `last_results`; legacy `preferences` and
  `loaded_config` are dropped on load.
- Import never writes `config/`, never changes the roster, and does not change
  the current interface state.
- Corrupt memory falls back to a result-only default without blocking startup.
- `save_memory()` uses atomic replacement; do not write `memory.json` directly.
- Legacy `ScrollSingle` entries are ignored.

### Logs and viewer

- The log path is shared between the writer and viewer.
- The viewer closes with the main window.
- If the file is deleted, the viewer shows "No log entries" and keeps watching
  the parent directory.
- Touch behaviour depends on platform; verify on real hardware.

### Security

- Network access is limited to the user-triggered update check and repository/feedback links.
- No secrets, tokens, telemetry, or uploads.
- `config/` is read-only; only the configured memory and log files are written.
- `doc/memory.json` and `doc/log.log` are git-ignored.

## 19. Tests

- `script/test_output_fit.py`: non-rolling wrapping/shrinking; fixed rolling
  slots, stable geometry, long-name re-layout, and layout reset.
- `script/test_memory.py`: result-only storage, legacy preference removal, and
  import/export.
- `script/test_scroll_lift.py`: remaining pool, one-by-one stops, reset, and
  quantity clamping.
- `script/test_config.py`: configuration compatibility, invalid-value fallback,
  splash wait, version font sizing, maximum mode, and quantity clamping.
- `script/test_update.py`: version parsing and newer-version comparison.

Run: `QT_QPA_PLATFORM=offscreen python -m unittest discover -s script -p 'test_*.py'`.

## 20. Version

Current version: **3.10.3**.

Main changes in the 3.8.x series:

- Fixed rolling-multi window flicker.
- Fixed memory-import window widening and raw dictionary output.
- Shared auto-fit output across all modes.
- Resizable window with a configured startup size.
- Expanded status bar.
- Single / ScrollSingle aliases.
- New ScrollLift mode.
- Live read-only text viewer.
- New splash image with dynamic version.
- Documented, simplified configuration.
- Multilingual business-logic documentation.
- Splash version scaled to one third of the image width and rendered pure white.

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
- Startup language comes from `language.toml` `preferred`, mode from
  `[app].default_mode`, and quantities start at 1.
- Version is now `3.8.2`.

## 23. 3.8.3 additions

- `_draw_splash_version()` now scales automatically from the image width: a
  100px probe font measures the width of `v3.8.3`, then the actual pixel size
  is derived from the target width (one third of the image width).
  `_splash_version_pixel_size()` performs the conversion and falls back to 1px
  for invalid input.
- The font size now follows the splash scale exactly, with no fixed size and no
  minimum-size jump.
- The version text is always pure white `#FFFFFF`; the translucent black shadow
  remains for contrast.
- Removed `[splash].version_font_size` and `[splash].version_color`; those keys
  are ignored in older configuration files.
- Margins and shadow offset scale with the image to keep placement consistent
  at different resolutions.
- Version is now `3.8.3`.

## 24. 3.8.4 additions

- Removed memory-based configuration: startup no longer reads remembered
  theme, roster, log level, mode, language, quantity, or window size.
- Theme comes from `theme.toml` `default`; language from `language.toml`
  `preferred`; roster, mode, log level, and window size from `config.toml`;
  quantities start at 1.
- Removed `[app].remember_preferences` and `[window].remember_size`, including
  debounced window-size saving, close-time saving, and startup restore.
- The memory file now stores only `last_results`; legacy `preferences` and
  `loaded_config` are ignored on load/import and omitted from exports.
- Added `SlotOutputView`, `_SlotGrid`, and `choose_slot_layout()` to
  `lib/OutputView.py`.
- ScrollMulti and ScrollLift now use fixed slots. The first draw decides the
  positions; ticks only change text; an overlong name re-lays out and locks the
  new layout.
- The next draw, a quantity change, reset, or result import clears the layout
  lock.
- Added tests for fixed-slot layout, stable positions, long-name re-layout, and
  result-only memory import/export.
- Version is now `3.8.4`.

## 25. 3.9.1 additions

- Raised the output-label `.ui` font size from 30 to 33 and regenerated all
  four `lib/ui_*.py` files.
- Synchronized `[ui].display_font_size` to 33 and changed `BUILTIN_CONFIG`
  and the `OutputView` fallback to 33 so the runtime actually uses it.
- Added `tests/` to `.gitignore` and untracked it in the new commit while
  keeping local test files; history is unchanged.
- Version is now `3.9.1`.

## 26. 3.9.3 additions

- Update button is enabled only when a newer release exists; a Manual check
  button opens the Releases page without closing the dialog.
- `[update].timeout_ms` (default 15000) controls the GitHub request timeout;
  screen lookup and `QByteArray` handling are type-safe.
- Name spacing is compact; rolling grids are capped by content and centred on
  large screens.
- Removed `[assets]` and `[paths]`; all asset/document paths are constants.
- Log level filters file output only; the program log viewer shows the whole
  current session with coloured level tags.
- Canonical mode names and identifiers: Multi, ScrollMulti, ScrollSingle,
  Single, Lift, ScrollLift.
- Version bumped to 3.9.3.

## 27. 3.9.2 additions

- Added `[window].size_mode = "maximum"`; `_window_is_maximized()` skips size calculation and `reveal_window()` uses `showMaximized()`.
- Added a vertical quantity slider beside the quantity column on all four pages. `_QuantitySliderTouchFilter` maps touch positions to values, and `_set_quantity()` synchronises value, label, slider range, and rolling controller.
- `_refresh_quantity_ranges()` clamps and synchronises all four quantities after roster changes or configuration reloads.
- Added `lib/UpdateDialog.py` using an asynchronous `QNetworkAccessManager` request to GitHub Releases. `parse_version()` and `is_newer_version()` compare tags; closing aborts a pending request.
- Added `ui/Update.ui` and `ui/TextViewer.ui`; the viewer now loads its `.ui`. Build scripts and CI compile every `ui/*.ui`.
- QtNetwork is no longer excluded from any build configuration.
- Added trilingual update texts; help, README, and history are updated to 3.9.2.
- Added maximum-mode, quantity-clamping, and version-comparison tests.

## 28. 3.9.4 additions

- `UpdateDialog` now parses GitHub responses with `QJsonDocument.fromJson()`/`toVariant()`, removing the `memoryview.decode` type warning caused by `QByteArray.data()`.
- Removed `json`, `re`, `QFont`, and the unused `Qt`; `parse_version()` uses a manual digit scanner and the font uses a copy of the existing `QFont`.
- Cached the GitHub API and Releases `QUrl` objects; update-button gating, manual check, and timeout behaviour are unchanged.
- A project-wide AST scan found no other unused imports.
- Version bumped to 3.9.4.

## 29. 3.10.0 release notes

- Merged the accumulated 3.9.2–3.9.4 changes into `main` and triggered the GitHub Actions release with `3.10.0[upgrade]`.
- This release includes quantity sliders, maximum startup, the update checker, compact name layout, fixed asset/document paths, full-session highlighted logs, and canonical mode names.
- Version bumped to 3.10.0.

## 30. 3.10.1 CI maintenance

- The previous 3.10.0 build annotations contained only Node.js 20 deprecation warnings and the `ubuntu-latest` migration notice.
- All official actions were upgraded to node24 releases: checkout v7.0.1, setup-python v7.1.0, cache v6.1.0, upload-artifact v7.0.2, download-artifact v8.0.2, and action-gh-release v3.0.3.
- Ubuntu jobs are pinned to `ubuntu-24.04` to avoid the Ubuntu 26.04 migration from October to November 2026.
- The commit message is passed to shell steps through the `COMMIT_MSG` environment variable, avoiding expression interpolation and script-injection risk.
- `actionlint v1.7.12` reports no issues. Version bumped to 3.10.1 with no `[upgrade]` tag, so no release is triggered.

## 31. 3.10.2 structural changes

- Build scripts moved to `script/build.sh` and `script/build.bat`; both return to the repository root automatically.
- The six unit-test files moved to `script/` and run with `.venv/bin/python -m unittest discover -s script -p 'test_*.py'`; the unreferenced `tests/config_49/` was removed.
- Added `doc/project-manifest.json` as the machine-readable index; consult it first, then read only the needed files.
- Added `script/last-history-reader.sh`, which writes history summaries to `/tmp`; `doc/releasenote.md` is read only by CI and release tooling.
- GitHub Release bodies are extracted from the matching version section in `doc/releasenote.md`, with a fallback body when absent.
- Version bumped to 3.10.2.

## 32. 3.10.3 additions

- Themes may define `[themes.<key>.background]`. `BackgroundWidget` paints the central content area and supports `cover`, `contain`, `center`, and `tile`; `blur_direction` accepts `uniform`, `horizontal`, `vertical`, `diagonal`, `center-out`, and `out-center`. A missing `blur_radius` defaults to 24, giving a uniformly blurred image. Relative `image` paths resolve under `ui/`.
- The default `randname-dark` theme has no background table, so its appearance is unchanged. The new `randname-bg-light` example theme uses `ui/background-example.png`.
- The image covers only the central content area. The menu bar and status bar keep their theme background and receive a gradient shadow drawn by the background layer.
- In fixed-size mode, if the configured width or height exceeds the available screen, `_fixed_size_exceeds_screen()` temporarily maximises the window without rewriting the configuration; restoring uses an on-screen size.
- **File > Initialize** calls `StateManager.reset_memory()`, returns all four modes to quantity 1, clears results and rolling pools, and clears Qt pixmap caches. Logs are preserved, and the initialization itself is written as an `initialize` log entry.
- Fixed the Multi and Lift quantity sliders: `_prepare_quantity_slider()` passed lowercase `"multi"`/`"lift"` while `_set_quantity()` expects the canonical mode constants, so dragging had no effect.
- `WindowTheme.apply_titlebar()` sets the Windows title bar through DWM: Windows 11 uses caption/text/border colors and Windows 10 falls back to immersive dark mode; non-Windows platforms are a no-op.
- Added `ui/background-example.png` and `script/make_background_example.py`; the build scripts and CI package the new image. Test count is 54.
- Version bumped to 3.10.3.
