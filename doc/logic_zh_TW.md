# randname 業務邏輯說明（正體中文）

Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; see the GNU General Public License for more details.

本文記錄 randname 3.10.0 的實際行為、隱藏機制與邊界。簡體中文見
`logic_zh_CN.md`，英文見 `logic_en_US.md`。

## 1. 術語與模式

| 內部識別 | 正體介面 | 簡體介面 | English | 頁面 |
| --- | --- | --- | --- | --- |
| `Multi` | 多抽 | 多抽 | Multi | 多抽頁面 |
| `Single` | 單抽 | 单抽 | Single | 多抽頁面（數量 1） |
| `Lift` | 減量抽 | 减量抽 | Lift | 減量抽頁面 |
| `ScrollMulti` | 滾動多抽 | 滚动多抽 | ScrollMulti | 滾動多抽頁面 |
| `ScrollSingle` | 滾動單抽 | 滚动单抽 | ScrollSingle | 滾動多抽頁面（數量 1） |
| `ScrollLift` | 滾動減量抽 | 滚动减量抽 | ScrollLift | 滾動減量抽頁面 |

- 單抽與滾動單抽只是選單快捷方式，不建立獨立頁面或控制器。
- 結果、日誌與記憶仍使用 `Multi`、`Lift`、`ScrollMulti`、`ScrollLift` 作為
  `mode` 欄位。
- 使用者可見文字不再直接顯示 `ScrollMulti` 等內部識別。

## 2. 檔案與職責

| 路徑 | 職責 |
| --- | --- |
| `main.py` | 啟動、主視窗、選單、狀態列、頁面切換、記憶回填 |
| `lib/version.py` | `APP_VERSION = "3.10.0"` |
| `lib/Multi.py` | 多抽演算法 |
| `lib/Lift.py` | 減量抽演算法 |
| `lib/ScrollMulti.py` | 滾動多抽控制器 |
| `lib/ScrollLift.py` | 滾動減量抽控制器（繼承 ScrollMultiController） |
| `lib/OutputView.py` | 非滾動輸出框自適應；滾動模式固定格子 `SlotOutputView` |
| `lib/TextViewer.py` | 唯讀即時說明/授權/日誌檢視器 |
| `lib/UpdateDialog.py` | 檢查更新視窗、GitHub Releases 查詢與版本比較 |
| `lib/StateManager.py` | 設定、記憶結果、日誌 |
| `lib/importnames.py` | 名單載入 |
| `lib/ThemeManager.py` | 主題與 QSS |
| `lib/LanguageManager.py` | 語言包與回退 |
| `ui/*.ui` | Qt Designer 原始檔 |
| `lib/ui_*.py` | `pyside6-uic` 產物，建置前重新產生 |
| `config/*.toml` | 設定、名單、主題、語言 |
| `doc/memory.json` | 各模式最近結果（僅供匯出/匯入） |
| `doc/log.log` | 持久日誌 |

## 3. 啟動流程

1. 顯示 GPL 橫幅。
2. 建立 `QApplication`。
3. `_bootstrap_config()` 讀取 `config/config.toml`，失敗時讀
   `.config.default.toml`，再失敗使用內建設定。
4. 載入圖示與啟動畫面。
5. 依 `[splash]` 的 `size_mode`/`screen_ratio`/`aspect_ratio` 縮放，保持比例。
6. `_draw_splash_version()` 在右下角繪製 `v3.10.0`；字號始終依圖片寬度的三分之一
   自動縮放，文字固定為純白色，不提供字號或顏色設定。
7. `_startup_file_check()` 收集可恢復檔案警告；`required` 目前恆為空。
8. 匯入 `lib` 模組。
9. 圖示、啟動圖、說明、授權、日誌與記憶路徑固定於程式碼，不再有可設定路徑段。
10. 不讀取記憶偏好；每次啟動都從設定檔與獨立設定檔讀取介面狀態。
11. 日誌等級：`[logging].level` > `INFO`；該等級只控制檔案寫入。
12. 主題：`theme.toml` 的 `default` > `config.toml` `app.theme`（舊鍵） > 第一個主題。
13. 語言：`language.toml` 的 `preferred` > `config.toml` `app.language`（舊鍵） > 系統語言 > `en_US`。
14. 名單：`[app].roster` > 第一組名單。
15. 模式：`[app].default_mode` > `Multi`；數量固定從 1 開始。
16. 建立 `MainWindow`、套用主題；主視窗是否立即顯示取決於 `[splash].mode`。
17. `[splash].mode = 1` 時先只顯示啟動畫面，剩餘時間到後才顯示主視窗並關閉啟動畫面；其他模式在主視窗就緒後立即顯示並關閉啟動畫面。

## 4. 設定優先順序

主題：

```
theme.toml default（有效）
  > config.toml [app].theme（舊鍵）
  > 第一個主題
```

語言：

```
language.toml preferred（有效）
  > config.toml [app].language（舊鍵）
  > 系統語言
  > en_US
```

其他：

- 名單：`[app].roster` > 第一組。
- 模式：`[app].default_mode` > `Multi`。
- 日誌等級：`[logging].level` > `INFO`。
- 數量：固定從 1 開始。
- 視窗：每次啟動都由 `[window]` 計算初始尺寸，不讀取記憶尺寸。

啟動時不會從記憶檔還原主題、名單、日誌等級、模式、語言、數量或視窗尺寸。

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

`size_mode = "maximum"` 時不計算上述尺寸；`_window_is_maximized()` 判斷後只設定最小尺寸，`reveal_window()` 以 `showMaximized()` 顯示。重新整理設定時，可見視窗也會立即最大化。

啟動畫面使用相同演算法，預設 `screen_ratio = 0.25`、`aspect_ratio = 2.0`。

啟動畫面關閉時機由 `[splash].mode` 決定：

- `mode = 0`：主視窗就緒後立即 `window.show()` 並關閉啟動畫面。
- `mode = 1`：只顯示啟動畫面，等 `duration_ms - splash_timer.elapsed()` 到點後再 `window.show()` 並 `splash.finish(window)`。
- 延後顯示主視窗是為了避開 Wayland：Wayland 不支援 `QSplashScreen` 置頂，主視窗一旦提前顯示就會完全蓋住啟動畫面。
- `_splash_wait_ms(mode, duration_ms, elapsed_ms)` 計算剩餘毫秒數，其他模式回傳 0。

### 拉伸與持久化

- `resizable = true` 允許拖動邊緣，最小尺寸 640×480。
- `resizable = false` 使用 `setFixedSize()`。
- 內容變化永遠不會改變視窗尺寸。
- 拉伸後尺寸不會寫入記憶；下次啟動仍使用設定檔的初始尺寸。
- 「檔案 > 重新整理程式狀態」不重設視窗尺寸。

### 狀態列

- 左側顯示 `showMessage()` 臨時訊息。
- 右側永久顯示模式、名單、數量、主題、語言、日誌等級、版本，以 `|` 分隔。
- `[statusbar].show_*` 可逐項隱藏。
- 模式、名單、數量、主題、語言、日誌等級或設定變更後呼叫
  `_update_status_info()`。
- 版本來自 `lib/version.py`。

## 6. 輸出框自適應

### 6.1 非滾動模式（OutputView）

`lib/OutputView.py` 包裝一個 `QLabel`：

1. `setSizePolicy(Ignored, Ignored)`、`setMinimumSize(0, 0)`，避免
   `QLabel.sizeHint()` 撐大視窗。
2. 基準字號 `[ui].display_font_size`；下限 `display_min_font_size`；步長
   `display_font_step`；行距 `display_line_spacing`；內距 `display_padding`。
3. 姓名依顯示寬度貪婪分行，姓名間兩個空格，不會從姓名中間斷開。
4. 先嘗試基準字號單行；放不下且高度足夠時多行；仍放不下時逐步縮字號。
5. 極端長姓名在最小字號仍超寬時，允許 Qt 在字元間換行。
6. `set_message()` 用於「等待輸入」「暫無結果」，固定使用基準字號。
7. `resizeEvent` 重新排版，使用者拉伸後自動調整。

### 6.2 滾動模式（SlotOutputView）

`SlotOutputView` 沿用原輸出 `QLabel` 作為背景容器，內部用 `_SlotGrid` 手動擺放子 `QLabel`：

1. `begin_round(pool, quantity)` 建立 `quantity` 個固定格子。
2. 第一次 `set_names()` 時計算並鎖定佈局：目標列數以
   `round(sqrt(N * H / W))` 估算；比較所有欄數組合，優先字號最大，字號相同時
   選擇最接近目標列數者。6 人、寬輸出框通常為 2 列 × 3 欄。
3. 每格等寬等高，文字水平/垂直置中；最後一列不足時整列置中。
4. 鎖定後每次 tick 只更新文字，格子幾何不變，已停止的名字不會移動。
5. 目前姓名放不進鎖定格時，重新計算欄數/列數/字號並再次鎖定。
6. `clear_round()`、下一輪 `start()`、更改數量、重設時清除鎖定，下次抽取重新佈局。
7. 匯入歷史結果時依結果人數建立格子並計算一次佈局。
8. ScrollMulti 與 ScrollLift 共用此視圖。

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
  5. 呼叫 `view.begin_round(pool.values(), total)` 建立固定格子；第一次 tick 時鎖定本輪佈局與字號。
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
- `update_names()` 名單變更時重置；`update_rate()` 只改間隔；`set_quantity()` 在閒置時清除佈局鎖定，下一輪重新佈局。

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

- 選單「單抽」→ `_show_single_page()`：多抽數量設 1、更新標籤、切到多抽頁。
- 選單「滾動單抽」→ `_show_scroll_single_page()`：滾動多抽數量設 1、更新
  控制器、切到滾動多抽頁。
- `default_mode` 相容：`Single` → 多抽數量 1；`ScrollSingle` → 滾動多抽數量 1；
  非法值 → 多抽。
- 不建立 `Single.py`、`ScrollSingle.py`、`WidgetScrollSingle.ui` 或獨立頁面。

## 12. 記憶檔

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

- 記憶檔只保存各模式最近結果，不再保存主題、名單、模式、語言、日誌等級、數量或視窗尺寸。
- 執行期結果條目通常為 `{"result": ..., "meta": ...}`；Multi/Lift 使用
  `{"result": ..., "time": ...}`。
- UTF-8、`ensure_ascii=False`、`indent=2`。
- `save_memory()` 先寫 `.tmp` 再原子替換。
- `_normalize_memory()` 只保留 `last_results`，丟棄舊 `preferences` 與 `loaded_config`。
- 舊 `ScrollSingle` 條目會被忽略。
- 每次抽取/滾動完成後儲存結果。
- 主題、名單、語言、日誌等級、模式、數量和視窗尺寸變化都不再寫入記憶檔。
- 匯入/匯出不寫 `config/`，也不改變目前介面狀態。
- 匯入舊記憶檔時只還原 `last_results`；其中的 `preferences`、`loaded_config` 會被忽略。
- 記憶損壞時回退為只含 `last_results` 的預設結構，不阻止啟動。

## 13. 日誌

- `StateManager.configure_logging()` 將根 logger 設為 DEBUG 並安裝 `_SessionLogHandler`。
- Handler 始終將記錄存入 `SESSION_LOG_RECORDS`，再依所選等級寫入 `doc/log.log`。
- `StateManager.log()` 寫出精簡單行：

```
time=2026-10-18 12:00:00 level=INFO action=Multi result=(...)
```

- 欄位順序：`time` → `level` → `action` → `result` → `error`。
- `StateManager.log()` 也會先寫入 `SESSION_LOG_RECORDS`，再判斷檔案等級；因此日誌視窗始終包含本次執行的全部等級。
- 日誌檢視器把工作階段記錄渲染為 HTML，並為行首的 `level=...` 或 `[INFO]` 等級標記上色。
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

- `language.toml` 的 `preferred` 是首次啟動語言；舊 `app.language` 僅作後備。
- `LanguageManager.ENGLISH` 是內建備援。
- 缺少翻譯鍵時回退英語，再回退鍵名。
- `{count}`、`{name}` 等佔位符必須保留。
- 切換語言立即刷新選單、按鈕、占位文案與狀態列，不清除目前結果。

## 16. UI 與選單

- 主視窗：`ui/Main.ui` → `lib/ui_main.py`。
- 頁面：多抽、減量抽、滾動多抽、滾動減量抽。
- 四個數量頁面在數量欄右側各有一個縱向 `QSlider`；`_prepare_quantity_slider()` 安裝觸控過濾器，`_set_quantity()` 統一同步數值、標籤、滑動條與滾動控制器。
- 文字視窗：`ui/TextViewer.ui`；檢查更新視窗：`ui/Update.ui`。
- 模式選單順序：單抽、多抽、減量抽、分隔線、滾動單抽、滾動多抽、滾動減量抽。
- 關於選單：說明、程式日誌、檢查更新、記錄等級、分隔線、授權、專案原始碼、回饋。
- 專案與回饋網址硬寫在 `main.py` 的 `REPOSITORY_URL`、`FEEDBACK_URL`，
  不是設定項。
- 模式 QAction 未加入 `QActionGroup`；以目前頁面與 `current_mode` 為準。

## 17. 建置與發布

1. `pyside6-uic` 遍歷編譯全部 `ui/*.ui`，檔名轉小寫後輸出為 `lib/ui_<name>.py`；新增 `.ui` 不需修改建置腳本。
2. Nuitka 包含 `ui/randname1.png`、`ui/randname-start.png`、
   `.config.default.toml`、`.name.default.toml`、`config/`、`doc/`。
3. 已刪除 `WidgetScrollSingle.ui`、`ui_widgetscrollsingle.py`、
   `ScrollSingle.py`、`randname-start_v3.6.png`、`randname-start_v3.7.png`。
4. 版本在 `lib/version.py`；提交訊息使用 `3.10.0[upgrade]_...` 觸發發布。檢查更新使用 QtNetwork，建置時不再排除 `PySide6.QtNetwork`。

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

- 記憶檔只保存 `last_results`；舊 `preferences`、`loaded_config` 讀取時會被丟棄。
- 匯入不寫 `config/`、不改名單或目前介面狀態。
- 記憶損壞時回退為只含 `last_results` 的預設結構，不阻止啟動。
- `save_memory()` 使用原子替換；不要直接寫 `memory.json`。
- 舊 `ScrollSingle` 條目會被忽略。

### 日誌與檢視器

- 日誌檔固定為 `doc/log.log`；程式日誌視窗顯示目前工作階段記憶體中的全部等級記錄。
- 檢視器非模態，關閉主視窗時一併關閉。
- 檔案被刪除時顯示「目前尚無日誌記錄」，並繼續監聽父目錄。
- 觸控行為依平台而異，需實機驗證。

### 安全

- 程式只會在使用者主動檢查更新或點擊專案、回饋連結時連網。
- 沒有密鑰、權杖、遙測或上傳。
- `config/` 唯讀；只寫入設定的記憶檔與日誌檔。
- `doc/memory.json`、`doc/log.log` 已加入 `.gitignore`。

## 19. 測試

- `tests/test_output_fit.py`：非滾動單行/多行/縮字號；滾動固定格子、位置穩定、超長姓名重排、重設佈局。
- `tests/test_memory.py`：只保留結果、舊偏好丟棄、匯入/匯出結果。
- `tests/test_scroll_lift.py`：剩餘池、逐個停止、重設、數量越界。
- `tests/test_config.py`：設定相容、非法值回退、啟動畫面等待、版本號字號換算、最大化模式與數量夾緊。
- `tests/test_update.py`：版本號解析與新版本比較。

執行：`QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests`。

## 20. 版本

目前版本：**3.10.0**。

3.8.x 主要變更：

- 修正滾動多抽視窗閃動。
- 修正匯入記憶撐寬視窗與直接顯示字典內容。
- 所有模式共用輸出框自適應。
- 視窗可拉伸，但每次啟動使用設定尺寸。
- 狀態列資訊擴充。
- 單抽/滾動單抽別名。
- 新增滾動減量抽。
- 即時唯讀文字檢視器。
- 啟動畫面新圖與動態版本號。
- 設定註解與精簡。
- 業務邏輯文件多語言化。
- 啟動畫面版本號依圖片寬度三分之一自動縮放並固定純白。

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

## 22. 3.8.2 增補

- 啟動畫面 `mode = 1` 不再提前顯示主視窗；`reveal_window()` 在剩餘時間到後才 `window.show()` 並關閉啟動畫面，修正 Wayland 下啟動畫面被主視窗完全遮住、「一閃而過」的問題。
- 新增 `_splash_wait_ms()` 計算啟動畫面剩餘顯示時間；`mode = 0` 和其他模式回傳 0，維持「就緒即關閉」。
- 啟動時語言回到 `language.toml` 的 `preferred`，模式回到 `[app].default_mode`，數量從 1 開始。
- 版本更新為 `3.8.2`。

## 23. 3.8.3 增補

- `_draw_splash_version()` 改為依圖片寬度自動縮放：以 100px 探針字型量測 `v3.8.3`
  的寬度，再依目標寬度（圖片寬度的三分之一）反推實際像素字號；
  `_splash_version_pixel_size()` 負責換算，非法輸入回退為 1px。
- 字號嚴格隨啟動畫面縮放比例變化，不再讀取固定字號，也沒有最小字號跳變。
- 版本號文字固定為純白色 `#FFFFFF`；保留黑色半透明陰影以增強對比。
- 移除 `[splash].version_font_size` 和 `[splash].version_color`；舊設定中的這兩個鍵會被忽略。
- 邊距與陰影偏移依圖片尺寸等比縮放，避免不同解析度下位置偏移。
- 版本更新為 `3.8.3`。

## 24. 3.8.4 增補

- 刪除記憶設定功能：啟動時不再讀取主題、名單、日誌等級、模式、語言、數量或視窗尺寸偏好。
- 主題取 `theme.toml` 的 `default`；語言取 `language.toml` 的 `preferred`；名單、模式、日誌等級與視窗尺寸取 `config.toml`；數量固定從 1 開始。
- 移除 `[app].remember_preferences`、`[window].remember_size`，並刪除視窗尺寸防抖儲存、關閉儲存與啟動還原。
- 記憶檔只保留 `last_results`；舊檔中的 `preferences`、`loaded_config` 在讀取/匯入時被忽略，匯出檔也不再包含它們。
- `lib/OutputView.py` 新增 `SlotOutputView`、`_SlotGrid` 與 `choose_slot_layout()`。
- ScrollMulti 與 ScrollLift 改用固定格子；第一次抽取確定位置，滾動時只更新文字，超長姓名觸發重排並重新鎖定。
- 下一輪抽取、更改數量、重設或匯入結果時清除佈局鎖定。
- 新增固定格子佈局、位置穩定、超長姓名重排與記憶匯出匯入測試。
- 版本更新為 `3.8.4`。

## 25. 3.9.1 增補

- 輸出框 `.ui` 字號由 30 調整為 33，並重新產生 4 個 `lib/ui_*.py`。
- `[ui].display_font_size` 同步改為 33，`BUILTIN_CONFIG` 與 `OutputView` 的 fallback 也改為 33，確保執行時實際生效。
- `tests/` 加入 `.gitignore`，並從新提交取消追蹤；本機測試檔案保留，歷史提交不變。
- 版本更新為 `3.9.1`。

## 26. 3.9.3 增補

- 檢查更新僅在偵測到新版本時啟用「更新」；新增「手動查詢」開啟 Releases 頁面。
- `[update].timeout_ms`（預設 15000）控制 GitHub 請求逾時；修正螢幕與 `QByteArray` 型別問題。
- 姓名排版緊湊化；大螢幕下滾動格子依內容收攏並置中。
- 刪除 `[assets]`、`[paths]`，資源與文件路徑固定於程式碼。
- 日誌等級只過濾檔案輸出；程式日誌視窗顯示目前工作階段全部等級並高亮。
- 模式名稱與識別字統一為 Multi、ScrollMulti、ScrollSingle、Single、Lift、ScrollLift。
- 版本號更新到 3.9.3。

## 27. 3.9.2 增補

- `[window].size_mode` 新增 `maximum`：`_window_is_maximized()` 判斷後跳過尺寸計算，只設最小尺寸；`reveal_window()` 呼叫 `showMaximized()`。重新整理設定時可見視窗立即最大化。
- 四個模式頁在數量欄右側新增縱向 `QSlider`；`_prepare_quantity_slider()` 安裝 `_QuantitySliderTouchFilter`，把觸點縱向位置換算成數值，支援觸控拖動。
- `_set_quantity()` 統一更新數值、標籤、滑動條範圍與滾動控制器；`_refresh_quantity_ranges()` 在切換名單或重新整理設定時夾緊並同步四個模式。
- 新增 `lib/UpdateDialog.py`：以 `QNetworkAccessManager` 非同步查詢 GitHub Releases，`parse_version()`/`is_newer_version()` 比較版本；關閉視窗會中止未完成請求。
- 新增 `ui/Update.ui` 與 `ui/TextViewer.ui`，文字檢視器改用 `.ui`；建置腳本與 CI 遍歷全部 `ui/*.ui`。
- 檢查更新使用 QtNetwork，三個建置設定皆移除 `--nofollow-import-to=PySide6.QtNetwork`。
- 三語新增 `action.check_update`、`update.*` 文案；說明、README、歷史記錄同步到 3.9.2。
- 新增最大化模式、數量夾緊、版本比較測試。

## 28. 3.9.4 增補

- `UpdateDialog` 改用 `QJsonDocument.fromJson()`/`toVariant()` 解析 GitHub 回應，消除 `QByteArray.data()` 的 `memoryview.decode` 型別警告。
- 移除 `json`、`re`、`QFont` 與未使用的 `Qt`；`parse_version()` 改為手寫數字掃描，字型改用現有 `QFont` 副本。
- 快取 GitHub API 與 Releases 的 `QUrl`；更新按鈕狀態、手動查詢與逾時行為不變。
- 全專案 AST 掃描僅發現並移除上述 `Qt` 未使用 import。
- 版本號更新到 3.9.4。

## 29. 3.10.0 發佈說明

- 將 3.9.2–3.9.4 的累積改動合併到 `main`，並以 `3.10.0[upgrade]` 觸發 GitHub Actions 發佈。
- 本版本包含數量滑桿、啟動最大化、檢查更新、姓名緊湊排版、固定資源路徑、完整工作階段日誌高亮與模式名稱標準化。
- 版本號更新到 3.10.0。
