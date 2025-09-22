#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
停止機制單元測試
"""

import unittest
import sys
import os

# 確保能夠匯入專案模組
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestStopMechanism(unittest.TestCase):
    """測試停止機制功能"""

    def setUp(self):
        """測試前準備"""
        try:
            from ai_utils import model_traning
            self.model_traning = model_traning
            # 重設停止標誌
            self.model_traning.reset_stop_training_flag()
        except ImportError as e:
            self.fail(f"無法匯入 model_traning 模組: {e}")

    def test_stop_flag_functions(self):
        """測試停止標誌相關函式"""
        # 測試初始狀態
        self.assertFalse(
            self.model_traning.is_training_stopped(), "初始停止狀態應該是 False")

        # 測試設定停止標誌
        self.model_traning.set_stop_training_flag(True)
        self.assertTrue(
            self.model_traning.is_training_stopped(), "設定後停止狀態應該是 True")

        # 測試重設停止標誌
        self.model_traning.reset_stop_training_flag()
        self.assertFalse(
            self.model_traning.is_training_stopped(), "重設後停止狀態應該是 False")

        # 測試設定為 False
        self.model_traning.set_stop_training_flag(False)
        self.assertFalse(self.model_traning.is_training_stopped(),
                         "設定為 False 後停止狀態應該是 False")

    def test_train_model_stop_early(self):
        """測試訓練函式的早期停止功能"""
        # 設定停止標誌
        self.model_traning.set_stop_training_flag(True)

        # 嘗試執行訓練，應該立即返回 None
        result = self.model_traning.train_model(
            data_path="traning_data/train_data(top20).csv",
            output_path="output_models/test_stop.bin"
        )

        # 訓練應該被停止，返回 None
        self.assertIsNone(result, "當停止標誌為 True 時，訓練應該返回 None")

    def test_hyperparameter_tuning_stop_early(self):
        """測試超參數調優的早期停止功能"""
        # 設定停止標誌
        self.model_traning.set_stop_training_flag(True)

        # 嘗試執行超參數調優，應該立即返回 None
        result = self.model_traning.hyperparameter_tuning(
            data_path="traning_data/train_data(top20).csv"
        )

        # 調優應該被停止，返回 None
        self.assertIsNone(result, "當停止標誌為 True 時，超參數調優應該返回 None")

    def tearDown(self):
        """測試後清理"""
        if hasattr(self, 'model_traning'):
            self.model_traning.reset_stop_training_flag()


def run_stop_mechanism_tests():
    """執行停止機制測試"""
    print("=== 停止機制單元測試 ===")

    # 建立測試套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStopMechanism)

    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 輸出結果摘要
    print(f"\n=== 測試結果摘要 ===")
    print(f"執行測試數: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"錯誤: {len(result.errors)}")

    if result.failures:
        print("\n失敗的測試:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\n錯誤的測試:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_stop_mechanism_tests()
    if success:
        print("\n✅ 所有停止機制測試通過！")
    else:
        print("\n❌ 有停止機制測試失敗！")
        sys.exit(1)
