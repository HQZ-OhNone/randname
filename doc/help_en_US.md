# randname Help

randname is a desktop app for classroom roll calls. The Mode menu contains Single, Multi, Lift, ScrollSingle, ScrollMulti, and ScrollLift.

## Drawing

- **Single:** A shortcut that opens Multi and sets the quantity to `1`; it has no separate page.
- **Multi:** Set the quantity with the increase/decrease buttons or the vertical slider, then select Draw. A draw contains no duplicate names; later draws start from the full roster again.
- **Lift:** Each draw removes selected people from the remaining pool for the current run. Reset restores the active roster. Changing rosters or refreshing changed roster data also resets the remaining pool.
- **ScrollSingle:** A shortcut that opens ScrollMulti and sets the quantity to `1`.
- **ScrollMulti:** Set the quantity with the vertical slider or buttons, then select Draw to show that many fixed slots cycling at once. Slot positions are decided on the first draw (for example six names form a centred 3×2 grid), and each press of Stop fixes one name without moving names already fixed. If a name is too long, randname adjusts the grid or font size and locks it again; the next draw or a quantity change resets the layout. Names fixed this round never appear again in the same round. The cycle rate is controlled by `scroll.rate`.
- **ScrollLift:** The scrolling and fixed-slot layout is the same as ScrollMulti, but names drawn this round are removed from the remaining pool. The Reset button restores the full roster. The rate is also controlled by `scroll.rate`.

All four quantity pages provide a vertical slider from `1` to the current roster size. It supports dragging and touch input and stays synchronised with the buttons and quantity display. Changing rosters or refreshing configuration clamps an out-of-range quantity automatically.

The output box never changes the window size. In non-rolling modes, names are shown on one line when possible, wrapped onto multiple lines when there is enough height, and the font is reduced for the current draw when the box is already full. Rolling modes keep every name in a fixed slot and reduce the font only when a name cannot fit its slot. Name spacing is compact, and on large screens the rolling grid is capped by its content width and centred instead of stretching names across the whole box.

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

randname does not remember the theme, roster, log level, mode, language, quantity, or window size from the last session. Every startup reads the configuration and dedicated theme/language files so the interface state is consistent. The memory file is used only to store and import/export recent results.

## Window and Status Bar

The main window can be resized by dragging its edges, but the next startup still uses the initial size configured in `[window]`; the last resized size is not remembered. Long names and memory imports never change the window size. Set `size_mode` to `"maximum"` to start maximised.

The left side of the status bar shows temporary messages such as "Multi complete"; the right side shows the current mode, roster, quantity, theme, language, log level, and version. Each item can be hidden in `[statusbar]`.

## Settings

Edit `config/config.toml` to set the startup mode, roster, splash screen, window size, output font sizes, rolling rate, viewer, status bar, log level, and update timeout; the theme and language come from their dedicated `theme.toml` and `language.toml` files. Every option in the configuration file has an explanatory comment. The icon, splash image, help, license, log, and memory paths are fixed in code and are no longer configurable.

```toml
[window]
size_mode = "screen_ratio"   # or "fixed", "maximum"
screen_ratio = 0.75          # initial size as a share of the available screen
aspect_ratio = 1.5
width = 1000
height = 600
resizable = true

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

Choose a threshold under **About > Log level**: Debug, Information, Warning, Error, or Critical. The threshold controls only what is written to `doc/log.log`; the program log window always shows every level from the current run and highlights the level tag at the start of each line.

File > Import memory and File > Export memory exchange recent results as JSON. They do not replace configuration, roster, or interface state. The runtime memory file is `doc/memory.json` and stores only each mode's most recent result.

Help, the license, and the program log all use randname's own read-only viewer. The viewer is clamped to the available desktop area so the taskbar remains accessible; it supports touch-drag scrolling, and its font size and refresh interval can be adjusted in `[viewer]`.

**About > Check for updates** queries GitHub Releases asynchronously. A large label at the top shows checking, up to date, a new version found, or a failed check; the text below shows `doc/history.md`. Update is enabled only when a newer release is found, opens the Releases page, and closes the window. Manual check always opens the Releases page without closing the window, and OK only closes it. If the network is unavailable or GitHub rate-limits the request, use Manual check.

## Startup and Troubleshooting

The splash screen appears before data checks and window initialization. Missing configuration, roster, language, or theme files use their available backup or built-in data; randname reports these cases in the status bar and log without an extra dialog. Missing executable components stop startup and show a detailed error.

If a configured choice is unavailable after editing files, use **File > Refresh application data**. If the selected help translation is unavailable, the Help command opens this English document. **About > Feedback** contains GitHub Issues and Email; if no mail client can be opened, a dialog shows the email address.
