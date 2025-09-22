#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試參數驗證器的詳細功能
包含各種邊界值和無效輸入的測試
"""

import unittest
import sys
import os

# 添加專案根目錄到路徑（必須在 import app_utils 之前）
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 動態 import，避免被格式化工具干擾
ParameterValidator = __import__('app_utils.parameter_validator', fromlist=[
                                'ParameterValidator']).ParameterValidator


class TestParameterValidatorDetails(unittest.TestCase):
    """測試參數驗證器的詳細功能"""

    def setUp(self):
        """設定測試環境"""
        class MockVar:
            def __init__(self, value):
                self.value = value

            def get(self):
                return self.value

        class MockApp:
            def __init__(self):
                self.run_mode = MockVar("1")
                self.target_column = MockVar("is_recommended")
                self.exclude_columns = MockVar("")
                self.train_data_path = MockVar(
                    "traning_data/train_data(top20).csv")
                self.model_output_folder = MockVar("output_models")
                self.model_filename = MockVar("model.bin")

                # 可變的參數用於測試
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

        self.app = MockApp()
        self.validator = ParameterValidator(self.app)

    def test_float_input_validation(self):
        """測試浮點數輸入驗證"""
        print("=== 測試浮點數輸入驗證 ===")

        # 有效輸入
        valid_inputs = ["0.5", "1.0", "0", "123.456", "-1.5", ".", ""]
        for value in valid_inputs:
            result = self.validator.validate_float_input(value, "test")
            self.assertTrue(result, f"'{value}' 應該是有效的浮點數輸入")

        # 無效輸入
        invalid_inputs = ["abc", "1.2.3", "1e", "∞"]
        for value in invalid_inputs:
            result = self.validator.validate_float_input(value, "test")
            self.assertFalse(result, f"'{value}' 應該是無效的浮點數輸入")

        print("✅ 浮點數輸入驗證測試通過")

    def test_int_input_validation(self):
        """測試整數輸入驗證"""
        print("=== 測試整數輸入驗證 ===")

        # 有效輸入
        valid_inputs = ["123", "0", "-1", "", "-"]
        for value in valid_inputs:
            result = self.validator.validate_int_input(value, "test")
            self.assertTrue(result, f"'{value}' 應該是有效的整數輸入")

        # 無效輸入
        invalid_inputs = ["1.5", "abc", "1e5", "∞"]
        for value in invalid_inputs:
            result = self.validator.validate_int_input(value, "test")
            self.assertFalse(result, f"'{value}' 應該是無效的整數輸入")

        print("✅ 整數輸入驗證測試通過")

    def test_ratio_input_validation(self):
        """測試比例輸入驗證"""
        print("=== 測試比例輸入驗證 ===")

        # 有效輸入
        valid_inputs = ["0", "0.5", "1.0", "0.999", "", "0.", "."]
        for value in valid_inputs:
            result = self.validator.validate_ratio_input(value, "test")
            self.assertTrue(result, f"'{value}' 應該是有效的比例輸入")

        # 無效輸入
        invalid_inputs = ["-0.1", "1.1", "2", "abc"]
        for value in invalid_inputs:
            result = self.validator.validate_ratio_input(value, "test")
            self.assertFalse(result, f"'{value}' 應該是無效的比例輸入")

        print("✅ 比例輸入驗證測試通過")

    def test_learning_rate_validation(self):
        """測試學習率驗證"""
        print("=== 測試學習率驗證 ===")

        # 有效輸入
        valid_inputs = ["0.01", "0.1", "1.0", "0", "", "0.", "."]
        for value in valid_inputs:
            result = self.validator.validate_learning_rate_input(value, "test")
            self.assertTrue(result, f"'{value}' 應該是有效的學習率")

        # 無效輸入
        invalid_inputs = ["-0.01", "1.1", "2", "abc"]
        for value in invalid_inputs:
            result = self.validator.validate_learning_rate_input(value, "test")
            self.assertFalse(result, f"'{value}' 應該是無效的學習率")

        print("✅ 學習率驗證測試通過")

    def test_n_estimators_validation(self):
        """測試樹的數量驗證"""
        print("=== 測試樹的數量驗證 ===")

        # 有效輸入
        valid_inputs = ["1", "100", "1000", "10000", ""]
        for value in valid_inputs:
            result = self.validator.validate_n_estimators_input(value, "test")
            self.assertTrue(result, f"'{value}' 應該是有效的樹的數量")

        # 無效輸入
        invalid_inputs = ["0", "-1", "10001", "1.5", "abc"]
        for value in invalid_inputs:
            result = self.validator.validate_n_estimators_input(value, "test")
            self.assertFalse(result, f"'{value}' 應該是無效的樹的數量")

        print("✅ 樹的數量驗證測試通過")

    def test_boundary_value_validation(self):
        """測試邊界值驗證"""
        print("=== 測試邊界值驗證 ===")

        # 測試測試集比例邊界值
        self.app.test_size.value = 0.0001  # 接近0
        errors = self.validator.validate_all_parameters()
        size_errors = [e for e in errors if "測試集比例" in e]
        self.assertEqual(len(size_errors), 0, "0.0001應該是有效的測試集比例")

        self.app.test_size.value = 0.9999  # 接近1
        errors = self.validator.validate_all_parameters()
        size_errors = [e for e in errors if "測試集比例" in e]
        self.assertEqual(len(size_errors), 0, "0.9999應該是有效的測試集比例")

        self.app.test_size.value = 0  # 邊界無效值
        errors = self.validator.validate_all_parameters()
        size_errors = [e for e in errors if "測試集比例" in e]
        self.assertGreater(len(size_errors), 0, "0應該是無效的測試集比例")

        self.app.test_size.value = 1  # 邊界無效值
        errors = self.validator.validate_all_parameters()
        size_errors = [e for e in errors if "測試集比例" in e]
        self.assertGreater(len(size_errors), 0, "1應該是無效的測試集比例")

        print("✅ 邊界值驗證測試通過")

    def test_negative_value_validation(self):
        """測試負數值驗證"""
        print("=== 測試負數值驗證 ===")

        # 測試不允許負數的參數
        negative_test_params = [
            ('categorical_threshold', '類別數量閾值'),
            ('similarity_matches_count', '模糊匹配返回數量'),
            ('model_n_estimators', '樹的數量'),
            ('model_learning_rate', '學習率'),
            ('model_num_leaves', '葉子節點數'),
            ('model_scale_pos_weight', '正例權重')
        ]

        for param_name, error_keyword in negative_test_params:
            # 重置為有效值
            self.app.test_size.value = 0.2

            # 設定負值
            getattr(self.app, param_name).value = -1

            errors = self.validator.validate_all_parameters()
            param_errors = [e for e in errors if error_keyword in e]
            self.assertGreater(len(param_errors), 0,
                               f"{param_name} 不應該接受負值")

            # 恢復正值
            getattr(self.app, param_name).value = 1

        print("✅ 負數值驗證測試通過")

    def test_warning_generation(self):
        """測試參數範圍檢查（替代警告功能）"""
        print("=== 測試參數範圍檢查 ===")

        # 測試有效範圍內的值不產生錯誤
        self.app.model_n_estimators.value = 250  # 正常值
        self.app.model_learning_rate.value = 0.01  # 正常值
        errors = self.validator.validate_all_parameters()

        # 由於缺少必填項目，會有錯誤，但不應有關於這些參數的錯誤
        n_estimators_errors = [e for e in errors if "樹的數量" in e]
        learning_rate_errors = [e for e in errors if "學習率" in e]

        self.assertEqual(len(n_estimators_errors), 0, "正常的樹數量不應該產生錯誤")
        self.assertEqual(len(learning_rate_errors), 0, "正常的學習率不應該產生錯誤")

        print("✅ 參數範圍檢查測試通過")


def test_parameter_validator_details():
    """主要測試函式"""
    print("🚀 開始測試參數驗證器詳細功能...")
    unittest.main(verbosity=2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
