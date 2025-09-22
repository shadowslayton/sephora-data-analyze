#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
參數驗證器
提供所有GUI參數的驗證邏輯
"""

import os


class ParameterValidator:
    """參數驗證器類別"""

    def __init__(self, app_instance):
        """
        初始化驗證器

        Args:
            app_instance: 應用程式實例，用於存取GUI變數
        """
        self.app = app_instance

    def validate_float_input(self, value, widget_name):
        """驗證浮點數輸入"""
        if value == "" or value == "-" or value == ".":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def validate_int_input(self, value, widget_name):
        """驗證整數輸入"""
        if value == "" or value == "-":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False

    def validate_positive_float_input(self, value, widget_name):
        """驗證正浮點數輸入"""
        if value == "" or value == ".":
            return True
        try:
            float_value = float(value)
            return float_value >= 0
        except ValueError:
            return False

    def validate_positive_int_input(self, value, widget_name):
        """驗證正整數輸入"""
        if value == "":
            return True
        try:
            int_value = int(value)
            return int_value >= 0
        except ValueError:
            return False

    def validate_ratio_input(self, value, widget_name):
        """驗證比例輸入 (0-1 之間的浮點數)"""
        if value == "" or value == "0." or value == ".":
            return True
        try:
            float_value = float(value)
            return 0 <= float_value <= 1
        except ValueError:
            return False

    def validate_learning_rate_input(self, value, widget_name):
        """驗證學習率輸入 (0-1 之間的正浮點數)"""
        if value == "" or value == "0." or value == "." or value == "0":
            return True
        try:
            float_value = float(value)
            return 0 <= float_value <= 1
        except ValueError:
            return False

    def validate_n_estimators_input(self, value, widget_name):
        """驗證樹的數量輸入 (1-10000)"""
        if value == "":
            return True
        try:
            int_value = int(value)
            return 1 <= int_value <= 10000
        except ValueError:
            return False

    def validate_num_leaves_input(self, value, widget_name):
        """驗證葉子節點數輸入 (1-1000)"""
        if value == "":
            return True
        try:
            int_value = int(value)
            return 1 <= int_value <= 1000
        except ValueError:
            return False

    def validate_cv_folds_input(self, value, widget_name):
        """驗證交叉驗證折數輸入 (2-20)"""
        if value == "":
            return True
        try:
            int_value = int(value)
            return 2 <= int_value <= 20
        except ValueError:
            return False

    def validate_all_parameters(self):
        """驗證所有參數的合理性"""
        errors = []
        run_mode = self.app.run_mode.get()

        # === 基本必填項目檢查 ===
        # TARGET_COLUMN 必填檢查
        if not self.app.target_column.get().strip():
            errors.append("❌ 必填項目：請輸入目標欄位名稱")

        # 檢查目標欄位與排除欄位的衝突
        target_col = self.app.target_column.get().strip()
        exclude_cols_str = self.app.exclude_columns.get().strip()
        if target_col and exclude_cols_str:
            exclude_cols = [col.strip()
                            for col in exclude_cols_str.split(',') if col.strip()]
            if target_col in exclude_cols:
                errors.append(f"❌ 參數衝突：目標欄位 '{target_col}' 不能同時出現在排除欄位列表中")
                errors.append(f"   排除欄位: {exclude_cols}")
                errors.append(f"   請從排除欄位中移除目標欄位，或者更改目標欄位")

        # 檔案路徑必填檢查
        if not self.app.train_data_path.get().strip():
            errors.append("❌ 必填項目：請選擇訓練資料檔案")
        elif not os.path.exists(self.app.train_data_path.get()):
            errors.append(f"❌ 檔案不存在：{self.app.train_data_path.get()}")

        # 模型輸出相關參數 - 只有訓練模式才需要檢查
        if run_mode in ["1", "3"]:  # 包含模型訓練的模式
            if not self.app.model_output_folder.get().strip():
                errors.append("❌ 必填項目：請選擇模型輸出資料夾")
            elif not os.path.exists(self.app.model_output_folder.get()):
                errors.append(f"❌ 資料夾不存在：{self.app.model_output_folder.get()}")

            if not self.app.model_filename.get().strip():
                errors.append("❌ 必填項目：請輸入模型檔案名稱")

        # === 數值範圍檢查 ===
        # 資料處理參數
        if not (0 < self.app.test_size.get() < 1):
            errors.append("❌ 測試集比例必須在 0 和 1 之間")

        if self.app.random_state.get() < 0:
            errors.append("❌ 隨機種子必須大於等於 0")

        if not (0 < self.app.similarity_cutoff.get() <= 1):
            errors.append("❌ 相似度閾值必須在 0 和 1 之間")

        if self.app.categorical_threshold.get() <= 0:
            errors.append("❌ 類別數量閾值必須大於 0")

        if self.app.similarity_matches_count.get() <= 0:
            errors.append("❌ 模糊匹配返回數量必須大於 0")

        # 模型參數
        if self.app.model_n_estimators.get() <= 0:
            errors.append("❌ 樹的數量必須大於 0")
        elif self.app.model_n_estimators.get() > 10000:
            errors.append("⚠️ 警告：樹的數量過大可能導致訓練時間過長")

        if self.app.model_learning_rate.get() <= 0:
            errors.append("❌ 學習率必須大於 0")
        elif self.app.model_learning_rate.get() > 1:
            errors.append("⚠️ 警告：學習率過大可能導致訓練不穩定")

        if self.app.model_num_leaves.get() <= 0:
            errors.append("❌ 葉子節點數必須大於 0")
        elif self.app.model_num_leaves.get() > 1000:
            errors.append("⚠️ 警告：葉子節點數過大可能導致過擬合")

        if self.app.model_scale_pos_weight.get() <= 0:
            errors.append("❌ 正例權重必須大於 0")

        # === 運行模式特定驗證 ===
        if run_mode in ["2", "3"]:  # 包含超參數調優的模式
            if self.app.cv_folds.get() <= 1:
                errors.append("❌ 交叉驗證折數必須大於 1")
            elif self.app.cv_folds.get() > 20:
                errors.append("⚠️ 警告：交叉驗證折數過大會顯著增加訓練時間")

            if self.app.importance_n_repeats.get() <= 0:
                errors.append("❌ 特徵重要性重複次數必須大於 0")
            elif self.app.importance_n_repeats.get() > 50:
                errors.append("⚠️ 警告：重複次數過大會顯著增加計算時間")

            if self.app.grid_search_verbose_basic.get() < 0:
                errors.append("❌ 網格搜尋詳細程度-基本必須大於等於 0")

            if self.app.grid_search_verbose_detailed.get() < 0:
                errors.append("❌ 網格搜尋詳細程度-詳細必須大於等於 0")

        # === 檔案格式檢查 ===
        if self.app.train_data_path.get().strip() and not self.app.train_data_path.get().lower().endswith('.csv'):
            errors.append("⚠️ 警告：訓練資料檔案建議使用 .csv 格式")

        if self.app.model_filename.get().strip() and not any(self.app.model_filename.get().lower().endswith(ext)
                                                             for ext in ['.bin', '.pkl', '.joblib', '.model']):
            errors.append("⚠️ 警告：模型檔案建議使用 .bin, .pkl, .joblib 或 .model 副檔名")

        # === 效能建議 ===
        if (self.app.model_n_estimators.get() > 1000 and
            self.app.model_num_leaves.get() > 100 and
                self.app.model_n_jobs.get() == 1):
            errors.append("💡 建議：參數較大時建議使用多核心處理 (N_JOBS = -1)")

        return errors
