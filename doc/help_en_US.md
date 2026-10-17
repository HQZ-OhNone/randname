# randname Help

randname is a desktop app for classroom roll calls. The Mode menu contains Single, Multi, Elimination, Rolling Single, Rolling Multi, and Rolling Elimination.

## Drawing

- **Single:** A shortcut that opens Multi and sets the quantity to `1`; it has no separate page.
- **Multi:** Set the quantity with the increase/decrease buttons, then select Draw. A draw contains no duplicate names; later draws start from the full roster again.
- **Elimination:** Each draw removes selected people from the remaining pool for the current run. Reset restores the active roster. Changing rosters or refreshing changed roster data also resets the remaining pool.
- **Rolling Single:** A shortcut that opens Rolling Multi and sets the quantity to `1`.
- **Rolling Multi:** Set the quantity, then select Draw to show that many reels cycling at once. The button becomes "Stop (x/n)"; each press stops the frontmost reel and fixes its name. Names fixed this round never appear again in the same round. The cycle rate is controlled by `scroll.rate`.
- **Rolling Elimination:** The rolling behaviour is the same as Rolling Multi, but names drawn this round are removed from the remaining pool. The Reset button restores the full roster. The rate is also controlled by `scroll.rate`.

The output box never changes the window size. Names are shown on one line when possible, wrapped onto multiple lines when there is enough height, and the font is reduced for the current draw when the box is already full. Every mode uses this rule.

## Rosters

Choose a roster from the Roster menu. Rosters are stored in `config/name.toml`; each roster has a stable key, localized display names, and a keyed list of people:

```toml
[rosters.class_1.name]
en_US = "Class 1"
zh_CN = "一班"
zh_TW = "一班"

[rosters.class_1.names]
"student-001" = "Alex Morgan"
"student-002" = "Taylor Chen"
```

Use a unique key for every person. Roster display names use the current interface language, the system language, English, then the roster key. If the main roster file is unavailable, randname tries `.name.default.toml` and then a built-in one-person roster.

## Language and Themes

Select a language from Language. Available language packs are listed in `config/language.toml`; English is built in and remains available if that file is missing. The `preferred` value selects the first-startup language. A legacy `app.language` in `config/config.toml` is only a fallback; `language.toml`'s `preferred` wins. Switching language applies immediately and does not discard the current draw result.

Themes are stored in `config/theme.toml`. Its `default` key selects the fallback theme. Theme names use the same current-language, system-language, English, key fallback order as roster names.

The memory file keeps only the theme, roster, log level, and window size from the last session; mode, language, and quantities return to the configuration defaults on every startup. Set `app.remember_preferences = false` in `config/config.toml` to stop remembering even the theme, roster, and log level (window size remains controlled by `[window].remember_size`).

## Window and Status Bar

The main window can be resized by dragging its edges. The resulting size is written to `doc/memory.json` and restored on the next startup; set `[window].remember_size = false` to disable this. Long names and memory imports never change the window size.

The left side of the status bar shows temporary messages such as "Multi complete"; the right side shows the current mode, roster, quantity, theme, language, log level, and version. Each item can be hidden in `[statusbar]`.

## Settings

Edit `config/config.toml` to set the startup mode, roster, splash screen, window size, output font sizes, rolling rate, viewer, status bar, and log level; the theme and language come from their dedicated `theme.toml` and `language.toml` files. Every option in the configuration file has an explanatory comment.

```toml
[window]
size_mode = "screen_ratio"   # or "fixed"
screen_ratio = 0.75          # initial size as a share of the available screen
aspect_ratio = 1.5
width = 1000
height = 600
resizable = true
remember_size = true

[scroll]
rate = 30

[splash]
enabled = true
mode = 1
duration_ms = 1000
screen_ratio = 0.25
```

In proportional mode the splash is constrained by `screen_ratio`, and the main window is calculated from `screen_ratio` and `aspect_ratio`. Splash mode `0` closes when the main window is ready; mode `1` keeps it visible for at least `duration_ms` and only then shows the main window, so the window cannot cover the splash. The current version is drawn in the bottom-right corner of the splash.

Use **File > Refresh application data** after editing configuration, rosters, language packs, or themes. The current mode, theme, language, roster, result, and status are retained when their selections remain valid. If a selected resource was removed, randname chooses an available fallback.

## Logs and Memory

Choose a threshold under **About > Log level**: Debug, Information, Warning, Error, or Critical. Records below the selected level are omitted. **About > Program log** opens `doc/log.log` read-only and refreshes automatically as the file changes, so it can be watched while the program runs.

File > Import memory and File > Export memory exchange recent results as JSON. They do not replace configuration or roster files. The runtime memory file is `doc/memory.json`.

Help, the license, and the program log all use randname's own read-only viewer. The viewer is clamped to the available desktop area so the taskbar remains accessible; it supports touch-drag scrolling, and its font size and refresh interval can be adjusted in `[viewer]`.

## Startup and Troubleshooting

The splash screen appears before data checks and window initialization. Missing configuration, roster, language, or theme files use their available backup or built-in data; randname reports these cases in the status bar and log without an extra dialog. Missing executable components stop startup and show a detailed error.

If a configured choice is unavailable after editing files, use **File > Refresh application data**. If the selected help translation is unavailable, the Help command opens this English document. **About > Feedback** contains GitHub Issues and Email; if no mail client can be opened, a dialog shows the email address.
