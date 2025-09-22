#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
處理配置檔案的匯入和匯出功能
"""

import os
from .app_constants import PARAM_MAPPING


class ConfigManager:
    """配置管理器類別"""

    def __init__(self, app_instance):
        """
        初始化配置管理器

        Args:
            app_instance: 應用程式實例，用於存取GUI變數
        """
        self.app = app_instance

    def generate_config_code(self):
        """產生配置程式碼"""
        # 處理 exclude_columns 列表
        exclude_cols_str = ""
        if self.app.exclude_columns.get().strip():
            cols_list = [col.strip()
                         for col in self.app.exclude_columns.get().split(',') if col.strip()]
            # 統一使用逗號分隔的字串格式
            exclude_cols_str = f"EXCLUDE_COLUMNS = '{','.join(cols_list)}'"
        else:
            exclude_cols_str = "EXCLUDE_COLUMNS = ''"

        config_code = f"""# 自動產生的參數配置
TARGET_COLUMN = '{self.app.target_column.get()}'
{exclude_cols_str}

# 資料處理參數
TEST_SIZE = {self.app.test_size.get()}
RANDOM_STATE = {self.app.random_state.get()}
SIMILARITY_CUTOFF = {self.app.similarity_cutoff.get()}
CATEGORICAL_THRESHOLD = {self.app.categorical_threshold.get()}
SIMILARITY_MATCHES_COUNT = {self.app.similarity_matches_count.get()}

# 模型參數
MODEL_N_ESTIMATORS = {self.app.model_n_estimators.get()}
MODEL_LEARNING_RATE = {self.app.model_learning_rate.get()}
MODEL_NUM_LEAVES = {self.app.model_num_leaves.get()}
MODEL_SCALE_POS_WEIGHT = {self.app.model_scale_pos_weight.get()}
MODEL_N_JOBS = {self.app.model_n_jobs.get()}
MODEL_VERBOSE = {self.app.model_verbose.get()}

# 超參數調優參數
CV_FOLDS = {self.app.cv_folds.get()}
IMPORTANCE_N_REPEATS = {self.app.importance_n_repeats.get()}
GRID_SEARCH_VERBOSE_BASIC = {self.app.grid_search_verbose_basic.get()}
GRID_SEARCH_VERBOSE_DETAILED = {self.app.grid_search_verbose_detailed.get()}
SCORING_METRIC = '{self.app.scoring_metric.get()}'
IMPORTANCE_SCORING = '{self.app.importance_scoring.get()}'

# 檔案路徑參數
DEFAULT_TRAIN_DATA_PATH = "{self.app.train_data_path.get().replace(chr(92), '/')}"
DEFAULT_MODEL_OUTPUT_PATH = "{os.path.join(self.app.model_output_folder.get(), self.app.model_filename.get()).replace(chr(92), '/')}"
"""
        return config_code

    def export_config(self, filename):
        """
        匯出配置到檔案

        Args:
            filename: 要儲存的檔案名稱

        Returns:
            bool: 是否成功匯出
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.generate_config_code())
            return True
        except Exception as e:
            raise Exception(f"匯出配置時發生錯誤: {str(e)}")

    def import_config(self, filename):
        """
        從檔案匯入配置

        Args:
            filename: 要讀取的檔案名稱

        Returns:
            int: 成功更新的參數數量
        """
        try:
            # 讀取配置檔案
            with open(filename, 'r', encoding='utf-8') as f:
                config_content = f.read()

            # 解析配置內容
            config_dict = {}
            for line in config_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    config_dict[key] = value

            # 更新GUI參數值
            updated_count = 0
            for config_key, (attr_name, _, type_converter) in PARAM_MAPPING.items():
                if config_key in config_dict and hasattr(self.app, attr_name):
                    try:
                        value = type_converter(config_dict[config_key])
                        getattr(self.app, attr_name).set(value)
                        updated_count += 1
                    except (ValueError, TypeError):
                        # 忽略轉換失敗的參數
                        pass

            # 特殊處理檔案路徑
            if 'DEFAULT_MODEL_OUTPUT_PATH' in config_dict:
                full_path = config_dict['DEFAULT_MODEL_OUTPUT_PATH']
                folder = os.path.dirname(full_path)
                model_filename = os.path.basename(full_path)
                if folder:
                    self.app.model_output_folder.set(folder)
                if model_filename:
                    self.app.model_filename.set(model_filename)
                updated_count += 1

            # 特殊處理其他路徑參數
            if 'DEFAULT_TRAIN_DATA_PATH' in config_dict:
                self.app.train_data_path.set(
                    config_dict['DEFAULT_TRAIN_DATA_PATH'])
                updated_count += 1

            if 'TARGET_COLUMN' in config_dict:
                self.app.target_column.set(config_dict['TARGET_COLUMN'])
                updated_count += 1

            if 'EXCLUDE_COLUMNS' in config_dict:
                # 直接使用逗號分隔的字串格式
                exclude_str = config_dict['EXCLUDE_COLUMNS'].strip()
                self.app.exclude_columns.set(exclude_str)
                updated_count += 1

            return updated_count

        except Exception as e:
            raise Exception(f"匯入配置時發生錯誤: {str(e)}")

    def reset_to_defaults(self):
        """重設所有參數為預設值"""
        # 使用映射字典重設參數
        for config_key, (attr_name, default_value, _) in PARAM_MAPPING.items():
            if hasattr(self.app, attr_name):
                getattr(self.app, attr_name).set(default_value)

        # 檔案路徑參數和目標欄位名稱清空
        self.app.train_data_path.set("")
        self.app.target_column.set("")
        self.app.exclude_columns.set("")
        self.app.model_output_folder.set("")
        self.app.model_filename.set("")

        # 運行模式重設
        self.app.run_mode.set("1")
