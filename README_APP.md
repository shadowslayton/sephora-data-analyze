# Sephora 產品推薦模型訓練器

## 檔案說明

- `traning_app.py` - GUI 圖形化介面應用程式
- `ai_utils/model_traning.py` - 核心模型訓練程式碼
- `README_APP.md` - 本說明檔案

## 使用方法

### 1. 建立虛擬環境

#### Windows 環境

```powershell
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 安裝相依套件
pip install -r requirements.txt
```

#### macOS/Linux 環境

```bash
# 建立虛擬環境
python3 -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate

# 安裝相依套件
pip install -r requirements.txt
```

### 2. 開發環境啟動

#### Windows

```powershell
.\.venv\Scripts\Activate.ps1
python traning_app.py
```

#### macOS/Linux

```bash
source .venv/bin/activate
python3 traning_app.py
```

### 3. 單元測試

#### Windows

```powershell
.\.venv\Scripts\Activate.ps1
python unit_tests\run_all_tests.py
```

#### macOS/Linux

```bash
source .venv/bin/activate
python3 unit_tests/run_all_tests.py
```

### 4. 設定參數

應用程式提供單一頁面的參數設定，分為四個區塊：

#### 基本設定參數

- **目標欄位名稱** (TARGET_COLUMN): 必填，指定資料中哪個欄位作為預測目標，如 "is_recommended"
- **排除欄位** (EXCLUDE_COLUMNS): 排除高相關度欄位，用逗號分隔，如 "rating" (相關度 0.885)

#### 資料處理參數

- **測試集比例** (TEST_SIZE): 預設 0.2，測試集佔總資料的比例
- **隨機種子** (RANDOM_STATE): 預設 42，確保結果可重現
- **相似度閾值** (SIMILARITY_CUTOFF): 預設 0.6，判斷兩個項目是否相似的閾值
- **類別數量閾值** (CATEGORICAL_THRESHOLD): 預設 10，高維度類別特徵的唯一值數量閾值
- **模糊匹配返回數量** (SIMILARITY_MATCHES_COUNT): 預設 1，模糊匹配返回的候選項目數量

#### 模型參數

- **樹的數量** (MODEL_N_ESTIMATORS): 預設 250，決策樹的數量
- **學習率** (MODEL_LEARNING_RATE): 預設 0.01，控制模型更新的步長
- **葉子節點數** (MODEL_NUM_LEAVES): 預設 60，每棵樹的最大葉子節點數
- **正例權重** (MODEL_SCALE_POS_WEIGHT): 預設 0.55，用於處理不平衡資料集的正例權重
- **並行工作數** (MODEL_N_JOBS): 預設 -1，-1 表示使用所有 CPU 核心
- **詳細程度** (MODEL_VERBOSE): 預設 0，訓練過程輸出詳細程度 (-1:靜默, 0:警告, 1:資訊, 2:除錯)

#### 超參數調優參數

- **交叉驗證折數** (CV_FOLDS): 預設 5，交叉驗證的折數
- **特徵重要性重複次數** (IMPORTANCE_N_REPEATS): 預設 5，特徵重要性計算的重複次數
- **網格搜尋詳細程度-基本** (GRID_SEARCH_VERBOSE_BASIC): 預設 2，基本網格搜尋的輸出詳細程度
- **網格搜尋詳細程度-詳細** (GRID_SEARCH_VERBOSE_DETAILED): 預設 3，詳細網格搜尋的輸出詳細程度
- **主要評分指標** (SCORING_METRIC): 預設 f1_macro，主要評分指標
- **特徵重要性評分** (IMPORTANCE_SCORING): 預設 f1_macro，特徵重要性計算使用的評分指標

#### 檔案路徑參數

- **訓練資料路徑** (TRAIN_DATA_PATH): 訓練資料檔案的完整路徑，支援 CSV 格式
- **模型輸出資料夾** (MODEL_OUTPUT_FOLDER): 模型檔案的儲存資料夾
- **模型檔案名稱** (MODEL_FILENAME): 儲存的模型檔案名稱，建議使用 .bin 或 .pkl 副檔名

### 5. 運行模式

1. **僅訓練模型**: 使用目前參數直接訓練
2. **僅超參數調優**: 只進行參數最佳化
3. **超參數優調並訓練模型**: 先調優再訓練

### 6. 執行與管理

- **開始執行**: 執行選定的訓練模式
- **停止執行**: 中止進行中的訓練
- **重設參數**: 恢復預設值
- **匯入/匯出設定**: 儲存和載入參數配置

## 重要提醒

### 環境設定

1. **Python 版本**: 建議使用 Python 3.8 或以上版本
2. **虛擬環境**: 必須在 `.venv` 虛擬環境下執行，避免套件衝突
3. **相依套件**: 確保所有 requirements.txt 中的套件都已正確安裝
4. **TARGET_COLUMN**: 必填欄位，指定預測目標，需要包含二元分類值（0/1 或 True/False）
5. **EXCLUDE_COLUMNS**: 排除與目標欄位高度相關的欄位避免資料洩漏，用逗號分隔多個欄位
6. **檔案路徑**: 確保所有路徑正確且有權限存取，訓練資料需為 CSV 格式

## 檔案結構

```
sephora-data-analyze/
├── traning_app.py              # 主程式
├── app_utils/                  # GUI 模組
├── ai_utils/                   # AI 訓練模組
├── requirements.txt            # Python 相依套件清單
├── .venv/                      # 虛擬環境（需要建立）
├── traning_data/               # 訓練資料目錄
└── output_models/              # 模型輸出目錄
```

## 錯誤排除

### 環境問題

- **虛擬環境未啟動**: 確認終端機顯示 `(.venv)` 前綴
- **套件缺失**: 執行 `pip install -r requirements.txt` 安裝所有相依套件
- **Python 版本**: 確保使用 Python 3.8 或以上版本
- **權限問題**: 確認對專案資料夾有讀寫權限

### 應用程式問題

- **GUI 無法啟動**: 檢查 tkinter 是否正確安裝
- **模組匯入錯誤**: 確認所有 app_utils 和 ai_utils 模組檔案存在
- **檔案路徑錯誤**: 確保訓練資料檔案路徑正確且檔案存在
- **記憶體不足**: 大型資料集可能需要更多記憶體

### 訓練問題

- **資料載入失敗**: 檢查 CSV 檔案格式和編碼
- **目標欄位錯誤**: 確認 TARGET_COLUMN 欄位名稱正確
- **參數驗證失敗**: 檢查 Console 視窗的詳細錯誤訊息
- **訓練中斷**: 檢查資料品質和參數設定

### 常見解決方案

```bash
# 重新安裝相依套件
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 清理 Python 快取
find . -type d -name "__pycache__" -delete
find . -name "*.pyc" -delete

# 重新啟動虛擬環境
deactivate
source .venv/bin/activate  # macOS/Linux
# 或
.\.venv\Scripts\Activate.ps1  # Windows
```
