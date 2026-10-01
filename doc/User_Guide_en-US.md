# randname User Guide (English, US)

randname is a desktop app for classroom roll calls and random name selection. It includes four modes: Single, Multi, Lift, and ScrollSingle. This guide covers installation, everyday use, configuration, and troubleshooting. The app's menus and controls are currently displayed in Simplified Chinese; their labels are included below.

Languages: [简体中文](使用指南_简体中文.md) | [繁體中文](使用指南.md)

## 1. Install and Launch

### Prebuilt Release

1. Download the release for your operating system from [GitHub Releases](https://github.com/HQZ-OhNone/randname/releases).
2. Extract the archive to a directory where you can write files.
3. Run `randname` on Linux or `randname.exe` on Windows.

The splash screen stays visible for at least one second. If initialization takes longer, it remains open until the main window is ready.

### Run from Source

The project requires Python 3.12.10 and PySide6 6.11.1. From the project root, create a virtual environment and install PySide6:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install PySide6==6.11.1
python main.py
```

In Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`; the remaining installation commands are the same. If you do not use a virtual environment, make sure `python` points to a compatible Python version.

### Build the App

The repository includes `build_linux.sh` and `build_windows.bat`. Install the required Python, PySide6, and Nuitka versions for your target platform, then run the matching script. Build output is placed in `build/`; use the scripts as the source of truth for build options and included resources.

## 2. Window and Modes

Use the **模式** (Mode) menu at the top of the window to switch pages. Changing modes does not clear the roster. The startup mode is set by `app.default_mode` in `doc/config.toml`; it defaults to `ScrollSingle`. The status bar at the bottom reports the latest result or operation status.

### Single (单抽)

1. Choose **模式 -> 单抽** (Mode -> Single).
2. Click **抽取** (Draw).
3. The selected name appears in the result area and in the status bar.

Each draw randomly selects one person from the full roster. The selected person is not removed, so they may be selected again on a later draw.

### Multi (多抽)

1. Choose **模式 -> 多抽** (Mode -> Multi).
2. Use the `+` and `-` buttons next to the quantity to set the number of people. The minimum is 1 and the maximum is the current roster size.
3. Click **抽取** (Draw).

Names are unique within one draw. Separate draws are independent, so previous selections are not permanently removed. The result area lists everyone selected in the current draw.

### Lift (减量抽)

1. Choose **模式 -> 减量抽** (Mode -> Lift).
2. Set the quantity and click **抽取** (Draw).
3. Later draws continue from the remaining roster.
4. Click **重置** (Reset) to restore the full roster and start over.

The remaining roster is kept only for the current app session and is not carried over after the app closes. A draw cannot select more people than remain.

### ScrollSingle (滚动单抽)

1. Choose **模式 -> 滚动单抽** (Mode -> ScrollSingle).
2. Click **开始** (Start) to cycle through names in the result area.
3. Click **停止** (Stop). The name shown when the cycle stops is the result.

The cycling speed is set by `scroll_single.rate`, the number of updates per second. The roster is reshuffled after each pass. Stopped results are saved to recent results and the log.

## 3. Roster and Configuration

The configuration file is `doc/config.toml`, in TOML format. It is read at startup. If it is missing or cannot be parsed, the app tries `.config.default.toml` in the project root and displays a notice that the fallback configuration is in use. Back up the file before editing it.

| Section | Fields | Description |
| --- | --- | --- |
| `[app]` | `name` | App name. |
| `[app]` | `default_mode` | Startup mode: `Single`, `Multi`, `Lift`, or `ScrollSingle`. |
| `[app]` | `theme` | Startup theme name; the default is `randname`, matching a TOML filename in `theme/` without its extension. |
| `[splash]` | `duration_ms` | Minimum splash-screen duration in milliseconds; defaults to `1000`. |
| `[window]` | `width`, `height` | Initial window dimensions; both must be positive integers. |
| `[scroll_single]` | `rate` | ScrollSingle updates per second; must be a positive integer. |
| `[names]` | Roster entries | Each key is a unique ID, and each value is a display name. |

Example roster:

```toml
[names]
"student-001" = "Alex Morgan"
"student-002" = "Taylor Chen"
```

Use a unique key for each person. Restart the app after editing `doc/config.toml` to apply all settings. **文件 -> 重新加载配置** (File -> Reload Configuration) reloads the roster, rescans `theme/`, and applies the theme specified in the configuration. New, edited, or removed valid themes appear in the theme menu immediately. Window size and startup mode still require a restart.

## 4. Themes

The startup theme is selected by `app.theme`. While the app is running, choose a theme from the **主题** (Theme) menu. The app discovers valid files matching `theme/*.toml`. To create a custom theme, copy an existing file and adjust its colors; the new file must include a `[colors]` section. See the other files in that directory for examples. After adding or editing a theme, use **文件 -> 重新加载配置** (File -> Reload Configuration) to rescan the directory and apply the configured theme without restarting.

## 5. Memory and Logs

- `doc/memory.json` stores imported/exported memory data and the latest results for each mode.
- `doc/log.log` records events such as configuration loading, draw results, and errors.
- **文件 -> 导入...** (File -> Import...) loads a JSON memory file and applies its roster, if present, and recent results. It does not overwrite `doc/config.toml`.
- **文件 -> 导出...** (File -> Export...) saves the current memory data to a JSON file.

Memory and configuration files serve different purposes. Edit `doc/config.toml` to change the roster used for everyday draws. Use memory import/export to back up or move recent results.

## 6. Troubleshooting

**A draw produces no result**

Make sure `[names]` contains at least one valid entry in the configuration currently in use. Check `doc/config.toml` for misspelled keys, unmatched quotes, or invalid TOML. An empty roster cannot be drawn from.

**Multi or Lift selects fewer people than requested**

Multi cannot exceed the total roster size, and Lift cannot exceed the remaining roster size. In Lift mode, click **重置** (Reset) to restore the full roster.

**Configuration or theme changes do not appear**

Reload Configuration reloads the roster and theme files and applies the configured theme. The startup mode and window size are applied when the app starts, so restart the app after changing those settings.

**The configuration file will not load**

Check that `doc/config.toml` is valid TOML, especially string quotes and section names. If the primary file cannot be read, the app tries `.config.default.toml`. If neither file is usable, restore a valid configuration and restart.

## 7. License and Support

This project is licensed under the GNU General Public License v3.0. Read the full [GPL-3.0 license](gpl-3.0.txt). For issues and source code, visit the [GitHub repository](https://github.com/HQZ-OhNone/randname).