#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整合測試：驗證實際應用程式的按鈕狀態控制
"""

import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import sys
import os

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 動態匯入避免格式化工具重新排序
traning_app = __import__('traning_app', fromlist=['ModelTrainingApp'])


# 模擬整個 ai_utils 模組以避免載入問題
@patch('traning_app.threading.Thread')
@patch('tkinter.messagebox.showerror')
@patch('tkinter.messagebox.showinfo')
class TestRealAppButtonStates(unittest.TestCase):
    """測試真實應用程式的按鈕狀態控制"""

    def setUp(self):
        """設定測試環境"""
        # 使用 patch 來避免真的載入 GUI
        with patch('traning_app.GuiBuilder'):
            with patch('traning_app.ParameterValidator'):
                with patch('traning_app.ConfigManager'):
                    self.root = tk.Tk()
                    self.root.withdraw()  # 隱藏視窗

                    # 建立應用程式實例
                    self.app = traning_app.ModelTrainingApp(self.root)

                    # 手動建立模擬按鈕
                    self.app.run_button = tk.Button(self.root, text="開始執行")
                    self.app.stop_button = tk.Button(
                        self.root, text="停止執行", state="disabled")
                    self.app.reset_button = tk.Button(self.root, text="重設參數")
                    self.app.import_button = tk.Button(self.root, text="匯入設定")
                    self.app.export_button = tk.Button(self.root, text="匯出設定")
                    self.app.browse_train_data_button = tk.Button(
                        self.root, text="瀏覽訓練資料")
                    self.app.browse_output_folder_button = tk.Button(
                        self.root, text="瀏覽輸出資料夾")

    def tearDown(self):
        """清理測試環境"""
        if self.root:
            self.root.destroy()

    def test_initial_state(self, mock_showinfo, mock_showerror, mock_thread):
        """測試初始狀態"""
        # 檢查初始訓練狀態
        self.assertFalse(self.app.is_training)

        # 檢查初始按鈕狀態
        self.assertEqual(self.app.run_button['state'], 'normal')
        self.assertEqual(self.app.stop_button['state'], 'disabled')
        self.assertEqual(self.app.reset_button['state'], 'normal')
        self.assertEqual(self.app.import_button['state'], 'normal')
        self.assertEqual(self.app.export_button['state'], 'normal')
        self.assertEqual(self.app.browse_train_data_button['state'], 'normal')
        self.assertEqual(
            self.app.browse_output_folder_button['state'], 'normal')

    def test_disable_buttons_method(self, mock_showinfo, mock_showerror, mock_thread):
        """測試禁用按鈕方法"""
        # 執行禁用方法
        self.app._disable_all_buttons_except_stop()

        # 檢查按鈕狀態
        self.assertEqual(self.app.run_button['state'], 'disabled')
        self.assertEqual(self.app.stop_button['state'], 'normal')    # 停止按鈕應該啟用
        self.assertEqual(self.app.reset_button['state'], 'disabled')
        self.assertEqual(self.app.import_button['state'], 'disabled')
        self.assertEqual(self.app.export_button['state'], 'disabled')
        self.assertEqual(
            self.app.browse_train_data_button['state'], 'disabled')
        self.assertEqual(
            self.app.browse_output_folder_button['state'], 'disabled')

    def test_enable_buttons_method(self, mock_showinfo, mock_showerror, mock_thread):
        """測試啟用按鈕方法"""
        # 先禁用所有按鈕
        self.app._disable_all_buttons_except_stop()

        # 再啟用所有按鈕除了停止按鈕
        self.app._enable_all_buttons_except_stop()

        # 檢查按鈕狀態
        self.assertEqual(self.app.run_button['state'], 'normal')
        self.assertEqual(
            self.app.stop_button['state'], 'disabled')   # 停止按鈕應該禁用
        self.assertEqual(self.app.reset_button['state'], 'normal')
        self.assertEqual(self.app.import_button['state'], 'normal')
        self.assertEqual(self.app.export_button['state'], 'normal')
        self.assertEqual(self.app.browse_train_data_button['state'], 'normal')
        self.assertEqual(
            self.app.browse_output_folder_button['state'], 'normal')

    @patch('traning_app.ParameterValidator')
    def test_run_training_button_transition(self, mock_validator_class, mock_showinfo, mock_showerror, mock_thread):
        """測試開始執行時的按鈕狀態轉換"""
        # 模擬驗證器
        mock_validator = MagicMock()
        mock_validator.validate_all_parameters.return_value = []  # 沒有錯誤
        self.app.validator = mock_validator

        # 設定必要的變數
        self.app.target_column.set("test_target")
        self.app.train_data_path.set("test_data.csv")
        self.app.model_output_folder.set("test_output")
        self.app.model_filename.set("test_model.bin")

        # 執行訓練
        self.app.run_training()

        # 檢查訓練狀態
        self.assertTrue(self.app.is_training)

        # 檢查按鈕狀態（應該禁用所有按鈕除了停止按鈕）
        self.assertEqual(self.app.run_button['state'], 'disabled')
        self.assertEqual(
            self.app.stop_button['state'], 'normal')     # 停止按鈕應該啟用
        self.assertEqual(self.app.reset_button['state'], 'disabled')
        self.assertEqual(self.app.import_button['state'], 'disabled')
        self.assertEqual(self.app.export_button['state'], 'disabled')
        self.assertEqual(
            self.app.browse_train_data_button['state'], 'disabled')
        self.assertEqual(
            self.app.browse_output_folder_button['state'], 'disabled')

    def test_stop_training_button_transition(self, mock_showinfo, mock_showerror, mock_thread):
        """測試停止執行時的按鈕狀態轉換"""
        # 設定為訓練中狀態
        self.app.is_training = True
        self.app._disable_all_buttons_except_stop()

        # 執行停止訓練
        self.app.stop_training()

        # 檢查訓練狀態
        self.assertFalse(self.app.is_training)

        # 檢查按鈕狀態（應該恢復所有按鈕正常，停止按鈕禁用）
        self.assertEqual(self.app.run_button['state'], 'normal')
        self.assertEqual(
            self.app.stop_button['state'], 'disabled')   # 停止按鈕應該禁用
        self.assertEqual(self.app.reset_button['state'], 'normal')
        self.assertEqual(self.app.import_button['state'], 'normal')
        self.assertEqual(self.app.export_button['state'], 'normal')
        self.assertEqual(self.app.browse_train_data_button['state'], 'normal')
        self.assertEqual(
            self.app.browse_output_folder_button['state'], 'normal')

    def test_complete_workflow(self, mock_showinfo, mock_showerror, mock_thread):
        """測試完整工作流程的按鈕狀態變化"""
        # 1. 初始狀態檢查
        self.assertFalse(self.app.is_training)
        self.assertEqual(self.app.run_button['state'], 'normal')
        self.assertEqual(self.app.stop_button['state'], 'disabled')

        # 2. 開始執行
        self.app.is_training = True
        self.app._disable_all_buttons_except_stop()

        # 檢查執行中狀態
        self.assertTrue(self.app.is_training)
        self.assertEqual(self.app.run_button['state'], 'disabled')
        self.assertEqual(self.app.stop_button['state'], 'normal')

        # 3. 停止執行
        self.app.is_training = False
        self.app._enable_all_buttons_except_stop()

        # 檢查停止後狀態
        self.assertFalse(self.app.is_training)
        self.assertEqual(self.app.run_button['state'], 'normal')
        self.assertEqual(self.app.stop_button['state'], 'disabled')

    @patch('traning_app.ParameterValidator')
    def test_validation_failure_no_button_change(self, mock_validator_class, mock_showinfo, mock_showerror, mock_thread):
        """測試參數驗證失敗時按鈕狀態不變"""
        # 模擬驗證器返回錯誤
        mock_validator = MagicMock()
        mock_validator.validate_all_parameters.return_value = ["錯誤1", "錯誤2"]
        self.app.validator = mock_validator

        # 記錄初始按鈕狀態
        initial_run_state = self.app.run_button['state']
        initial_stop_state = self.app.stop_button['state']

        # 嘗試執行訓練
        self.app.run_training()

        # 檢查訓練狀態（不應該改變）
        self.assertFalse(self.app.is_training)

        # 檢查按鈕狀態（不應該改變）
        self.assertEqual(self.app.run_button['state'], initial_run_state)
        self.assertEqual(self.app.stop_button['state'], initial_stop_state)

        # 檢查是否顯示錯誤訊息
        mock_showerror.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
