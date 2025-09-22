#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
應用程式常數定義
包含參數映射、說明文字等常數
"""

# 參數映射字典：配置名稱 -> (GUI屬性名, 預設值, 類型轉換器)
PARAM_MAPPING = {
    # 基本設定參數
    'TARGET_COLUMN': ('target_column', '', str),
    'EXCLUDE_COLUMNS': ('exclude_columns', '', str),

    # 資料處理參數
    'TEST_SIZE': ('test_size', 0.2, float),
    'RANDOM_STATE': ('random_state', 42, int),
    'SIMILARITY_CUTOFF': ('similarity_cutoff', 0.6, float),
    'CATEGORICAL_THRESHOLD': ('categorical_threshold', 10, int),
    'SIMILARITY_MATCHES_COUNT': ('similarity_matches_count', 1, int),

    # 模型參數
    'MODEL_N_ESTIMATORS': ('model_n_estimators', 250, int),
    'MODEL_LEARNING_RATE': ('model_learning_rate', 0.01, float),
    'MODEL_NUM_LEAVES': ('model_num_leaves', 60, int),
    'MODEL_SCALE_POS_WEIGHT': ('model_scale_pos_weight', 0.55, float),
    'MODEL_N_JOBS': ('model_n_jobs', -1, int),
    'MODEL_VERBOSE': ('model_verbose', 0, int),

    # 超參數調優參數
    'CV_FOLDS': ('cv_folds', 5, int),
    'IMPORTANCE_N_REPEATS': ('importance_n_repeats', 5, int),
    'GRID_SEARCH_VERBOSE_BASIC': ('grid_search_verbose_basic', 2, int),
    'GRID_SEARCH_VERBOSE_DETAILED': ('grid_search_verbose_detailed', 3, int),
    'SCORING_METRIC': ('scoring_metric', 'f1_macro', str),
    'IMPORTANCE_SCORING': ('importance_scoring', 'f1_macro', str),

    # 檔案路徑參數
    'DEFAULT_TRAIN_DATA_PATH': ('train_data_path', 'traning_data/train_data(top20).csv', str),
    'MODEL_OUTPUT_FOLDER': ('model_output_folder', 'output_models', str),
    'MODEL_FILENAME': ('model_filename', 'model_final.bin', str),
}

# 參數說明字典
PARAM_DESCRIPTIONS = {
    # 基本設定參數
    'TARGET_COLUMN': '目標欄位名稱，指定資料中哪個欄位作為預測目標（標籤）。需要手動指定，例如 "is_recommended"。此欄位應包含二元分類值（0/1 或 True/False），用於訓練分類模型。',
    'EXCLUDE_COLUMNS': '要排除的欄位列表，用逗號分隔。主要目標是排除與目標欄位相關度過高的欄位，避免資料洩漏和模型過度擬合。例如：rating 與 is_recommended 相關度 0.885，應排除。格式："rating,product_id"',

    # 資料處理參數
    'TEST_SIZE': '測試集佔總資料的比例，用於評估模型效能。建議值 0.2-0.3，表示 20%-30% 資料用於測試。',
    'RANDOM_STATE': '隨機種子，確保結果可重現。設定相同數值可獲得一致的訓練結果。',
    'SIMILARITY_CUTOFF': '相似度閾值，用於判斷兩個項目是否相似。數值越高表示要求更高的相似度。',
    'CATEGORICAL_THRESHOLD': '類別特徵的唯一值數量閾值。超過此數量的特徵會被視為高維度類別特徵。',
    'SIMILARITY_MATCHES_COUNT': '模糊匹配時返回的候選項目數量。數值越大搜尋越廣泛但計算時間增加。',

    # 模型參數
    'MODEL_N_ESTIMATORS': '決策樹的數量。數值越大模型越複雜，準確度可能提升但訓練時間增加。建議範圍 100-1000。',
    'MODEL_LEARNING_RATE': '學習率，控制模型更新的步長。數值越小學習越穩定但需要更多樹。建議範圍 0.01-0.3。',
    'MODEL_NUM_LEAVES': '每棵樹的最大葉子節點數。控制模型複雜度，數值越大越容易過擬合。建議範圍 20-100。',
    'MODEL_SCALE_POS_WEIGHT': '正例權重，用於處理不平衡資料集。數值越大越重視正例（推薦項目）的預測。',
    'MODEL_N_JOBS': '並行處理的工作數。-1 表示使用所有 CPU 核心，1 表示單執行緒。',
    'MODEL_VERBOSE': '訓練過程中的輸出詳細程度。-1:靜默，0:警告，1:資訊，2:除錯。',

    # 超參數調優參數
    'CV_FOLDS': '交叉驗證的折數。將資料分成 n 份進行驗證，提高評估可靠性。建議 3-10 折。',
    'IMPORTANCE_N_REPEATS': '特徵重要性計算的重複次數。重複越多結果越穩定但計算時間增加。',
    'GRID_SEARCH_VERBOSE_BASIC': '基本網格搜尋的輸出詳細程度。數值越大輸出越詳細。',
    'GRID_SEARCH_VERBOSE_DETAILED': '詳細網格搜尋的輸出詳細程度。用於深度調優時的詳細資訊。',
    'SCORING_METRIC': '主要評分指標。f1_macro:平衡準確率和召回率，roc_auc:分類效能，balanced_accuracy:平衡準確度。',
    'IMPORTANCE_SCORING': '特徵重要性計算使用的評分指標。選擇與主要評分指標一致的指標。',

    # 檔案路徑參數
    'TRAIN_DATA_PATH': '訓練資料檔案的完整路徑。支援 CSV 格式，確保檔案包含所需的特徵欄位。',
    'MODEL_OUTPUT_FOLDER': '模型檔案的儲存資料夾。確保有足夠的磁碟空間和寫入權限。',
    'MODEL_FILENAME': '儲存的模型檔案名稱。建議使用 .bin 或 .pkl 副檔名。'
}

# 超參數自動回填的參數映射
BEST_PARAMS_MAPPING = {
    'model__n_estimators': ('model_n_estimators', 'int'),
    'model__learning_rate': ('model_learning_rate', 'float'),
    'model__num_leaves': ('model_num_leaves', 'int'),
    'model__scale_pos_weight': ('model_scale_pos_weight', 'float'),
    'model__reg_alpha': ('model_reg_alpha', 'float')  # 如果有的話
}
