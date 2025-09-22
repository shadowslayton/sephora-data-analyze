#!/usr/bin/env python3
"""
測試 exclude_columns 功能
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


def test_exclude_columns():
    """測試排除多個欄位的功能"""
    print("=== 測試排除欄位功能 ===")

    # 測試資料路徑
    data_path = "traning_data/train_data(top20).csv"

    # 首先載入資料查看有哪些欄位
    try:
        data = pd.read_csv(data_path)
        print(f"資料形狀: {data.shape}")
        print(f"所有欄位: {list(data.columns)}")
        print()

        # 檢查 rating 和 is_recommended 的相關性
        if 'rating' in data.columns and 'is_recommended' in data.columns:
            correlation = data['rating'].corr(data['is_recommended'])
            print(f"rating 和 is_recommended 的相關係數: {correlation:.3f}")
            print()

        # 測試不排除任何欄位的檢測結果
        print("--- 不排除任何欄位 ---")
        feature_cols, target_col, missing_cols = model_traning.detect_columns(
            data, None, None, "is_recommended", None)
        print(f"檢測到的特徵欄位數量: {len(feature_cols) if feature_cols else 0}")
        if feature_cols:
            print(f"前 10 個特徵欄位: {feature_cols[:10]}")
        print()

        # 測試排除 rating 欄位
        print("--- 排除 rating 欄位 ---")
        exclude_cols = ["rating"]
        feature_cols_excluded, target_col_excluded, missing_cols_excluded = model_traning.detect_columns(
            data, None, None, "is_recommended", exclude_cols)
        print(
            f"排除後的特徵欄位數量: {len(feature_cols_excluded) if feature_cols_excluded else 0}")
        if feature_cols_excluded:
            print(f"前 10 個特徵欄位: {feature_cols_excluded[:10]}")
            if 'rating' in feature_cols_excluded:
                print("❌ 錯誤: rating 欄位仍然存在！")
            else:
                print("✅ 成功: rating 欄位已被排除")
        print()

        # 測試排除多個欄位
        print("--- 排除多個欄位: rating, product_id ---")
        exclude_cols_multiple = ["rating", "product_id"]
        feature_cols_multi, target_col_multi, missing_cols_multi = model_traning.detect_columns(
            data, None, None, "is_recommended", exclude_cols_multiple)
        print(
            f"排除後的特徵欄位數量: {len(feature_cols_multi) if feature_cols_multi else 0}")
        if feature_cols_multi:
            print(f"前 10 個特徵欄位: {feature_cols_multi[:10]}")
            excluded_found = [
                col for col in exclude_cols_multiple if col in feature_cols_multi]
            if excluded_found:
                print(f"❌ 錯誤: 以下欄位仍然存在: {excluded_found}")
            else:
                print("✅ 成功: 所有指定的欄位都已被排除")
        print()

        print("=== 測試完成 ===")

    except FileNotFoundError:
        print(f"❌ 找不到資料檔案: {data_path}")
        print("請確保資料檔案存在於指定路徑")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")


if __name__ == "__main__":
    test_exclude_columns()
