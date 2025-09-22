#!/usr/bin/env python3
"""
測試超參數調優自動回填功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_parameter_auto_fill():
    """測試參數自動回填功能"""
    print("=== 測試超參數調優自動回填功能 ===")

    # 模擬最佳參數結果
    mock_best_params = {
        'model__n_estimators': 300,
        'model__learning_rate': 0.005,
        'model__num_leaves': 40,
        'model__scale_pos_weight': 0.56,
        'model__reg_alpha': 0.5
    }

    print("模擬的最佳參數:")
    for param, value in mock_best_params.items():
        clean_param = param.replace('model__', '')
        print(f"  {clean_param}: {value}")

    # 測試參數映射邏輯
    param_mapping = {
        'model__n_estimators': ('model_n_estimators', 'int'),
        'model__learning_rate': ('model_learning_rate', 'float'),
        'model__num_leaves': ('model_num_leaves', 'int'),
        'model__scale_pos_weight': ('model_scale_pos_weight', 'float'),
        'model__reg_alpha': ('model_reg_alpha', 'float')
    }

    print("\n參數映射測試:")
    for param_key, value in mock_best_params.items():
        if param_key in param_mapping:
            gui_attr, param_type = param_mapping[param_key]
            print(
                f"  {param_key} -> GUI屬性: {gui_attr}, 類型: {param_type}, 值: {value}")

            # 測試類型轉換
            try:
                if param_type == 'int':
                    converted_value = int(value)
                elif param_type == 'float':
                    converted_value = float(value)
                else:
                    converted_value = value
                print(
                    f"    轉換成功: {type(converted_value).__name__}({converted_value})")
            except Exception as e:
                print(f"    轉換失敗: {e}")

    print("\n✅ 參數自動回填功能測試完成")


if __name__ == "__main__":
    test_parameter_auto_fill()
