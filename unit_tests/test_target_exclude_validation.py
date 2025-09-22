#!/usr/bin/env python3
"""
測試目標欄位和排除欄位的防呆機制
"""

import pandas as pd
import sys
import os
import importlib.util
# 新增父目錄到 Python 路徑，讓我們可以匯入 model_traning
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 動態匯入 model_traning 模組，避免自動排版工具干擾
spec = importlib.util.spec_from_file_location(
    "model_traning", os.path.join(parent_dir, "ai_utils", "model_traning.py"))
if spec is not None and spec.loader is not None:
    model_traning = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_traning)
else:
    raise ImportError("無法載入 model_traning 模組")


def test_target_exclude_validation():
    """測試目標欄位不能出現在排除欄位中的防呆機制"""
    print("=== 測試目標欄位與排除欄位的防呆機制 ===")

    # 測試資料路徑
    data_path = "traning_data/train_data(top20).csv"

    try:
        data = pd.read_csv(data_path)
        print(f"資料載入成功，形狀: {data.shape}")
        print(f"目標欄位: is_recommended")
        print()

        # 測試 1: 正常情況 - 目標欄位不在排除列表中
        print("=== 測試 1: 正常情況 ===")
        print("目標欄位: is_recommended")
        print("排除欄位: ['rating', 'product_id']")

        result1 = model_traning.detect_columns(
            data, None, "is_recommended", "is_recommended", ["rating", "product_id"])

        if result1[0] is not None:
            print("✅ 正常情況測試通過")
            print(f"   特徵欄位數量: {len(result1[0])}")
        else:
            print("❌ 正常情況測試失敗")
        print()

        # 測試 2: 錯誤情況 - 目標欄位在排除列表中
        print("=== 測試 2: 錯誤情況 - 目標欄位在排除列表中 ===")
        print("目標欄位: is_recommended")
        print("排除欄位: ['rating', 'is_recommended']")

        result2 = model_traning.detect_columns(
            data, None, "is_recommended", "is_recommended", ["rating", "is_recommended"])

        if result2[0] is None:
            print("✅ 防呆機制正常工作：成功檢測到錯誤並阻止執行")
        else:
            print("❌ 防呆機制失效：應該檢測到錯誤但沒有")
        print()

        # 測試 3: 錯誤情況 - 只有目標欄位在排除列表中
        print("=== 測試 3: 錯誤情況 - 只有目標欄位在排除列表中 ===")
        print("目標欄位: is_recommended")
        print("排除欄位: ['is_recommended']")

        result3 = model_traning.detect_columns(
            data, None, "is_recommended", "is_recommended", ["is_recommended"])

        if result3[0] is None:
            print("✅ 防呆機制正常工作：成功檢測到錯誤並阻止執行")
        else:
            print("❌ 防呆機制失效：應該檢測到錯誤但沒有")
        print()

        # 測試 4: 測試 load_and_validate_data 函式的防呆機制
        print("=== 測試 4: load_and_validate_data 函式防呆機制 ===")
        print("目標欄位: is_recommended")
        print("排除欄位: ['is_recommended', 'rating']")

        result4 = model_traning.load_and_validate_data(
            data_path, None, "is_recommended", "is_recommended", ["is_recommended", "rating"])

        if result4[0] is None:
            print("✅ load_and_validate_data 防呆機制正常工作")
        else:
            print("❌ load_and_validate_data 防呆機制失效")
        print()

        # 測試 5: 邊界情況 - 空的排除列表
        print("=== 測試 5: 邊界情況 - 空的排除列表 ===")
        print("目標欄位: is_recommended")
        print("排除欄位: []")

        result5 = model_traning.detect_columns(
            data, None, "is_recommended", "is_recommended", [])

        if result5[0] is not None:
            print("✅ 空排除列表測試通過")
            print(f"   特徵欄位數量: {len(result5[0])}")
        else:
            print("❌ 空排除列表測試失敗")
        print()

        # 測試 6: 邊界情況 - None 排除列表
        print("=== 測試 6: 邊界情況 - None 排除列表 ===")
        print("目標欄位: is_recommended")
        print("排除欄位: None")

        result6 = model_traning.detect_columns(
            data, None, "is_recommended", "is_recommended", None)

        if result6[0] is not None:
            print("✅ None 排除列表測試通過")
            print(f"   特徵欄位數量: {len(result6[0])}")
        else:
            print("❌ None 排除列表測試失敗")
        print()

        print("=== 防呆機制測試完成 ===")
        print("建議：在使用 GUI 或直接呼叫函式時，")
        print("請確保目標欄位不要出現在排除欄位列表中。")

    except FileNotFoundError:
        print(f"❌ 找不到資料檔案: {data_path}")
        print("請確保資料檔案存在於指定路徑")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_target_exclude_validation()
