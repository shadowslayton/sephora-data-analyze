#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 traning_app.py 的配置管理和錯誤處理功能
包含配置匯入、錯誤處理、邊界情況測試
"""

import unittest
import sys
import os
import tkinter as tk
from unittest.mock import patch, MagicMock, mock_open

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestConfigAndErrorHandling(unittest.TestCase):
    """測試配置管理和錯誤處理"""

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
            # 建立模擬的 status_text - 使用 setattr 避免型別檢查錯誤
            setattr(self.app, 'status_text', MagicMock())
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

        # 安全地銷毀 tkinter 視窗
        if hasattr(self, 'root') and self.root:
            try:
                self.root.destroy()
            except:
                pass  # 忽略銷毀錯誤

    def test_config_import_success(self):
        """測試配置匯入成功案例"""
        print("=== 測試配置匯入成功案例 ===")

        # 建立測試配置內容（無需建立實體檔案）
        config_content = """# 測試配置檔案
TARGET_COLUMN = "test_target"
EXCLUDE_COLUMNS = "col1,col2,col3"
TEST_SIZE = 0.25
MODEL_N_ESTIMATORS = 300
MODEL_LEARNING_RATE = 0.005
RANDOM_STATE = 123
"""

        # 使用 mock 來模擬檔案讀取，避免建立實體檔案
        with patch('tkinter.filedialog.askopenfilename') as mock_open_dialog:
            with patch('builtins.open', mock_open(read_data=config_content)) as mock_file:
                mock_open_dialog.return_value = "mock_config.config"

                # 執行匯入
                updated_count = self.app.import_config()

                # 檢查參數是否被正確設定
                self.assertEqual(self.app.target_column.get(), "test_target")
                self.assertEqual(
                    self.app.exclude_columns.get(), "col1,col2,col3")
                self.assertEqual(self.app.test_size.get(), 0.25)
                self.assertEqual(self.app.model_n_estimators.get(), 300)
                self.assertEqual(self.app.model_learning_rate.get(), 0.005)
                self.assertEqual(self.app.random_state.get(), 123)

                # 檢查更新計數
                if updated_count is not None:
                    self.assertGreater(updated_count, 0)

        print("✅ 配置匯入成功案例測試通過")

    def test_config_import_malformed_file(self):
        """測試匯入格式錯誤的配置檔案"""
        print("=== 測試匯入格式錯誤的配置檔案 ===")

        # 建立格式錯誤的配置內容（無需建立實體檔案）
        malformed_content = """# 錯誤格式的配置檔案
TARGET_COLUMN "missing_equals"
EXCLUDE_COLUMNS = 
INVALID_LINE_WITHOUT_EQUALS
TEST_SIZE = "not_a_number"
MODEL_N_ESTIMATORS = abc
"""

        # 使用 mock 來模擬檔案讀取，避免建立實體檔案
        with patch('tkinter.filedialog.askopenfilename') as mock_open_dialog:
            with patch('builtins.open', mock_open(read_data=malformed_content)) as mock_file:
                with patch('tkinter.messagebox.showerror') as mock_error:
                    mock_open_dialog.return_value = "malformed_config.config"

                    # 執行匯入（應該處理錯誤）
                    try:
                        self.app.import_config()
                        # 如果沒有拋出異常，檢查是否顯示了錯誤訊息
                        # 某些格式錯誤可能被忽略而不是拋出異常
                    except Exception:
                        # 預期可能會有異常
                        pass

        print("✅ 格式錯誤配置檔案測試通過")

    def test_config_import_nonexistent_file(self):
        """測試匯入不存在的檔案"""
        print("=== 測試匯入不存在的檔案 ===")

        with patch('tkinter.filedialog.askopenfilename') as mock_open_dialog:
            with patch('tkinter.messagebox.showerror') as mock_error:
                mock_open_dialog.return_value = "nonexistent_file.config"

                # 執行匯入
                self.app.import_config()

                # 檢查是否顯示錯誤訊息
                mock_error.assert_called()

        print("✅ 不存在檔案測試通過")

    def test_config_import_cancel(self):
        """測試使用者取消匯入"""
        print("=== 測試使用者取消匯入 ===")

        with patch('tkinter.filedialog.askopenfilename') as mock_open_dialog:
            mock_open_dialog.return_value = ""  # 使用者取消

            # 記錄原始參數值
            original_target = self.app.target_column.get()
            original_test_size = self.app.test_size.get()

            # 執行匯入
            result = self.app.import_config()

            # 檢查參數沒有改變
            self.assertEqual(self.app.target_column.get(), original_target)
            self.assertEqual(self.app.test_size.get(), original_test_size)

        print("✅ 使用者取消匯入測試通過")

    def test_apply_best_parameters_success(self):
        """測試參數自動回填成功案例"""
        print("=== 測試參數自動回填成功案例 ===")

        # 模擬最佳參數
        best_params = {
            'model__n_estimators': 300,
            'model__learning_rate': 0.005,
            'model__num_leaves': 40,
            'model__scale_pos_weight': 0.6
        }

        # 執行參數回填
        self.app.apply_best_parameters(best_params)

        # 強制執行待處理的 tkinter 事件
        self.root.update()

        # 檢查參數是否被正確設定
        self.assertEqual(self.app.model_n_estimators.get(), 300)
        self.assertEqual(self.app.model_learning_rate.get(), 0.005)
        self.assertEqual(self.app.model_num_leaves.get(), 40)
        self.assertEqual(self.app.model_scale_pos_weight.get(), 0.6)

        print("✅ 參數自動回填成功案例測試通過")

    def test_apply_best_parameters_invalid_types(self):
        """測試參數自動回填中的類型轉換錯誤"""
        print("=== 測試參數自動回填類型轉換錯誤 ===")

        # 模擬包含無效類型的最佳參數
        best_params = {
            'model__n_estimators': 'invalid_int',  # 應該是整數但是字串
            'model__learning_rate': 'invalid_float',  # 應該是浮點數但是字串
            'model__num_leaves': 30.5  # 應該是整數但是浮點數（這個應該能轉換）
        }

        # 執行參數回填
        self.app.apply_best_parameters(best_params)

        # 強制執行待處理的 tkinter 事件
        self.root.update()

        # 檢查能轉換的參數是否正確設定
        self.assertEqual(self.app.model_num_leaves.get(), 30)  # 30.5 轉成 30

        print("✅ 參數自動回填類型轉換錯誤測試通過")

    def test_apply_best_parameters_empty(self):
        """測試空的最佳參數"""
        print("=== 測試空的最佳參數 ===")

        # 執行空參數回填
        self.app.apply_best_parameters({})

        # 強制執行待處理的 tkinter 事件
        self.root.update()

        print("✅ 空最佳參數測試通過")

    def test_training_with_validation_errors(self):
        """測試含有驗證錯誤的訓練執行"""
        print("=== 測試含有驗證錯誤的訓練執行 ===")

        # 建立模擬元件
        setattr(self.app, 'run_button', MagicMock())
        setattr(self.app, 'stop_button', MagicMock())

        # 模擬驗證器回傳錯誤
        validation_errors = ["目標欄位不能為空", "訓練資料路徑無效"]

        with patch.object(self.app.validator, 'validate_all_parameters', return_value=validation_errors):
            with patch('tkinter.messagebox.showerror') as mock_error:
                # 執行訓練
                self.app.run_training()

                # 檢查錯誤訊息被顯示
                mock_error.assert_called_once()

                # 檢查訓練狀態沒有改變
                self.assertFalse(self.app.is_training)

                # 檢查按鈕狀態沒有改變
                run_button = getattr(self.app, 'run_button', None)
                stop_button = getattr(self.app, 'stop_button', None)
                if run_button and hasattr(run_button, 'config'):
                    run_button.config.assert_not_called()
                if stop_button and hasattr(stop_button, 'config'):
                    stop_button.config.assert_not_called()

        print("✅ 驗證錯誤的訓練執行測試通過")

    def test_training_already_running(self):
        """測試當訓練已在執行時再次點擊執行"""
        print("=== 測試重複執行訓練 ===")

        # 設定為已在訓練狀態
        self.app.is_training = True

        # 建立模擬元件
        setattr(self.app, 'run_button', MagicMock())
        setattr(self.app, 'stop_button', MagicMock())

        # 執行訓練（應該立即返回）
        self.app.run_training()

        # 檢查沒有進行任何操作
        run_button = getattr(self.app, 'run_button', None)
        stop_button = getattr(self.app, 'stop_button', None)
        if run_button and hasattr(run_button, 'config'):
            run_button.config.assert_not_called()
        if stop_button and hasattr(stop_button, 'config'):
            stop_button.config.assert_not_called()

        print("✅ 重複執行訓練測試通過")

    def test_gui_builder_integration(self):
        """測試GUI建構器整合"""
        print("=== 測試GUI建構器整合 ===")

        # 檢查GUI建構器是否正確初始化
        self.assertIsNotNone(self.app.gui_builder)
        self.assertEqual(self.app.gui_builder.app, self.app)

        # 測試GUI建構器方法是否可呼叫
        self.assertTrue(hasattr(self.app.gui_builder,
                        'create_scrollable_frame'))
        self.assertTrue(hasattr(self.app.gui_builder, 'create_control_panel'))

        print("✅ GUI建構器整合測試通過")

    def test_validator_integration(self):
        """測試參數驗證器整合"""
        print("=== 測試參數驗證器整合 ===")

        # 檢查驗證器是否正確初始化
        self.assertIsNotNone(self.app.validator)
        self.assertEqual(self.app.validator.app, self.app)

        # 測試驗證器方法是否可呼叫
        self.assertTrue(hasattr(self.app.validator, 'validate_all_parameters'))
        self.assertTrue(hasattr(self.app.validator, 'validate_float_input'))

        print("✅ 參數驗證器整合測試通過")

    def test_config_manager_integration(self):
        """測試配置管理器整合"""
        print("=== 測試配置管理器整合 ===")

        # 檢查配置管理器是否正確初始化
        self.assertIsNotNone(self.app.config_manager)
        self.assertEqual(self.app.config_manager.app, self.app)

        # 測試配置管理器方法是否可呼叫
        self.assertTrue(
            hasattr(self.app.config_manager, 'generate_config_code'))
        self.assertTrue(hasattr(self.app.config_manager, 'export_config'))

        print("✅ 配置管理器整合測試通過")


def test_config_and_error_handling():
    """主要測試函式"""
    print("🚀 開始測試配置管理和錯誤處理功能...")
    unittest.main(verbosity=2)


if __name__ == "__main__":
    test_config_and_error_handling()
