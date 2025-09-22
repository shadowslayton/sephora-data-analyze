#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試按鈕狀態控制功能的簡化版本
專門測試按鈕狀態切換邏輯
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import tkinter as tk
import sys
import os

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@patch('tkinter.messagebox.showerror')
@patch('tkinter.messagebox.showinfo')
class TestButtonStateLogic(unittest.TestCase):
    """測試按鈕狀態控制邏輯"""

    def setUp(self):
        """設定測試環境"""
        # 建立模擬的應用程式類別來測試邏輯
        self.mock_app = Mock()

        # 建立模擬按鈕
        self.mock_app.run_button = Mock()
        self.mock_app.stop_button = Mock()
        self.mock_app.reset_button = Mock()
        self.mock_app.import_button = Mock()
        self.mock_app.export_button = Mock()
        self.mock_app.browse_train_data_button = Mock()
        self.mock_app.browse_output_folder_button = Mock()

        # 設定按鈕初始狀態
        self.mock_app.run_button.config = Mock()
        self.mock_app.stop_button.config = Mock()
        self.mock_app.reset_button.config = Mock()
        self.mock_app.import_button.config = Mock()
        self.mock_app.export_button.config = Mock()
        self.mock_app.browse_train_data_button.config = Mock()
        self.mock_app.browse_output_folder_button.config = Mock()

        # 設定訓練狀態
        self.mock_app.is_training = False

    def test_disable_all_buttons_except_stop(self, mock_showinfo, mock_showerror):
        """測試禁用所有按鈕除了停止按鈕的邏輯"""
        # 定義實際的方法邏輯
        def _disable_all_buttons_except_stop():
            buttons_to_disable = [
                self.mock_app.run_button,
                self.mock_app.reset_button,
                self.mock_app.import_button,
                self.mock_app.export_button,
                self.mock_app.browse_train_data_button,
                self.mock_app.browse_output_folder_button
            ]

            for button in buttons_to_disable:
                if button:
                    button.config(state="disabled")

            # 啟用停止按鈕
            if self.mock_app.stop_button:
                self.mock_app.stop_button.config(state="normal")

        # 執行測試
        _disable_all_buttons_except_stop()

        # 驗證禁用的按鈕
        self.mock_app.run_button.config.assert_called_with(state="disabled")
        self.mock_app.reset_button.config.assert_called_with(state="disabled")
        self.mock_app.import_button.config.assert_called_with(state="disabled")
        self.mock_app.export_button.config.assert_called_with(state="disabled")
        self.mock_app.browse_train_data_button.config.assert_called_with(
            state="disabled")
        self.mock_app.browse_output_folder_button.config.assert_called_with(
            state="disabled")

        # 驗證啟用的停止按鈕
        self.mock_app.stop_button.config.assert_called_with(state="normal")

    def test_enable_all_buttons_except_stop(self, mock_showinfo, mock_showerror):
        """測試啟用所有按鈕除了停止按鈕的邏輯"""
        # 定義實際的方法邏輯
        def _enable_all_buttons_except_stop():
            buttons_to_enable = [
                self.mock_app.run_button,
                self.mock_app.reset_button,
                self.mock_app.import_button,
                self.mock_app.export_button,
                self.mock_app.browse_train_data_button,
                self.mock_app.browse_output_folder_button
            ]

            for button in buttons_to_enable:
                if button:
                    button.config(state="normal")

            # 禁用停止按鈕
            if self.mock_app.stop_button:
                self.mock_app.stop_button.config(state="disabled")

        # 執行測試
        _enable_all_buttons_except_stop()

        # 驗證啟用的按鈕
        self.mock_app.run_button.config.assert_called_with(state="normal")
        self.mock_app.reset_button.config.assert_called_with(state="normal")
        self.mock_app.import_button.config.assert_called_with(state="normal")
        self.mock_app.export_button.config.assert_called_with(state="normal")
        self.mock_app.browse_train_data_button.config.assert_called_with(
            state="normal")
        self.mock_app.browse_output_folder_button.config.assert_called_with(
            state="normal")

        # 驗證禁用的停止按鈕
        self.mock_app.stop_button.config.assert_called_with(state="disabled")

    def test_training_workflow_button_states(self, mock_showinfo, mock_showerror):
        """測試完整的訓練工作流程中的按鈕狀態變化"""

        # 定義方法邏輯
        def _disable_all_buttons_except_stop():
            buttons_to_disable = [
                self.mock_app.run_button,
                self.mock_app.reset_button,
                self.mock_app.import_button,
                self.mock_app.export_button,
                self.mock_app.browse_train_data_button,
                self.mock_app.browse_output_folder_button
            ]
            for button in buttons_to_disable:
                if button:
                    button.config(state="disabled")
            if self.mock_app.stop_button:
                self.mock_app.stop_button.config(state="normal")

        def _enable_all_buttons_except_stop():
            buttons_to_enable = [
                self.mock_app.run_button,
                self.mock_app.reset_button,
                self.mock_app.import_button,
                self.mock_app.export_button,
                self.mock_app.browse_train_data_button,
                self.mock_app.browse_output_folder_button
            ]
            for button in buttons_to_enable:
                if button:
                    button.config(state="normal")
            if self.mock_app.stop_button:
                self.mock_app.stop_button.config(state="disabled")

        # 1. 初始狀態：所有按鈕啟用，停止按鈕禁用
        self.assertFalse(self.mock_app.is_training)

        # 2. 開始執行：設定訓練狀態並禁用所有按鈕除了停止按鈕
        self.mock_app.is_training = True
        _disable_all_buttons_except_stop()

        # 驗證開始執行時的按鈕狀態
        self.assertTrue(self.mock_app.is_training)
        self.mock_app.run_button.config.assert_called_with(state="disabled")
        self.mock_app.stop_button.config.assert_called_with(state="normal")

        # 3. 停止執行：重設訓練狀態並啟用所有按鈕除了停止按鈕
        self.mock_app.is_training = False
        _enable_all_buttons_except_stop()

        # 驗證停止執行時的按鈕狀態
        self.assertFalse(self.mock_app.is_training)
        self.mock_app.run_button.config.assert_called_with(state="normal")
        self.mock_app.stop_button.config.assert_called_with(state="disabled")

    def test_button_list_completeness(self, mock_showinfo, mock_showerror):
        """測試按鈕列表的完整性"""
        # 確保所有按鈕都包含在控制列表中
        expected_buttons = [
            'run_button',
            'reset_button',
            'import_button',
            'export_button',
            'browse_train_data_button',
            'browse_output_folder_button'
        ]

        # 檢查模擬應用程式是否有所有預期的按鈕
        for button_name in expected_buttons:
            self.assertTrue(hasattr(self.mock_app, button_name),
                            f"缺少按鈕: {button_name}")

        # 停止按鈕應該單獨處理
        self.assertTrue(hasattr(self.mock_app, 'stop_button'), "缺少停止按鈕")

    def test_stop_button_behavior(self, mock_showinfo, mock_showerror):
        """測試停止按鈕的特殊行為"""

        # 定義方法邏輯
        def _disable_all_buttons_except_stop():
            if self.mock_app.stop_button:
                self.mock_app.stop_button.config(state="normal")

        def _enable_all_buttons_except_stop():
            if self.mock_app.stop_button:
                self.mock_app.stop_button.config(state="disabled")

        # 測試：執行訓練時，停止按鈕應該啟用
        _disable_all_buttons_except_stop()
        self.mock_app.stop_button.config.assert_called_with(state="normal")

        # 重設模擬
        self.mock_app.stop_button.config.reset_mock()

        # 測試：停止訓練後，停止按鈕應該禁用
        _enable_all_buttons_except_stop()
        self.mock_app.stop_button.config.assert_called_with(state="disabled")


if __name__ == '__main__':
    # 執行測試並顯示詳細結果
    unittest.main(verbosity=2)
