# Unit Tests 單元測試資料夾

## 📊 測試覆蓋總覽

### ✅ 所有測試檔案 (16 個)

1. **`test_additional_app_features.py`** - 額外應用程式功能測試
2. **`test_app_button_integration.py`** - 應用程式按鈕整合測試
3. **`test_app_core_functions.py`** - 核心應用程式功能測試
4. **`test_app_utils_modules.py`** - 公用程式模組測試
5. **`test_auto_fill_params.py`** - 超參數自動回填測試
6. **`test_button_control.py`** - 按鈕控制功能測試（整合版）
7. **`test_button_control_simple.py`** - 按鈕控制邏輯測試（簡化版）
8. **`test_button_state_logic.py`** - 按鈕狀態控制邏輯測試
9. **`test_config_and_error_handling.py`** - 配置管理和錯誤處理測試
10. **`test_exclude_columns.py`** - 排除欄位功能測試
11. **`test_execution_mode_validation.py`** - 執行模式驗證測試
12. **`test_gui_validation.py`** - GUI 驗證測試
13. **`test_parameter_validator_details.py`** - 參數驗證器詳細測試
14. **`test_stop_mechanism.py`** - 停止機制功能測試
15. **`test_target_exclude_validation.py`** - 目標欄位防呆機制測試
16. **`test_tooltip_gui_builder.py`** - 工具提示和 GUI 建構器測試

## 📁 詳細測試說明

### `test_exclude_columns.py`

測試排除欄位功能：單個欄位排除、多個欄位排除、資料洩漏問題解決

### `test_target_exclude_validation.py`

測試防呆機制：目標欄位與排除欄位衝突檢測、邊界情況處理

### `test_gui_validation.py`

測試 GUI 驗證：參數驗證邏輯、輸入處理、錯誤訊息

### `test_button_control.py` - 按鈕控制整合測試

測試按鈕控制功能的核心邏輯：模擬物件測試、方法驗證、狀態轉換邏輯、None 按鈕安全處理

### `test_button_control_simple.py` - 按鈕控制邏輯測試

測試按鈕控制邏輯核心功能：模擬按鈕物件、狀態轉換邏輯、邊界情況處理、多次操作測試

**🔧 特色**：兩個測試檔案都避免實體檔案產生，專注於邏輯驗證

### `test_auto_fill_params.py`

測試超參數調優自動回填功能：參數映射、類型轉換、GUI 更新

### `test_app_utils_modules.py` - 公用程式模組測試

測試應用程式公用程式模組：模組匯入、參數驗證器、配置管理器、GUI 建構器

### `test_app_core_functions.py` - 核心功能測試

測試 traning_app.py 的核心應用程式功能：應用程式初始化、檔案瀏覽、狀態更新、UI 控制、配置匯出

### `test_config_and_error_handling.py` - 配置和錯誤處理測試

測試配置管理和錯誤處理：配置匯入、錯誤處理、邊界情況、參數回填錯誤處理

### `test_additional_app_features.py` - 額外功能測試

測試額外應用程式功能：配置檔案操作、參數驗證整合、GUI 建構器整合、狀態管理

### `test_execution_mode_validation.py` - 執行模式驗證測試

測試三種執行模式的參數驗證：

- 模式 1：僅訓練模型
- 模式 2：僅超參數調優
- 模式 3：超參數調優 + 訓練模型

### `test_parameter_validator_details.py` - 參數驗證器詳細測試

詳細測試參數驗證功能：

- 邊界值驗證
- 型別驗證（整數、浮點數、比例）
- 負數檢測
- 學習率和樹數量特殊驗證

### `test_tooltip_gui_builder.py` - 工具提示和 GUI 建構器測試

測試 GUI 相關功能：

- 工具提示創建和文字編碼
- GUI 建構器初始化和方法存在性
- 參數說明完整性和品質
- GUI 元件配置

### `run_all_tests.py`

統一測試執行器：自動發現並執行所有測試，生成執行報告

### `test_button_state_logic.py` - 按鈕狀態控制邏輯測試

測試按鈕狀態控制邏輯核心功能：

- 禁用/啟用按鈕邏輯驗證
- 按鈕列表完整性檢查
- 停止按鈕特殊行為測試
- 完整工作流程按鈕狀態變化

### `test_app_button_integration.py` - 應用程式按鈕整合測試

測試真實應用程式的按鈕狀態控制：

- 初始按鈕狀態檢查
- 開始/停止執行的按鈕轉換
- 參數驗證失敗時的按鈕行為
- 完整執行工作流程驗證

## 🚀 重構成果

### 新模組架構

```
app_utils/
├── __init__.py              # 模組初始化
├── app_constants.py         # 應用程式常數定義
├── tooltip.py               # 工具提示元件
├── parameter_validator.py   # 參數驗證器
├── config_manager.py        # 配置管理器
└── gui_builder.py          # GUI 建構器
```

### 改進項目

- ✅ **模組化設計**：將 900+ 行程式碼拆分成多個專門模組
- ✅ **職責分離**：每個模組有明確的單一職責
- ✅ **可維護性提升**：程式碼結構更清晰，易於維護和擴展
- ✅ **測試覆蓋**：每個模組都有對應的單元測試
- ✅ **執行模式專業測試**：針對三種執行模式的完整驗證
- ✅ **詳細參數驗證**：包含邊界值、型別檢查等專業測試

## 🧪 執行測試

⚠️ **必須在專案根目錄和虛擬環境執行**

```powershell
# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 執行所有測試
.\.venv\Scripts\python.exe unit_tests\run_all_tests.py

# 執行單個測試範例
.\.venv\Scripts\python.exe unit_tests\test_exclude_columns.py
.\.venv\Scripts\python.exe unit_tests\test_execution_mode_validation.py
.\.venv\Scripts\python.exe unit_tests\test_parameter_validator_details.py
```

## 📈 測試統計

- **總測試檔案數**：15 個
- **所有測試都能正常執行**：100% 成功率
- **測試函式總數**：95+ 個測試案例
- **覆蓋範圍**：核心功能、模組化架構、執行模式、參數驗證、GUI 功能、按鈕控制、檔案操作、錯誤處理、按鈕狀態管理

## 🛠️ 新增測試

1. **檔案命名**：`test_<功能名稱>.py`
2. **放置位置**：`unit_tests/` 資料夾
3. **更新文件**：修改本 README.md 新增測試說明
4. **自動發現**：`run_all_tests.py` 會自動發現新測試

### 測試模板

```python
#!/usr/bin/env python3
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

### `test_stop_mechanism.py` - 停止機制功能測試

測試訓練過程的停止機制：
- **停止標誌管理**：設定、檢查、重設停止標誌
- **早期停止功能**：在訓練各階段檢查停止請求
- **`train_model` 停止**：測試模型訓練的早期停止
- **`hyperparameter_tuning` 停止**：測試超參數調優的早期停止

**🛡️ 特色**：防止長時間訓練任務無法停止的問題

### `test_tooltip_gui_builder.py`

def test_your_function():
    print("=== 測試開始 ===")
    # 測試程式碼
    print("=== 測試完成 ===")

if __name__ == "__main__":
    test_your_function()
```
