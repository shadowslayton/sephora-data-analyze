#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按鈕控制功能單元測試 - 簡化版本
專注測試按鈕控制邏輯而非 GUI 初始化
"""

import unittest
import sys
import os
from unittest.mock import patch

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockButton:
    """模擬按鈕類別"""

    def __init__(self, initial_state='normal'):
        self._state = initial_state

    def configure(self, state=None, **kwargs):
        if state is not None:
            self._state = state

    def config(self, state=None, **kwargs):
        self.configure(state=state, **kwargs)

    def __getitem__(self, key):
        if key == 'state':
            return self._state
        raise KeyError(f"Key '{key}' not found")


class MockApp:
    """模擬應用程式類別"""

    def __init__(self):
        # 建立模擬按鈕（使用 Any 型別以支援 None 賦值）
        self.run_button = MockButton('normal')
        self.stop_button = MockButton('disabled')
        self.reset_button = MockButton('normal')
        self.import_button = MockButton('normal')
        self.export_button = MockButton('normal')
        self.browse_train_data_button = MockButton('normal')
        self.browse_output_folder_button = MockButton('normal')

        # 訓練狀態
        self.is_training = False

    def _disable_all_buttons_except_stop(self):
        """禁用除了停止按鈕外的所有按鈕"""
        buttons_to_disable = [
            self.run_button,
            self.reset_button,
            self.import_button,
            self.export_button,
            self.browse_train_data_button,
            self.browse_output_folder_button
        ]

        for button in buttons_to_disable:
            if button is not None:
                button.configure(state="disabled")

        # 啟用停止按鈕
        if self.stop_button is not None:
            self.stop_button.configure(state="normal")

    def _enable_all_buttons_except_stop(self):
        """啟用除了停止按鈕外的所有按鈕"""
        buttons_to_enable = [
            self.run_button,
            self.reset_button,
            self.import_button,
            self.export_button,
            self.browse_train_data_button,
            self.browse_output_folder_button
        ]

        for button in buttons_to_enable:
            if button is not None:
                button.configure(state="normal")

        # 禁用停止按鈕
        if self.stop_button is not None:
            self.stop_button.configure(state="disabled")


class TestButtonControlLogic(unittest.TestCase):
    """測試按鈕控制邏輯"""

    def setUp(self):
        """設定測試環境"""
        # 全域禁用所有 messagebox 彈跳視窗
        self.patcher_showinfo = patch('tkinter.messagebox.showinfo')
        self.patcher_showerror = patch('tkinter.messagebox.showerror')
        self.patcher_showwarning = patch('tkinter.messagebox.showwarning')
        self.patcher_askyesno = patch(
            'tkinter.messagebox.askyesno', return_value=True)
        self.patcher_askokcancel = patch(
            'tkinter.messagebox.askokcancel', return_value=True)

        self.mock_showinfo = self.patcher_showinfo.start()
        self.mock_showerror = self.patcher_showerror.start()
        self.mock_showwarning = self.patcher_showwarning.start()
        self.mock_askyesno = self.patcher_askyesno.start()
        self.mock_askokcancel = self.patcher_askokcancel.start()

        self.app = MockApp()

    def test_initial_button_state(self):
        """測試初始按鈕狀態"""
        # 初始狀態下，所有按鈕應該啟用，除了停止按鈕
        self.assertEqual(
            self.app.run_button['state'], 'normal', "開始執行按鈕初始應該啟用")
        self.assertEqual(
            self.app.stop_button['state'], 'disabled', "停止執行按鈕初始應該禁用")
        self.assertEqual(
            self.app.reset_button['state'], 'normal', "重設參數按鈕初始應該啟用")
        self.assertEqual(
            self.app.import_button['state'], 'normal', "匯入設定按鈕初始應該啟用")
        self.assertEqual(
            self.app.export_button['state'], 'normal', "匯出設定按鈕初始應該啟用")
        self.assertEqual(
            self.app.browse_train_data_button['state'], 'normal', "瀏覽訓練資料按鈕初始應該啟用")
        self.assertEqual(
            self.app.browse_output_folder_button['state'], 'normal', "瀏覽輸出資料夾按鈕初始應該啟用")

    def test_disable_all_buttons_except_stop(self):
        """測試禁用除停止按鈕外的所有按鈕"""
        # 呼叫方法
        self.app._disable_all_buttons_except_stop()

        # 驗證狀態
        self.assertEqual(
            self.app.run_button['state'], 'disabled', "開始執行按鈕應該被禁用")
        self.assertEqual(self.app.stop_button['state'], 'normal', "停止執行按鈕應該啟用")
        self.assertEqual(
            self.app.reset_button['state'], 'disabled', "重設參數按鈕應該被禁用")
        self.assertEqual(
            self.app.import_button['state'], 'disabled', "匯入設定按鈕應該被禁用")
        self.assertEqual(
            self.app.export_button['state'], 'disabled', "匯出設定按鈕應該被禁用")
        self.assertEqual(
            self.app.browse_train_data_button['state'], 'disabled', "瀏覽訓練資料按鈕應該被禁用")
        self.assertEqual(
            self.app.browse_output_folder_button['state'], 'disabled', "瀏覽輸出資料夾按鈕應該被禁用")

    def test_enable_all_buttons_except_stop(self):
        """測試啟用除停止按鈕外的所有按鈕"""
        # 先禁用所有按鈕
        self.app._disable_all_buttons_except_stop()

        # 然後重新啟用
        self.app._enable_all_buttons_except_stop()

        # 驗證狀態
        self.assertEqual(self.app.run_button['state'], 'normal', "開始執行按鈕應該啟用")
        self.assertEqual(
            self.app.stop_button['state'], 'disabled', "停止執行按鈕應該被禁用")
        self.assertEqual(
            self.app.reset_button['state'], 'normal', "重設參數按鈕應該啟用")
        self.assertEqual(
            self.app.import_button['state'], 'normal', "匯入設定按鈕應該啟用")
        self.assertEqual(
            self.app.export_button['state'], 'normal', "匯出設定按鈕應該啟用")
        self.assertEqual(
            self.app.browse_train_data_button['state'], 'normal', "瀏覽訓練資料按鈕應該啟用")
        self.assertEqual(
            self.app.browse_output_folder_button['state'], 'normal', "瀏覽輸出資料夾按鈕應該啟用")

    def test_button_control_cycle(self):
        """測試完整的按鈕控制循環"""
        # 初始狀態
        self.assertEqual(
            self.app.stop_button['state'], 'disabled', "初始：停止按鈕應該禁用")
        self.assertEqual(self.app.run_button['state'], 'normal', "初始：開始按鈕應該啟用")

        # 模擬開始訓練
        self.app._disable_all_buttons_except_stop()
        self.app.is_training = True

        # 訓練中狀態
        self.assertEqual(
            self.app.stop_button['state'], 'normal', "訓練中：停止按鈕應該啟用")
        self.assertEqual(
            self.app.run_button['state'], 'disabled', "訓練中：開始按鈕應該禁用")

        # 模擬結束訓練
        self.app._enable_all_buttons_except_stop()
        self.app.is_training = False

        # 結束狀態
        self.assertEqual(
            self.app.stop_button['state'], 'disabled', "結束：停止按鈕應該禁用")
        self.assertEqual(self.app.run_button['state'], 'normal', "結束：開始按鈕應該啟用")

    def test_none_button_handling(self):
        """測試 None 按鈕的處理"""
        # 建立專門用於測試 None 處理的模擬應用程式
        class TestAppWithNoneButtons:
            def __init__(self):
                self.run_button = MockButton('normal')
                self.stop_button = MockButton('disabled')
                self.reset_button = MockButton('normal')
                self.import_button = None  # 這個設為 None
                self.export_button = None  # 這個設為 None
                self.browse_train_data_button = MockButton('normal')
                self.browse_output_folder_button = MockButton('normal')

            def _disable_all_buttons_except_stop(self):
                """禁用除了停止按鈕外的所有按鈕"""
                buttons_to_disable = [
                    self.run_button,
                    self.reset_button,
                    self.import_button,
                    self.export_button,
                    self.browse_train_data_button,
                    self.browse_output_folder_button
                ]

                for button in buttons_to_disable:
                    if button is not None:
                        button.configure(state="disabled")

                # 啟用停止按鈕
                if self.stop_button is not None:
                    self.stop_button.configure(state="normal")

            def _enable_all_buttons_except_stop(self):
                """啟用除了停止按鈕外的所有按鈕"""
                buttons_to_enable = [
                    self.run_button,
                    self.reset_button,
                    self.import_button,
                    self.export_button,
                    self.browse_train_data_button,
                    self.browse_output_folder_button
                ]

                for button in buttons_to_enable:
                    if button is not None:
                        button.configure(state="normal")

                # 禁用停止按鈕
                if self.stop_button is not None:
                    self.stop_button.configure(state="disabled")

        # 建立測試應用程式
        test_app = TestAppWithNoneButtons()

        # 這些操作應該不會引發錯誤
        test_app._disable_all_buttons_except_stop()
        test_app._enable_all_buttons_except_stop()

        # 其他按鈕仍應正常工作
        self.assertEqual(
            test_app.run_button['state'], 'normal', "非 None 按鈕應該正常工作")
        self.assertEqual(
            test_app.stop_button['state'], 'disabled', "停止按鈕應該正常工作")

    def test_multiple_disable_enable_calls(self):
        """測試多次呼叫禁用/啟用方法"""
        # 多次呼叫應該不會出問題
        self.app._disable_all_buttons_except_stop()
        self.app._disable_all_buttons_except_stop()
        self.assertEqual(
            self.app.run_button['state'], 'disabled', "多次禁用後按鈕狀態應該一致")

        self.app._enable_all_buttons_except_stop()
        self.app._enable_all_buttons_except_stop()
        self.assertEqual(
            self.app.run_button['state'], 'normal', "多次啟用後按鈕狀態應該一致")

    def tearDown(self):
        """清理測試環境"""
        # 停止所有 patcher
        self.patcher_showinfo.stop()
        self.patcher_showerror.stop()
        self.patcher_showwarning.stop()
        self.patcher_askyesno.stop()
        self.patcher_askokcancel.stop()


if __name__ == '__main__':
    unittest.main()
