#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試三種執行模式的參數驗證邏輯
專門測試模式1、模式2、模式3的驗證差異
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


class TestExecutionModeValidation(unittest.TestCase):
    """測試三種執行模式的參數驗證"""

    def setUp(self):
        """設定測試環境"""
        class MockVar:
            def __init__(self, value):
                self.value = value

            def get(self):
                return self.value

            def set(self, value):
                self.value = value

        # 創建模擬應用程式
        class MockApp:
            def __init__(self, mode):
                # 基本參數
                self.run_mode = MockVar(mode)
                self.target_column = MockVar("")
                self.exclude_columns = MockVar("")
                self.train_data_path = MockVar("")
                self.model_output_folder = MockVar("")
                self.model_filename = MockVar("")

                # 設定合理的預設數值參數
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

        self.mock_apps = {
            "1": MockApp("1"),
            "2": MockApp("2"),
            "3": MockApp("3")
        }

    def test_mode1_required_parameters(self):
        """測試模式1的必填參數驗證"""
        print("=== 測試模式1必填參數驗證 ===")

        app = self.mock_apps["1"]
        validator = ParameterValidator(app)

        # 測試空參數
        errors = validator.validate_all_parameters()
        required_errors = [e for e in errors if "必填項目" in e]

        self.assertEqual(len(required_errors), 4, "模式1應該有4個必填項目錯誤")

        # 檢查具體的必填項目
        error_text = "\n".join(required_errors)
        self.assertIn("目標欄位", error_text)
        self.assertIn("訓練資料檔案", error_text)
        self.assertIn("模型輸出資料夾", error_text)
        self.assertIn("模型檔案名稱", error_text)

        print("✅ 模式1必填參數驗證正確")

    def test_mode2_required_parameters(self):
        """測試模式2的必填參數驗證"""
        print("=== 測試模式2必填參數驗證 ===")

        app = self.mock_apps["2"]
        validator = ParameterValidator(app)

        # 測試空參數
        errors = validator.validate_all_parameters()
        required_errors = [e for e in errors if "必填項目" in e]

        self.assertEqual(len(required_errors), 2, "模式2應該只有2個必填項目錯誤")

        # 檢查具體的必填項目
        error_text = "\n".join(required_errors)
        self.assertIn("目標欄位", error_text)
        self.assertIn("訓練資料檔案", error_text)
        self.assertNotIn("模型輸出資料夾", error_text)
        self.assertNotIn("模型檔案名稱", error_text)

        print("✅ 模式2必填參數驗證正確")

    def test_mode3_required_parameters(self):
        """測試模式3的必填參數驗證"""
        print("=== 測試模式3必填參數驗證 ===")

        app = self.mock_apps["3"]
        validator = ParameterValidator(app)

        # 測試空參數
        errors = validator.validate_all_parameters()
        required_errors = [e for e in errors if "必填項目" in e]

        self.assertEqual(len(required_errors), 4, "模式3應該有4個必填項目錯誤")

        # 檢查具體的必填項目
        error_text = "\n".join(required_errors)
        self.assertIn("目標欄位", error_text)
        self.assertIn("訓練資料檔案", error_text)
        self.assertIn("模型輸出資料夾", error_text)
        self.assertIn("模型檔案名稱", error_text)

        print("✅ 模式3必填參數驗證正確")

    def test_hyperparameter_tuning_validation(self):
        """測試超參數調優相關的驗證邏輯"""
        print("=== 測試超參數調優參數驗證 ===")

        for mode in ["1", "2", "3"]:
            app = self.mock_apps[mode]

            # 設定有效的基本參數
            app.target_column.set("is_recommended")
            app.train_data_path.set("traning_data/train_data(top20).csv")
            app.model_output_folder.set("output_models")
            app.model_filename.set("model.bin")

            # 設定無效的超參數調優參數
            app.cv_folds.set(0)  # 無效值
            app.importance_n_repeats.set(-1)  # 無效值

            validator = ParameterValidator(app)
            errors = validator.validate_all_parameters()

            tuning_errors = [e for e in errors if any(keyword in e for keyword in
                                                      ["交叉驗證", "特徵重要性"])]

            if mode == "1":
                self.assertEqual(len(tuning_errors), 0,
                                 "模式1不應該驗證超參數調優參數")
                print(f"  模式{mode}: ✅ 正確不驗證調優參數")
            else:
                self.assertGreater(len(tuning_errors), 0,
                                   f"模式{mode}應該驗證超參數調優參數")
                print(f"  模式{mode}: ✅ 正確驗證調優參數 ({len(tuning_errors)} 個錯誤)")

    def test_mode_specific_parameter_isolation(self):
        """測試各模式參數驗證的隔離性"""
        print("=== 測試參數驗證隔離性 ===")

        # 測試模式2不受模型輸出參數影響
        app_mode2 = self.mock_apps["2"]
        app_mode2.target_column.set("is_recommended")
        app_mode2.train_data_path.set("traning_data/train_data(top20).csv")
        # 故意不設定模型輸出參數

        validator = ParameterValidator(app_mode2)
        errors = validator.validate_all_parameters()

        # 模式2應該沒有任何錯誤，因為它不需要模型輸出參數
        self.assertEqual(len(errors), 0, "模式2設定必要參數後應該沒有錯誤")
        print("✅ 模式2參數隔離性正確")

        # 測試模式1受模型輸出參數影響
        app_mode1 = self.mock_apps["1"]
        app_mode1.target_column.set("is_recommended")
        app_mode1.train_data_path.set("traning_data/train_data(top20).csv")
        # 故意不設定模型輸出參數

        validator = ParameterValidator(app_mode1)
        errors = validator.validate_all_parameters()

        model_output_errors = [e for e in errors if "模型" in e and "必填" in e]
        self.assertGreater(len(model_output_errors), 0, "模式1應該要求模型輸出參數")
        print("✅ 模式1參數要求正確")

    def test_parameter_conflict_detection_across_modes(self):
        """測試所有模式都正確檢測參數衝突"""
        print("=== 測試跨模式參數衝突檢測 ===")

        for mode in ["1", "2", "3"]:
            app = self.mock_apps[mode]

            # 設定衝突的參數
            app.target_column.set("is_recommended")
            app.exclude_columns.set("rating,is_recommended,price")
            app.train_data_path.set("traning_data/train_data(top20).csv")
            app.model_output_folder.set("output_models")
            app.model_filename.set("model.bin")

            validator = ParameterValidator(app)
            errors = validator.validate_all_parameters()

            conflict_errors = [e for e in errors if "參數衝突" in e]
            self.assertGreater(len(conflict_errors), 0,
                               f"模式{mode}應該檢測到參數衝突")
            print(f"  模式{mode}: ✅ 正確檢測參數衝突")


def test_execution_mode_validation():
    """主要測試函式"""
    print("🚀 開始測試三種執行模式的參數驗證...")
    unittest.main(verbosity=2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
