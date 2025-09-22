#!/usr/bin/env python3
"""
統一測試執行器 - 自動發現並執行所有單元測試
⚠️ 必須在專案根目錄執行
"""

import os
import sys
import subprocess
from pathlib import Path


def run_test_file(test_file_path):
    """執行單一測試檔案"""
    print(f"\n{'='*60}")
    print(f"🧪 執行測試: {test_file_path.name}")
    print(f"{'='*60}")

    try:
        # 獲取 Python 執行檔路徑
        python_exe = sys.executable

        # 執行測試檔案
        result = subprocess.run(
            [python_exe, str(test_file_path)],
            capture_output=True,
            text=True,
            cwd=str(test_file_path.parent.parent)  # 設定工作目錄為專案根目錄
        )

        # 輸出結果
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("錯誤輸出:")
            print(result.stderr)

        if result.returncode == 0:
            print(f"✅ 測試 {test_file_path.name} 執行成功")
        else:
            print(f"❌ 測試 {test_file_path.name} 執行失敗 (退出碼: {result.returncode})")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ 執行測試時發生錯誤: {e}")
        return False


def main():
    """主函式：自動發現並執行所有測試"""
    print("🚀 開始執行所有單元測試")

    # 獲取當前檔案所在目錄
    current_dir = Path(__file__).parent

    # 自動發現所有測試檔案
    test_files = sorted(list(current_dir.glob("test_*.py")))

    if not test_files:
        print("❌ 沒有找到任何測試檔案")
        return

    print(f"📁 找到 {len(test_files)} 個測試檔案:")
    for test_file in test_files:
        print(f"   - {test_file.name}")

    # 執行所有測試
    success_count = 0
    total_count = len(test_files)

    for test_file in test_files:
        if run_test_file(test_file):
            success_count += 1

    # 顯示總結
    print(f"\n{'='*60}")
    print(f"📊 測試執行總結")
    print(f"{'='*60}")
    print(f"總測試檔案數: {total_count}")
    print(f"成功執行: {success_count}")
    print(f"執行失敗: {total_count - success_count}")

    if success_count == total_count:
        print("🎉 所有測試都執行成功！")
    else:
        print(f"⚠️  有 {total_count - success_count} 個測試執行失敗")

    print(
        f"\n執行完成時間: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
