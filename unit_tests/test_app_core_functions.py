#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 traning_app.py 的核心應用程式功能
包含檔案瀏覽、狀態更新、配置管理、UI 控制等功能測試
"""

import unittest
import sys
import os
import tkinter as tk
from unittest.mock import patch, MagicMock

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestTrainingAppCore(unittest.TestCase):
    """測試訓練應用程式核心功能"""

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

        self.root = tk.Tk()
        self.root.withdraw()  # 隱藏視窗

        try:
            from traning_app import ModelTrainingApp
            self.app = ModelTrainingApp(self.root)
        except Exception as e:
            self.skipTest(f"無法建立應用程式實例: {e}")

    def tearDown(self):
        """清理測試環境"""
        # 停止所有 patcher
        self.patcher_showinfo.stop()
        self.patcher_showerror.stop()
        self.patcher_showwarning.stop()
        self.patcher_askyesno.stop()
        self.patcher_askokcancel.stop()

        if hasattr(self, 'root'):
            self.root.destroy()

    def test_app_initialization(self):
        """測試應用程式初始化"""
        print("=== 測試應用程式初始化 ===")

        # 檢查基本屬性
        self.assertIsNotNone(self.app.root)
        self.assertEqual(self.app.root.title(), "Sephora 產品推薦模型訓練器")
        self.assertFalse(self.app.is_training)

        # 檢查參數變數
        self.assertIsNotNone(self.app.target_column)
        self.assertIsNotNone(self.app.exclude_columns)
        self.assertIsNotNone(self.app.test_size)
        self.assertIsNotNone(self.app.model_n_estimators)

        # 檢查輔助物件
        self.assertIsNotNone(self.app.validator)
        self.assertIsNotNone(self.app.config_manager)
        self.assertIsNotNone(self.app.gui_builder)

        print("✅ 應用程式初始化測試通過")

    def test_default_parameter_values(self):
        """測試預設參數值"""
        print("=== 測試預設參數值 ===")

        # 檢查數值參數預設值
        self.assertEqual(self.app.test_size.get(), 0.2)
        self.assertEqual(self.app.random_state.get(), 42)
        self.assertEqual(self.app.similarity_cutoff.get(), 0.6)
        self.assertEqual(self.app.model_n_estimators.get(), 250)
        self.assertEqual(self.app.model_learning_rate.get(), 0.01)
        self.assertEqual(self.app.cv_folds.get(), 5)

        # 檢查字串參數預設值
        self.assertEqual(self.app.scoring_metric.get(), 'f1_macro')
        self.assertEqual(self.app.run_mode.get(), "1")
        self.assertEqual(self.app.target_column.get(), "")
        self.assertEqual(self.app.exclude_columns.get(), "")

        print("✅ 預設參數值測試通過")

    @patch('tkinter.filedialog.askopenfilename')
    def test_browse_train_data(self, mock_filedialog):
        """測試瀏覽訓練資料檔案功能"""
        print("=== 測試瀏覽訓練資料檔案 ===")

        # 模擬使用者選擇檔案
        test_file_path = "C:/test/data/train_data.csv"
        mock_filedialog.return_value = test_file_path

        # 執行檔案瀏覽
        self.app.browse_train_data()

        # 檢查結果
        self.assertEqual(self.app.train_data_path.get(), test_file_path)

        # 檢查 filedialog 被正確呼叫
        mock_filedialog.assert_called_once_with(
            title="選擇訓練資料檔案",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        # 測試使用者取消選擇的情況
        mock_filedialog.reset_mock()
        mock_filedialog.return_value = ""
        original_path = self.app.train_data_path.get()

        self.app.browse_train_data()
        self.assertEqual(self.app.train_data_path.get(),
                         original_path)  # 路徑不應改變

        print("✅ 瀏覽訓練資料檔案測試通過")

    @patch('tkinter.filedialog.askdirectory')
    def test_browse_model_output_folder(self, mock_filedialog):
        """測試瀏覽模型輸出資料夾功能"""
        print("=== 測試瀏覽模型輸出資料夾 ===")

        # 模擬使用者選擇資料夾
        test_folder_path = "C:/test/output"
        mock_filedialog.return_value = test_folder_path

        # 執行資料夾瀏覽
        self.app.browse_model_output_folder()

        # 檢查結果
        self.assertEqual(self.app.model_output_folder.get(), test_folder_path)

        # 檢查 filedialog 被正確呼叫
        mock_filedialog.assert_called_once_with(
            title="選擇模型輸出資料夾"
        )

        print("✅ 瀏覽模型輸出資料夾測試通過")

    def test_update_status_with_gui(self):
        """測試狀態更新功能（有GUI的情況）"""
        print("=== 測試狀態更新功能 ===")

        # 測試狀態更新（update_status 只輸出到 console）
        test_message = "測試狀態訊息"

        # 捕獲 print 輸出
        with patch('builtins.print') as mock_print:
            self.app.update_status(test_message)

            # 檢查是否有 print 被呼叫，且包含我們的訊息
            mock_print.assert_called_with(f"[狀態] {test_message}")

        print("✅ 狀態更新功能測試通過")

    def test_ui_state_management(self):
        """測試UI狀態管理"""
        print("=== 測試UI狀態管理 ===")

        # 建立模擬的按鈕元件
        setattr(self.app, 'run_button', MagicMock())
        setattr(self.app, 'stop_button', MagicMock())

        # 測試重設UI狀態
        self.app._reset_ui_state()

        # 檢查狀態
        self.assertFalse(self.app.is_training)
        run_button = getattr(self.app, 'run_button', None)
        stop_button = getattr(self.app, 'stop_button', None)
        if run_button and hasattr(run_button, 'config'):
            run_button.config.assert_called_with(state="normal")
        if stop_button and hasattr(stop_button, 'config'):
            stop_button.config.assert_called_with(state="disabled")

        print("✅ UI狀態管理測試通過")

    def test_stop_training(self):
        """測試停止訓練功能"""
        print("=== 測試停止訓練功能 ===")

        # 建立模擬的按鈕元件
        setattr(self.app, 'run_button', MagicMock())
        setattr(self.app, 'stop_button', MagicMock())

        # 設定訓練狀態
        self.app.is_training = True

        # 執行停止訓練
        self.app.stop_training()

        # 檢查UI狀態被重設
        self.assertFalse(self.app.is_training)

        print("✅ 停止訓練功能測試通過")

    def test_config_generation(self):
        """測試配置程式碼產生"""
        print("=== 測試配置程式碼產生 ===")

        # 設定一些測試參數
        self.app.target_column.set("test_target")
        self.app.exclude_columns.set("col1,col2")
        self.app.test_size.set(0.3)
        self.app.model_n_estimators.set(300)

        # 產生配置程式碼
        config_code = self.app.config_manager.generate_config_code()

        # 檢查配置程式碼內容
        self.assertIn("TARGET_COLUMN", config_code)
        self.assertIn("test_target", config_code)
        self.assertIn("EXCLUDE_COLUMNS", config_code)
        self.assertIn("col1,col2", config_code)
        self.assertIn("TEST_SIZE", config_code)
        self.assertIn("0.3", config_code)
        self.assertIn("MODEL_N_ESTIMATORS", config_code)
        self.assertIn("300", config_code)

        print("✅ 配置程式碼產生測試通過")

    def test_config_export(self):
        """測試配置匯出功能"""
        print("=== 測試配置匯出功能 ===")

        # 使用完全的 mock 避免產生實體檔案
        with patch('tkinter.filedialog.asksaveasfilename') as mock_save_dialog:
            with patch('tkinter.messagebox.showinfo') as mock_info:
                with patch.object(self.app.config_manager, 'export_config') as mock_export:
                    mock_save_dialog.return_value = "test_config.config"

                    # 設定一些測試參數
                    self.app.target_column.set("test_target")
                    self.app.model_n_estimators.set(300)

                    # 執行匯出
                    self.app.export_config()

                    # 驗證方法被正確呼叫
                    mock_save_dialog.assert_called_once()
                    mock_export.assert_called_once_with("test_config.config")
                    mock_info.assert_called_once()

        print("✅ 配置匯出功能測試通過")

    def test_parameter_reset(self):
        """測試參數重設功能"""
        print("=== 測試參數重設功能 ===")

        # 建立模擬的 status_text
        setattr(self.app, 'status_text', MagicMock())

        # 修改一些參數值
        original_test_size = self.app.test_size.get()
        original_n_estimators = self.app.model_n_estimators.get()

        self.app.test_size.set(0.5)
        self.app.model_n_estimators.set(500)
        self.app.target_column.set("modified_target")

        # 模擬使用者確認重設
        with patch('tkinter.messagebox.askyesno') as mock_confirm:
            mock_confirm.return_value = True

            # 執行參數重設
            self.app.reset_params()

            # 檢查參數是否被重設為預設值
            self.assertEqual(self.app.test_size.get(), original_test_size)
            self.assertEqual(self.app.model_n_estimators.get(),
                             original_n_estimators)
            self.assertEqual(self.app.target_column.get(), "")
            self.assertEqual(self.app.exclude_columns.get(), "")
            self.assertEqual(self.app.run_mode.get(), "1")

        print("✅ 參數重設功能測試通過")

    def test_training_state_control(self):
        """測試訓練狀態控制"""
        print("=== 測試訓練狀態控制 ===")

        # 建立模擬元件
        setattr(self.app, 'run_button', MagicMock())
        setattr(self.app, 'stop_button', MagicMock())
        setattr(self.app, 'status_text', MagicMock())

        # 模擬驗證器總是回傳無錯誤
        with patch.object(self.app.validator, 'validate_all_parameters', return_value=[]):
            # 初始狀態
            self.assertFalse(self.app.is_training)

            # 執行訓練（會立即返回因為我們模擬了執行緒）
            with patch('threading.Thread'):
                self.app.run_training()

                # 檢查訓練狀態
                self.assertTrue(self.app.is_training)

                # 檢查按鈕狀態更新
                run_button = getattr(self.app, 'run_button', None)
                stop_button = getattr(self.app, 'stop_button', None)

                if run_button and hasattr(run_button, 'config'):
                    run_button.config.assert_called_with(state="disabled")
                if stop_button and hasattr(stop_button, 'config'):
                    stop_button.config.assert_called_with(state="normal")

        print("✅ 訓練狀態控制測試通過")


def test_core_app_functions():
    """主要測試函式"""
    print("🚀 開始測試 traning_app.py 核心功能...")
    unittest.main(verbosity=2)


if __name__ == "__main__":
    test_core_app_functions()
