#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試應用程式公用程式模組
測試 app_utils 資料夾下的所有公用程式模組功能
"""

import unittest
import sys
import os

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestAppUtilsModules(unittest.TestCase):
    """測試應用程式公用程式模組"""

    def test_module_imports(self):
        """測試所有模組可以正確匯入"""
        try:
            from app_utils.app_constants import PARAM_MAPPING, PARAM_DESCRIPTIONS, BEST_PARAMS_MAPPING
            from app_utils.parameter_validator import ParameterValidator
            from app_utils.config_manager import ConfigManager
            from app_utils.gui_builder import GuiBuilder
            from app_utils.tooltip import ToolTip

            # 檢查常數
            self.assertIsInstance(PARAM_MAPPING, dict)
            self.assertIsInstance(PARAM_DESCRIPTIONS, dict)
            self.assertIsInstance(BEST_PARAMS_MAPPING, dict)

            # 檢查有足夠的參數
            self.assertGreater(len(PARAM_MAPPING), 10)
            self.assertGreater(len(PARAM_DESCRIPTIONS), 10)

            print("✅ 所有模組匯入成功")
            print(f"📊 參數映射項目: {len(PARAM_MAPPING)}")
            print(f"📖 參數說明項目: {len(PARAM_DESCRIPTIONS)}")
            print(f"🎯 最佳參數映射項目: {len(BEST_PARAMS_MAPPING)}")

        except ImportError as e:
            self.fail(f"模組匯入失敗: {e}")

    def test_parameter_validator_class(self):
        """測試參數驗證器類別"""
        from app_utils.parameter_validator import ParameterValidator

        # 模擬應用程式實例
        class MockApp:
            def __init__(self):
                # 創建一些模擬變數
                class MockVar:
                    def __init__(self, value):
                        self.value = value

                    def get(self):
                        return self.value

                self.run_mode = MockVar("1")
                self.target_column = MockVar("test_target")
                self.exclude_columns = MockVar("")
                self.train_data_path = MockVar("")
                self.model_output_folder = MockVar("")
                self.model_filename = MockVar("")

        mock_app = MockApp()
        validator = ParameterValidator(mock_app)

        # 測試驗證函式存在
        self.assertTrue(hasattr(validator, 'validate_float_input'))
        self.assertTrue(hasattr(validator, 'validate_int_input'))
        self.assertTrue(hasattr(validator, 'validate_all_parameters'))

        print("✅ 參數驗證器測試通過")

    def test_config_manager_class(self):
        """測試配置管理器類別"""
        from app_utils.config_manager import ConfigManager

        # 模擬應用程式實例
        class MockApp:
            def __init__(self):
                class MockVar:
                    def __init__(self, value):
                        self.value = value

                    def get(self):
                        return self.value

                    def set(self, value):
                        self.value = value

                # 創建所有需要的變數
                self.target_column = MockVar("test_target")
                self.exclude_columns = MockVar("col1,col2")
                self.test_size = MockVar(0.2)
                self.random_state = MockVar(42)
                self.similarity_cutoff = MockVar(0.6)
                self.categorical_threshold = MockVar(10)
                self.similarity_matches_count = MockVar(1)
                self.model_n_estimators = MockVar(250)
                self.model_learning_rate = MockVar(0.01)
                self.model_num_leaves = MockVar(60)
                self.model_scale_pos_weight = MockVar(0.55)
                self.model_n_jobs = MockVar(-1)
                self.model_verbose = MockVar(0)
                self.cv_folds = MockVar(5)
                self.importance_n_repeats = MockVar(5)
                self.grid_search_verbose_basic = MockVar(2)
                self.grid_search_verbose_detailed = MockVar(3)
                self.scoring_metric = MockVar('f1_macro')
                self.importance_scoring = MockVar('f1_macro')
                self.train_data_path = MockVar("test_data.csv")
                self.model_output_folder = MockVar("output")
                self.model_filename = MockVar("model.bin")

        mock_app = MockApp()
        config_manager = ConfigManager(mock_app)

        # 測試配置程式碼產生
        config_code = config_manager.generate_config_code()
        self.assertIn("TARGET_COLUMN", config_code)
        self.assertIn("EXCLUDE_COLUMNS", config_code)
        self.assertIn("TEST_SIZE", config_code)

        print("✅ 配置管理器測試通過")


if __name__ == '__main__':
    print("🚀 開始測試應用程式公用程式模組...")
    unittest.main(verbosity=2)
