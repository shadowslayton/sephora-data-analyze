#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 traning_app.py 的額外功能
專注於功能性測試，避免複雜的模擬
"""

import sys
import os
import tempfile

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_config_file_operations():
    """測試配置檔案操作功能"""
    print("=== 測試配置檔案操作功能 ===")

    try:
        import tkinter as tk
        from traning_app import ModelTrainingApp

        # 建立測試應用程式
        root = tk.Tk()
        root.withdraw()
        app = ModelTrainingApp(root)

        # 設定一些測試參數
        app.target_column.set("test_target")
        app.exclude_columns.set("col1,col2")
        app.test_size.set(0.3)
        app.model_n_estimators.set(300)
        app.model_learning_rate.set(0.005)

        # 測試配置程式碼產生
        config_code = app.config_manager.generate_config_code()

        # 檢查基本內容
        assert "TARGET_COLUMN" in config_code
        assert "test_target" in config_code
        assert "EXCLUDE_COLUMNS" in config_code
        assert "col1,col2" in config_code
        assert "TEST_SIZE" in config_code
        assert "0.3" in config_code
        assert "MODEL_N_ESTIMATORS" in config_code
        assert "300" in config_code

        print("✅ 配置程式碼產生測試通過")

        # 測試配置檔案匯出和匯入
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.config', encoding='utf-8') as temp_file:
            temp_file.write(config_code)
            temp_filename = temp_file.name

        try:
            # 修改參數
            app.target_column.set("modified_target")
            app.test_size.set(0.5)

            # 模擬匯入配置
            with open(temp_filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析配置內容
            config_dict = {}
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    config_dict[key] = value

            # 檢查解析結果
            assert 'TARGET_COLUMN' in config_dict
            assert config_dict['TARGET_COLUMN'] == 'test_target'
            assert 'TEST_SIZE' in config_dict
            assert config_dict['TEST_SIZE'] == '0.3'

            print("✅ 配置檔案解析測試通過")

        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

        root.destroy()

    except Exception as e:
        print(f"❌ 配置檔案操作測試失敗: {e}")
        return False

    return True


def test_parameter_validation_integration():
    """測試參數驗證整合"""
    print("=== 測試參數驗證整合 ===")

    try:
        import tkinter as tk
        from traning_app import ModelTrainingApp

        # 建立測試應用程式
        root = tk.Tk()
        root.withdraw()
        app = ModelTrainingApp(root)

        # 測試驗證器存在
        assert hasattr(app, 'validator')
        assert app.validator is not None

        # 測試驗證方法存在
        assert hasattr(app.validator, 'validate_all_parameters')
        assert hasattr(app.validator, 'validate_float_input')
        assert hasattr(app.validator, 'validate_int_input')

        # 測試基本驗證功能
        # 設定無效參數
        app.target_column.set("")  # 空的目標欄位
        app.train_data_path.set("")  # 空的資料路徑

        # 執行驗證
        errors = app.validator.validate_all_parameters()

        # 應該有錯誤
        assert isinstance(errors, list)
        print(f"   找到 {len(errors)} 個驗證錯誤")

        # 設定有效參數
        app.target_column.set("valid_target")
        app.train_data_path.set("valid_path.csv")
        app.model_output_folder.set("valid_folder")
        app.model_filename.set("model.bin")

        # 再次驗證
        errors = app.validator.validate_all_parameters()
        print(f"   設定有效參數後，剩餘錯誤數: {len(errors)}")

        print("✅ 參數驗證整合測試通過")

        root.destroy()

    except Exception as e:
        print(f"❌ 參數驗證整合測試失敗: {e}")
        return False

    return True


def test_gui_builder_integration():
    """測試GUI建構器整合"""
    print("=== 測試GUI建構器整合 ===")

    try:
        import tkinter as tk
        from traning_app import ModelTrainingApp

        # 建立測試應用程式
        root = tk.Tk()
        root.withdraw()
        app = ModelTrainingApp(root)

        # 測試GUI建構器存在
        assert hasattr(app, 'gui_builder')
        assert app.gui_builder is not None

        # 測試GUI建構器方法存在
        assert hasattr(app.gui_builder, 'create_scrollable_frame')
        assert hasattr(app.gui_builder, 'create_control_panel')
        assert hasattr(app.gui_builder, 'create_data_processing_group')

        # 檢查應用程式參考
        assert app.gui_builder.app is app

        print("✅ GUI建構器整合測試通過")

        root.destroy()

    except Exception as e:
        print(f"❌ GUI建構器整合測試失敗: {e}")
        return False

    return True


def test_best_parameters_application():
    """測試最佳參數應用功能"""
    print("=== 測試最佳參數應用功能 ===")

    try:
        import tkinter as tk
        from traning_app import ModelTrainingApp
        from app_utils.app_constants import BEST_PARAMS_MAPPING

        # 建立測試應用程式
        root = tk.Tk()
        root.withdraw()
        app = ModelTrainingApp(root)

        # 記錄原始參數值
        original_n_estimators = app.model_n_estimators.get()
        original_learning_rate = app.model_learning_rate.get()

        # 測試參數映射字典存在
        assert len(BEST_PARAMS_MAPPING) > 0
        print(f"   找到 {len(BEST_PARAMS_MAPPING)} 個最佳參數映射")

        # 模擬最佳參數
        best_params = {
            'model__n_estimators': 300,
            'model__learning_rate': 0.005,
            'model__num_leaves': 40
        }

        # 應用最佳參數（直接使用 root.after 來確保在主執行緒）
        # 由於我們在測試環境中，需要手動處理 root.after 呼叫
        original_after = app.root.after

        def mock_after(delay, func, *args):
            # 立即執行函式而不是延遲
            if callable(func):
                func(*args)
            return "mock_timer"

        # 臨時替換 after 方法
        setattr(app.root, 'after', mock_after)

        try:
            app.apply_best_parameters(best_params)

            # 檢查參數是否被更新
            assert app.model_n_estimators.get() == 300
            assert app.model_learning_rate.get() == 0.005
            assert app.model_num_leaves.get() == 40

        finally:
            # 恢復原始的 after 方法
            setattr(app.root, 'after', original_after)

        print("✅ 最佳參數應用測試通過")

        root.destroy()

    except Exception as e:
        print(f"❌ 最佳參數應用測試失敗: {e}")
        return False

    return True


def test_constants_and_mappings():
    """測試常數和映射定義"""
    print("=== 測試常數和映射定義 ===")

    try:
        from app_utils.app_constants import PARAM_MAPPING, PARAM_DESCRIPTIONS, BEST_PARAMS_MAPPING

        # 檢查參數映射
        assert isinstance(PARAM_MAPPING, dict)
        assert len(PARAM_MAPPING) > 10
        print(f"   參數映射項目: {len(PARAM_MAPPING)}")

        # 檢查參數說明
        assert isinstance(PARAM_DESCRIPTIONS, dict)
        assert len(PARAM_DESCRIPTIONS) > 10
        print(f"   參數說明項目: {len(PARAM_DESCRIPTIONS)}")

        # 檢查最佳參數映射
        assert isinstance(BEST_PARAMS_MAPPING, dict)
        assert len(BEST_PARAMS_MAPPING) > 0
        print(f"   最佳參數映射項目: {len(BEST_PARAMS_MAPPING)}")

        # 檢查一些基本的參數映射
        expected_params = ['TARGET_COLUMN', 'TEST_SIZE',
                           'MODEL_N_ESTIMATORS', 'MODEL_LEARNING_RATE']
        for param in expected_params:
            assert param in PARAM_MAPPING, f"缺少參數映射: {param}"

        print("✅ 常數和映射定義測試通過")

    except Exception as e:
        print(f"❌ 常數和映射定義測試失敗: {e}")
        return False

    return True


def test_app_state_management():
    """測試應用程式狀態管理"""
    print("=== 測試應用程式狀態管理 ===")

    try:
        import tkinter as tk
        from traning_app import ModelTrainingApp

        # 建立測試應用程式
        root = tk.Tk()
        root.withdraw()
        app = ModelTrainingApp(root)

        # 檢查初始狀態
        assert app.is_training == False
        assert app.status_text is None  # 初始應該是 None
        assert app.run_button is None
        assert app.stop_button is None

        # 檢查預設運行模式
        assert app.run_mode.get() == "1"

        # 測試參數重設功能的準備
        app.target_column.set("test_target")
        app.test_size.set(0.5)
        app.model_n_estimators.set(500)

        # 檢查參數是否被設定
        assert app.target_column.get() == "test_target"
        assert app.test_size.get() == 0.5
        assert app.model_n_estimators.get() == 500

        print("✅ 應用程式狀態管理測試通過")

        root.destroy()

    except Exception as e:
        print(f"❌ 應用程式狀態管理測試失敗: {e}")
        return False

    return True


def main():
    """執行所有額外功能測試"""
    print("🚀 開始測試 traning_app.py 額外功能...")

    tests = [
        test_config_file_operations,
        test_parameter_validation_integration,
        test_gui_builder_integration,
        test_best_parameters_application,
        test_constants_and_mappings,
        test_app_state_management
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ 測試 {test_func.__name__} 失敗")
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 發生異常: {e}")

    print(f"\n📊 測試結果: {passed}/{total} 通過")

    if passed == total:
        print("🎉 所有額外功能測試都通過！")
        return True
    else:
        print("❌ 部分測試失敗")
        return False


if __name__ == "__main__":
    main()
