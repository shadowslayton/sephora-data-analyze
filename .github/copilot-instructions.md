# GitHub Copilot 指令說明

⚠️ **本專案所有操作必須在 `.venv` 虛擬環境下執行**

## 虛擬環境指令

```powershell
# 啟動
.\.venv\Scripts\Activate.ps1

# 停用
deactivate
```

## 必須遵循的規則

1. **工作目錄**：所有操作必須在專案根目錄 `C:\Code\FangYi\sephora-data-analyze` 執行
2. **虛擬環境**：確認終端機顯示 `(.venv)` 前綴
3. **套件安裝**：所有 `pip install` 和 `python` 指令都在虛擬環境內執行
4. **測試要求**：每次修改程式碼或新增功能後，必須執行單元測試

## 測試執行

```powershell
# 執行所有測試
.\.venv\Scripts\python.exe unit_tests\run_all_tests.py

# 執行單個測試
.\.venv\Scripts\python.exe unit_tests\test_exclude_columns.py
.\.venv\Scripts\python.exe unit_tests\test_target_exclude_validation.py
.\.venv\Scripts\python.exe unit_tests\test_gui_validation.py
```

## 單元測試開發

1. **測試位置**：所有測試檔案必須放在 `unit_tests/` 資料夾
2. **檔案命名**：`test_<功能名稱>.py`
3. **必要更新**：新增測試時需同步更新 `unit_tests/README.md`
4. **自動發現**：測試執行器會自動發現所有 `test_*.py` 檔案
