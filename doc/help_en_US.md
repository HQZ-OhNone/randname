# randname Help

randname is a desktop app for classroom roll calls. The Mode menu contains Draw names, Elimination draw, and Rolling draw. Draw names accepts a quantity of one, so a separate single-draw mode is not needed.

## Drawing

- **Draw names:** Set the quantity with the increase/decrease buttons, then select Draw. A draw contains no duplicate names; later draws start from the full roster again. Set the quantity to `1` to draw one person.
- **Elimination draw:** Each draw removes selected people from the remaining pool for the current run. Reset restores the active roster. Changing rosters or refreshing changed roster data also resets the remaining pool.
- **Rolling draw:** Select Start to cycle through the active roster and Stop to choose the visible name. The cycle rate is controlled by `scroll_single.rate`.

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

Select a language from Language. Available language packs are listed in `config/language.toml`; English is built in and remains available if that file is missing. The `preferred` value selects the startup language. When it differs from `app.language` in `config/config.toml`, `language.toml`'s `preferred` wins (the `config.toml` value is used only when `preferred` is unset or invalid). Switching language applies immediately and does not discard the current draw result.

Themes are stored in `config/theme.toml`. Its `default` key selects the fallback theme. When it differs from `app.theme` in `config/config.toml`, `theme.toml`'s `default` wins (the `config.toml` value is used only when `default` is unset or invalid). Amber, Blue, Dark, Green, Light, and Purple each have `-dark` and `-light` variants, alongside Randname pink variants. Theme names use the same current-language, system-language, English, key fallback order as roster names.

## Settings

Edit `config/config.toml` to set the startup mode, roster, splash screen, window size, rolling rate, and log level; the theme and language come from their dedicated `theme.toml` and `language.toml` files. Proportional dimensions use `screen_ratio`; explicit dimensions use `fixed`.

```toml
[splash]
enabled = true
mode = 0
duration_ms = 1000
size_mode = "screen_ratio"
width = 480
height = 270

[window]
size_mode = "screen_ratio"
width = 800
height = 600
aspect_ratio = 1.5

[logging]
level = "INFO"
```

The proportional splash is constrained to one quarter of the screen width and height. The main window defaults to a 3:2 ratio and is constrained to three quarters of the screen width and height. Splash mode `0` closes when the main window is ready; mode `1` keeps it visible for `duration_ms`. Set `enabled = false` to disable it.

Use **File > Refresh application data** after editing configuration, rosters, language packs, or themes. The current mode, theme, language, roster, result, and status are retained when their selections remain valid. If a selected theme, language, or roster was removed, randname chooses an available fallback.

## Logs and Memory

Choose a threshold under **About > Log level**: Debug, Information, Warning, Error, or Critical. Records below the selected level are omitted. **About > Program log** displays all records captured since this process started. The persistent log is `doc/log.log`.

File > Import memory and File > Export memory exchange recent results as JSON. They do not replace configuration or roster files. The runtime memory file is `doc/memory.json`.

## Startup and Troubleshooting

The splash screen appears before data checks and window initialization. Missing configuration, roster, language, or theme files use their available backup or built-in data; randname reports these cases in the status bar and log without an extra dialog. Missing executable components stop startup and show a detailed error.

If a configured choice is unavailable after editing files, use **File > Refresh application data**. Help and the license are rendered in randname's own window and do not require an external viewer. If the selected help translation is unavailable, the Help command opens this English document.