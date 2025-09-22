#!/usr/bin/env python3
"""
測試 GUI 應用程式中的防呆機制
"""

import sys
import os
# 新增父目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 模擬 GUI 驗證邏輯


class MockTrainingApp:
    """模擬 GUI 應用程式的驗證邏輯"""

    def __init__(self):
        self.target_column_value = ""
        self.exclude_columns_value = ""

    def set_target_column(self, value):
        self.target_column_value = value

    def set_exclude_columns(self, value):
        self.exclude_columns_value = value

    def get_target_column(self):
        return self.target_column_value.strip()

    def get_exclude_columns(self):
        return self.exclude_columns_value.strip()

    def validate_parameters(self):
        """模擬 GUI 中的參數驗證邏輯"""
        errors = []

        # TARGET_COLUMN 必填檢查
        if not self.get_target_column():
            errors.append("❌ 必填項目：請輸入目標欄位名稱")

        # 檢查目標欄位與排除欄位的衝突
        target_col = self.get_target_column()
        exclude_cols_str = self.get_exclude_columns()
        if target_col and exclude_cols_str:
            exclude_cols = [col.strip()
                            for col in exclude_cols_str.split(',') if col.strip()]
            if target_col in exclude_cols:
                errors.append(f"❌ 參數衝突：目標欄位 '{target_col}' 不能同時出現在排除欄位列表中")
                errors.append(f"   排除欄位: {exclude_cols}")
                errors.append(f"   請從排除欄位中移除目標欄位，或者更改目標欄位")

        return errors


def test_gui_validation():
    """測試 GUI 驗證邏輯"""
    print("=== 測試 GUI 防呆機制 ===")

    app = MockTrainingApp()

    # 測試 1: 正常情況
    print("\n=== 測試 1: 正常情況 ===")
    app.set_target_column("is_recommended")
    app.set_exclude_columns("rating, product_id")

    errors = app.validate_parameters()
    if not errors:
        print("✅ 正常情況驗證通過")
        print(f"   目標欄位: {app.get_target_column()}")
        print(f"   排除欄位: {app.get_exclude_columns()}")
    else:
        print("❌ 正常情況驗證失敗")
        for error in errors:
            print(f"   {error}")

    # 測試 2: 目標欄位在排除列表中
    print("\n=== 測試 2: 目標欄位在排除列表中 ===")
    app.set_target_column("is_recommended")
    app.set_exclude_columns("rating, is_recommended, product_id")

    errors = app.validate_parameters()
    if errors:
        print("✅ GUI 防呆機制正常工作：")
        for error in errors:
            print(f"   {error}")
    else:
        print("❌ GUI 防呆機制失效")

    # 測試 3: 只有目標欄位在排除列表中
    print("\n=== 測試 3: 只有目標欄位在排除列表中 ===")
    app.set_target_column("is_recommended")
    app.set_exclude_columns("is_recommended")

    errors = app.validate_parameters()
    if errors:
        print("✅ GUI 防呆機制正常工作：")
        for error in errors:
            print(f"   {error}")
    else:
        print("❌ GUI 防呆機制失效")

    # 測試 4: 空白輸入
    print("\n=== 測試 4: 空白輸入 ===")
    app.set_target_column("")
    app.set_exclude_columns("")

    errors = app.validate_parameters()
    if errors:
        print("✅ 空白輸入檢查正常：")
        for error in errors:
            print(f"   {error}")
    else:
        print("❌ 空白輸入檢查失效")

    # 測試 5: 空格處理
    print("\n=== 測試 5: 空格處理 ===")
    app.set_target_column("  is_recommended  ")
    app.set_exclude_columns("  rating,  is_recommended,  product_id  ")

    errors = app.validate_parameters()
    if errors:
        print("✅ 空格處理和防呆機制正常工作：")
        for error in errors:
            print(f"   {error}")
    else:
        print("❌ 空格處理或防呆機制失效")

    print("\n=== GUI 防呆機制測試完成 ===")


if __name__ == "__main__":
    test_gui_validation()
