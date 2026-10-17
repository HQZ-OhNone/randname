# randname 業務邏輯說明（正體中文）

Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; see the GNU General Public License for more details.

本文記錄 randname 3.8.1 的實際行為、隱藏機制與邊界。簡體中文見
`logic_zh_CN.md`，英文見 `logic_en_US.md`。

## 1. 術語與模式

| 內部識別 | 正體介面 | 簡體介面 | English | 頁面 |
| --- | --- | --- | --- | --- |
| `Multi` | 多抽 | 多抽 | Multi | 多抽頁面 |
| `Single` | 單抽 | 单抽 | Single | 多抽頁面（數量 1） |
| `Lift` | 減量抽 | 减量抽 | Elimination | 減量抽頁面 |
| `ScrollMulti` | 滾動多抽 | 滚动多抽 | Rolling Multi | 滾動多抽頁面 |
| `ScrollSingle` | 滾動單抽 | 滚动单抽 | Rolling Single | 滾動多抽頁面（數量 1） |
| `ScrollLift` | 滾動減量抽 | 滚动减量抽 | Rolling Elimination | 滾動減量抽頁面 |

- 單抽與滾動單抽只是選單快捷方式，不建立獨立頁面或控制器。
- 結果、日誌與記憶仍使用 `Multi`、`Lift`、`ScrollMulti`、`ScrollLift` 作為
  `mode` 欄位。
- 使用者可見文字不再直接顯示 `ScrollMulti` 等內部識別。

## 2. 檔案與職責

| 路徑 | 職責 |
| --- | --- |
| `main.py` | 啟動、主視窗、選單、狀態列、頁面切換、記憶回填 |
| `lib/version.py` | `APP_VERSION = "3.8.1"` |
| `lib/Multi.py` | 多抽演算法 |
| `lib/Lift.py` | 減量抽演算法 |
| `lib/ScrollMulti.py` | 滾動多抽控制器 |
| `lib/ScrollLift.py` | 滾動減量抽控制器（繼承 ScrollMultiController） |
| `lib/OutputView.py` | 輸出框單行/多行/縮字號 |
| `lib/TextViewer.py` | 唯讀即時說明/授權/日誌檢視器 |
| `lib/StateManager.py` | 設定、記憶、偏好、日誌 |
| `lib/importnames.py` | 名單載入 |
| `lib/ThemeManager.py` | 主題與 QSS |
| `lib/LanguageManager.py` | 語言包與回退 |
| `ui/*.ui` | Qt Designer 原始檔 |
| `lib/ui_*.py` | `pyside6-uic` 產物，建置前重新產生 |
| `config/*.toml` | 設定、名單、主題、語言 |
| `doc/memory.json` | 偏好、視窗尺寸、最近結果 |
| `doc/log.log` | 持久日誌 |

## 3. 啟動流程

1. 顯示 GPL 橫幅。
2. 建立 `QApplication`。
3. `_bootstrap_config()` 讀取 `config/config.toml`，失敗時讀
   `.config.default.toml`，再失敗使用內建設定。
4. 載入圖示與啟動畫面。
5. 依 `[splash]` 的 `size_mode`/`screen_ratio`/`aspect_ratio` 縮放，保持比例。
6. `_draw_splash_version()` 在右下角繪製 `v3.8.1`；`version_font_size = 0`
   表示自動字號，`version_color` 控制顏色。
7. `_startup_file_check()` 收集可恢復檔案警告；`required` 目前恆為空。
8. 匯入 `lib` 模組。
9. `StateManager.configure_paths()` 套用 `[paths]`。
10. 讀取記憶偏好；`[app].remember_preferences = false` 時忽略。
11. 日誌等級：記憶中有效值 > `[logging].level` > `INFO`。
12. 主題：記憶中有效值 > `theme.toml` 的 `default` > `config.toml`
    `app.theme` > 第一個主題。
13. 語言：記憶中有效值 > `language.toml` 的 `preferred` > `config.toml`
    `app.language` > 系統語言 > `en_US`。
14. 名單：記憶中有效值 > `[app].roster` > 第一組名單。
15. 模式：記憶中有效值 > `[app].default_mode` > `Multi`。
16. 建立 `MainWindow`、套用主題、顯示；若記憶為最大化則還原。
17. 依 `[splash].mode` 關閉啟動畫面。

## 4. 設定優先順序

主題：

```
記憶 preferences.theme（有效）
  > theme.toml default（有效）
  > config.toml [app].theme（舊鍵）
  > 第一個主題
```

語言：

```
記憶 preferences.language（有效）
  > language.toml preferred（有效）
  > config.toml [app].language（舊鍵）
  > 系統語言
  > en_US
```

其他：

- 名單：記憶 `preferences.roster` > `[app].roster` > 第一組。
- 模式：記憶 `preferences.mode` > `[app].default_mode` > `Multi`。
- 日誌等級：記憶 `preferences.log_level` > `[logging].level` > `INFO`。
- 數量：記憶 `preferences.quantities` > 1。
- 視窗：`[window]` 計算初始尺寸；`remember_size = true` 且記憶尺寸有效時，
  記憶尺寸覆蓋初始尺寸。

`[app].remember_preferences = false` 只忽略應用偏好，不影響
`[window].remember_size`。

## 5. 視窗與狀態列

### 初始尺寸

`_configured_size()`：

1. `size_mode = "fixed"` 且 `width`/`height` 為正整數時直接使用。
2. 否則讀取 `screen_ratio`（預設 0.75，限制 0.05~1.0）與
   `aspect_ratio`（預設 1.5）。
3. `width = screen_width * screen_ratio`。
4. `height = width / aspect_ratio`。
5. 若 `height > screen_height * screen_ratio`，改用高度上限並重算寬度。
6. 回傳至少 1 的整數。

啟動畫面使用相同演算法，預設 `screen_ratio = 0.25`、`aspect_ratio = 2.0`。

### 拉伸與持久化

- `resizable = true` 允許拖動邊緣，最小尺寸 640×480。
- `resizable = false` 使用 `setFixedSize()`。
- 內容變化永遠不會改變視窗尺寸。
- 拉伸後 `resizeEvent` 啟動 450ms 單次計時器，逾時寫入記憶。
- 最大化/還原也觸發儲存。
- 關閉視窗時再儲存一次。
- 最大化時儲存 `normalGeometry()` 與 `maximized: true`；還原時儲存目前尺寸與
  `maximized: false`。
- 啟動時記憶尺寸會夾在目前螢幕可用區域內。
- 「檔案 > 重新整理程式狀態」不重設視窗尺寸。

### 狀態列

- 左側顯示 `showMessage()` 臨時訊息。
- 右側永久顯示模式、名單、數量、主題、語言、日誌等級、版本，以 `|` 分隔。
- `[statusbar].show_*` 可逐項隱藏。
- 模式、名單、數量、主題、語言、日誌等級或設定變更後呼叫
  `_update_status_info()`。
- 版本來自 `lib/version.py`。

## 6. 輸出框自適應（所有模式）

`lib/OutputView.py` 包裝一個 `QLabel`：

1. `setSizePolicy(Ignored, Ignored)`、`setMinimumSize(0, 0)`，避免
   `QLabel.sizeHint()` 撐大視窗。
2. 基準字號 `[ui].display_font_size`；下限 `display_min_font_size`；步長
   `display_font_step`；行距 `display_line_spacing`；內距 `display_padding`。
3. 姓名依顯示寬度貪婪分行，姓名間兩個空格，不會從姓名中間斷開。
4. 先嘗試基準字號單行；放不下且高度足夠時多行；仍放不下時逐步縮字號。
5. 極端長姓名在最小字號仍超寬時，允許 Qt 在字元間換行。
6. 滾動模式在每輪開始呼叫 `begin_round(pool_names, quantity)`：
   - 量測池中最寬的 `quantity` 個姓名；
   - 計算並鎖定能容納最壞情況的字號；
   - 本輪 tick 沿用鎖定字號，避免字號跳動；
   - 結果/重設後恢復自動字號。
7. `set_message()` 用於「等待輸入」「暫無結果」，固定使用基準字號。
8. `resizeEvent` 重新排版，使用者拉伸後自動調整。

## 7. 多抽（Multi）

`Multi.Multi(alllist, quantity)`：

1. `quantity > len(alllist)` 時回傳 `outdict = {}`。
2. 否則從完整名單無放回隨機抽取。
3. `outdict` 重新編號為 `"0"`, `"1"`, ...，每項
   `{"code": 原鍵, "name": 姓名}`。
4. 時間格式 `%Y-%m-%d-%H:%M:%S`。
5. 每次抽取都從完整名單開始。

結果：

```json
{
  "mode": "Multi",
  "quantity": {"total": 9, "selected": 3},
  "time": "2026-10-18-12:00:00",
  "outdict": {"0": {"code": "1", "name": "王小明"}}
}
```

## 8. 減量抽（Lift）

`Lift.Lift(alllist, Liftdict, quantity)`：

1. `Liftdict` 是目前剩餘名單；第一次由 `MainWindow` 傳入完整名單。
2. `Liftdict` 為空或 `quantity > len(Liftdict)` 時，`outdict = {}`，
   `Liftdict` 原樣回傳。
3. 否則無放回抽取，`outdict` 每項為單鍵包裹 `{原鍵: 姓名}`。
4. `Liftdict` 更新為未抽中者。
5. `quantity`：
   - `total`：完整名單人數；
   - `wasted`：`total - 抽取前 Liftdict 人數`；
   - `selected`：本次抽取數；
   - `Lift`：`抽取前 Liftdict 人數 - selected`，即本輪後剩餘人數。
6. `alllist` 直接引用完整名單，會寫入記憶。
7. 「重設」清空 `lift_current_dict`，數量不變。
8. 切換名單或重新整理後名單內容有變時清空狀態。

## 9. 滾動多抽（ScrollMulti）

`ScrollMultiController`：

- 建構時複製名單；`quantity` 預設 1；計時器間隔
  `max(1, 1000 // rate)`。
- `start()`：
  1. 名單為空時警告並返回。
  2. `total = min(quantity, len(names))`；請求數過大時警告。
  3. `pool = dict(names)` 作為本輪共享池。
  4. 建立 `total` 個 reel，各有隨機順序與索引。
  5. 呼叫 `view.begin_round(pool.values(), total)` 鎖定字號。
  6. 立即 `_tick()`，再啟動計時器。
- `_tick()` 推進每個 active reel；順序用完重新洗牌；若鍵已不在池中則重新洗牌。
- `stop_next()`：
  1. 取第一個 active reel。
  2. 標記 inactive。
  3. 若目前鍵已被先前的 reel 固定，從剩餘池補抽。
  4. 從池中移除該鍵。
  5. 重建所有 active reel 的順序，避免再出現已固定姓名。
  6. 刷新輸出。
  7. 沒有 active reel 時完成。
- 按鈕：執行中「停止（剩餘/總數）」，閒置「抽取」。
- `_finish()` 停止計時器、建立結果、恢復按鈕、呼叫
  `on_result(result, meta)`。
- 結果：`mode = "ScrollMulti"`、短橫線時間、
  `quantity.total = len(names)`、`quantity.selected = total`、`outdict`
  依停止順序編號，同一輪 code 不重複。
- `show_result()` 從記憶恢復顯示，不啟動滾動。
- `update_names()` 名單變更時重置；`update_rate()` 只改間隔。

## 10. 滾動減量抽（ScrollLift）

`ScrollLiftController` 繼承 `ScrollMultiController`，增加跨輪剩餘池：

- `lift_pool` 初始為完整名單。
- `start()`：
  1. `lift_pool` 為空時警告並返回；狀態列顯示「剩餘名單已空，請重設後繼續」。
  2. `available = len(lift_pool)`；`total = min(quantity, available)`。
  3. 記錄 `round_available = available`。
  4. `pool = dict(lift_pool)`。
  5. 建立 reel、鎖定字號、啟動計時器。
- 停止邏輯繼承；本輪固定者從 `pool` 移除。
- `_finish()` 先設 `lift_pool = dict(pool)`，再走父類完成流程。
- 結果：
  - `mode = "ScrollLift"`；
  - `quantity.total = len(names)`；
  - `quantity.wasted = total - round_available`；
  - `quantity.selected = total`；
  - `quantity.Lift = round_available - total`；
  - `outdict`：本輪抽中者；
  - `alllist`：完整名單；
  - `Liftdict`：本輪後剩餘名單。
- `reset()` 恢復 `lift_pool = dict(names)`，清空輸出，數量不變。
- `show_result()` 還原 `Liftdict`；舊記憶沒有 `Liftdict` 時，用完整名單減去
  `outdict` 的 code 還原。
- 匯入記憶只還原結果與剩餘池，不切換目前主題/語言。

## 11. 單抽與滾動單抽別名

- 選單「單抽」→ `_show_single_page()`：多抽數量設 1、更新標籤、切到多抽頁、
  儲存模式 `Multi`。
- 選單「滾動單抽」→ `_show_scrollsingle_page()`：滾動多抽數量設 1、更新
  控制器、切到滾動多抽頁、儲存模式 `ScrollMulti`。
- `default_mode` 相容：`Single` → 多抽數量 1；`ScrollSingle` → 滾動多抽數量 1；
  非法值 → 多抽。
- 不建立 `Single.py`、`ScrollSingle.py`、`WidgetScrollSingle.ui` 或獨立頁面。

## 12. 記憶檔

```json
{
  "preferences": {
    "theme": "randname-dark",
    "language": "zh_TW",
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

- 執行期結果條目通常為 `{"result": ..., "meta": ...}`；Multi/Lift 使用
  `{"result": ..., "time": ...}`。
- UTF-8、`ensure_ascii=False`、`indent=2`。
- `save_memory()` 先寫 `.tmp` 再原子替換。
- `_normalize_memory()` 補齊欄位、丟棄非法值、相容舊 `loaded_config`。
- 舊 `ScrollSingle` 條目會被忽略。
- 主題、語言、名單、模式、數量、日誌等級變更後立即儲存偏好。
- 視窗尺寸 450ms 防抖 + 關閉 + 最大化/還原時儲存。
- 每次抽取/滾動完成後儲存結果。
- 匯入/匯出不寫 `config/`。
- 匯入檔沒有 `preferences` 時保留目前偏好；有偏好時下次啟動生效，目前工作階段
  不立即切換。
- `remember_preferences = false` 關閉應用偏好，但 `remember_size` 仍獨立運作。

## 13. 日誌

- `StateManager.configure_logging()` 設定根 logger 並安裝 `_SessionLogHandler`。
- Handler 將記錄追加到 `[paths].log_file`，同時存入 `SESSION_LOG_RECORDS`。
- `StateManager.log()` 寫出精簡單行：

```
time=2026-10-18 12:00:00 level=INFO action=Multi result=(...)
```

- 欄位順序：`time` → `level` → `action` → `result` → `error`。
- `_log_value()` 將換行/製表符換成空格，`{}[]` 換成 `()`，保證單行。
- 低於目前等級的記錄不寫入。
- 「關於 > 程式日誌」讀取日誌檔，不只顯示本次工作階段記憶體。
- 檢視器每 `[viewer].refresh_ms` 檢查檔案修改時間/大小。

## 14. 內部文字檢視器

`lib/TextViewer.py`：

- 說明/授權：`QTextBrowser` + `setMarkdown()`。
- 日誌：`QPlainTextEdit` + `setPlainText()`。
- 唯讀、停用復原/重做。
- 非模態，可一邊執行程式一邊查看。
- `QFileSystemWatcher` 監聽檔案與父目錄；`QTimer` 輪詢備援。
- 保留捲動位置；原本在底部時跟隨新內容，使用者上捲後不強制跳到底部。
- 尺寸依父視窗螢幕的 `availableGeometry()`；不超過
  `available * max_screen_ratio` 再減 24px，最大 900×680，小螢幕自動縮小。
- 觸控：`QScroller` 左鍵手勢、22px 捲動條、40px 關閉按鈕。
- 同一路徑重複開啟時啟用既有視窗。
- 說明/授權檔案修改後即時刷新。

## 15. 主題與語言

### 主題

- `config/theme.toml` 集中保存 `default` 與 `[themes.<鍵>]`。
- 每個主題含 `color_format`、多語言 `name`、`colors`。
- 支援 `HexA`、`Hex`、`RGBA`、`RGB`。
- `_stylesheet()` 覆蓋頁面/控件背景、輸出框 ID
  （`label_MultiOutput`、`label_LiftOutput`、`label_ScrollMultiOutput`、
  `label_ScrollLiftOutput`）、按鈕、選單選取、狀態列。
- ID 選擇器優先於 `.ui` 內的 `QLabel` 元素樣式。
- 主題名依目前語言、系統語言、英語、鍵名回退。

### 語言

- `language.toml` 的 `preferred` 是首次啟動語言；記憶偏好優先。
- `LanguageManager.ENGLISH` 是內建備援。
- 缺少翻譯鍵時回退英語，再回退鍵名。
- `{count}`、`{name}` 等佔位符必須保留。
- 切換語言立即刷新選單、按鈕、占位文案與狀態列，不清除目前結果。

## 16. UI 與選單

- 主視窗：`ui/Main.ui` → `lib/ui_main.py`。
- 頁面：多抽、減量抽、滾動多抽、滾動減量抽。
- 模式選單順序：單抽、多抽、減量抽、分隔線、滾動單抽、滾動多抽、滾動減量抽。
- 關於選單：說明、程式日誌、記錄等級、分隔線、授權、專案原始碼、回饋。
- 專案與回饋網址硬寫在 `main.py` 的 `REPOSITORY_URL`、`FEEDBACK_URL`，
  不是設定項。
- 模式 QAction 未加入 `QActionGroup`；以目前頁面與 `current_mode` 為準。

## 17. 建置與發布

1. `pyside6-uic` 編譯：
   - `Main.ui` → `ui_main.py`
   - `WidgetMulti.ui` → `ui_widgetmulti.py`
   - `WidgetLift.ui` → `ui_widgetlift.py`
   - `WidgetScrollMulti.ui` → `ui_widgetscrollmulti.py`
   - `WidgetScrollLift.ui` → `ui_widgetscrolllift.py`
2. Nuitka 包含 `ui/randname1.png`、`ui/randname-start.png`、
   `.config.default.toml`、`.name.default.toml`、`config/`、`doc/`。
3. 已刪除 `WidgetScrollSingle.ui`、`ui_widgetscrollsingle.py`、
   `ScrollSingle.py`、`randname-start_v3.6.png`、`randname-start_v3.7.png`。
4. 版本在 `lib/version.py`；提交訊息使用 `3.8.1[upgrade]_...` 觸發發布。

## 18. 隱藏機制與邊界

### 輸出與視窗

- `Ignored` 尺寸策略是避免視窗被長文字撐大的關鍵，不要改回 `Expanding`。
- `setMinimumSize(0, 0)` 與手動分行共同防止版面最小尺寸傳播。
- 滾動模式每輪開始鎖定字號，避免 tick 時字號跳動。
- 使用者拉伸後重新排版；內容不會改變視窗尺寸。
- 極端長姓名在最小字號仍可能超寬，此時允許字元間換行。

### 滾動

- `ScrollMulti.pool` 是本輪共享池，`start()` 時從完整名單重建。
- 快速點擊可能發生在兩個 tick 之間；`stop_next()` 會檢查鍵是否仍可用。
- 每次停止後重建 active reel 順序，避免重複固定姓名。
- `quantity.total` 是完整名單人數；`quantity.selected` 是本輪實際抽取數。
- `ScrollLift.lift_pool` 跨輪保留；`quantity.wasted` 是此前已減量人數。
- ScrollLift 剩餘池為空時不會自動重設，必須按「重設」。
- 匯入 ScrollLift 記憶會還原 `Liftdict`，可繼續抽取。

### 減量抽

- 數量上限是完整名單長度，不是剩餘長度；剩餘不足時會得到空 `outdict`，
  介面顯示「暫無結果」，需調小數量或重設。
- `quantity.Lift` 是「本輪後剩餘人數」，不是「已減量數」。
- 匯入記憶不會還原 `lift_current_dict`。

### 記憶

- `loaded_config` 是舊版設定快照；新偏好以 `preferences` 為準。
- 匯入不寫 `config/`、不改名單、不立即切換主題/語言。
- 記憶損壞時回退預設結構，不阻止啟動。
- `save_memory()` 使用原子替換；不要直接寫 `memory.json`。
- 舊 `ScrollSingle` 條目會被忽略。

### 日誌與檢視器

- 日誌路徑由 `[paths].log_file` 決定，寫入端與檢視器共用。
- 檢視器非模態，關閉主視窗時一併關閉。
- 檔案被刪除時顯示「目前尚無日誌記錄」，並繼續監聽父目錄。
- 觸控行為依平台而異，需實機驗證。

### 安全

- 程式不主動連網；唯一網路行為是使用者點擊專案或回饋連結。
- 沒有密鑰、權杖、遙測或上傳。
- `config/` 唯讀；只寫入設定的記憶檔與日誌檔。
- `doc/memory.json`、`doc/log.log` 已加入 `.gitignore`。

## 19. 測試

- `tests/test_output_fit.py`
- `tests/test_memory.py`
- `tests/test_scroll_lift.py`
- `tests/test_config.py`

執行：`QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests`。

## 20. 版本

目前版本：**3.8.1**。

本輪主要變更：

- 修正滾動多抽視窗閃動。
- 修正匯入記憶撐寬視窗與直接顯示字典內容。
- 所有模式共用輸出框自適應。
- 視窗可拉伸並持久化尺寸。
- 狀態列資訊擴充。
- 記憶偏好與視窗尺寸。
- 單抽/滾動單抽別名。
- 新增滾動減量抽。
- 即時唯讀文字檢視器。
- 啟動畫面新圖與動態版本號。
- 設定註解與精簡。
- 業務邏輯文件多語言化。

## 21. 3.8.1 增補

- `OutputView` 尺寸策略由 `Ignored` 改為 `Expanding`，並保留 `.ui` 中 160 的水平
  stretch；否則 `QGridLayout` 會把寬度分給左右 spacer，輸出框只剩幾十像素。
- `OutputView` 始終保持 `wordWrap = True`。手動分行仍由 `pack_names()` 完成；
  `wordWrap` 只用於降低 `QLabel.minimumSizeHint()`，避免長姓名撐大視窗。
- 狀態列改為佔滿寬度的 `QWidget` 容器，內部用 `QHBoxLayout` 左對齊臨時訊息與
  全部資訊標籤；不再使用 `QStatusBar.showMessage()`，避免一般 widget 被臨時訊息隱藏。
- 臨時訊息透過 `_show_status_message()` 寫入 `status_message_label`；重新整理設定時
  保存/還原的也是該標籤文字。
- 「關於 > 回饋」改為二級選單：
  - `GitHub Issues`：開啟 `https://github.com/HQZ-OhNone/randname/issues`；
  - `Email`：呼叫系統郵件程式寄信至 `ohnone_hqz@outlook.com`；
  - 無法喚起郵件程式時，彈出資訊框顯示電子郵件地址。
- `EMAIL_ADDRESS` 與專案/回饋網址一樣硬寫在 `main.py`。
- 版本更新為 `3.8.1`。
