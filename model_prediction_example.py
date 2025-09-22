#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sephora 產品推薦模型預測範例
展示如何載入和使用訓練好的模型進行預測
"""

import pickle
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# 添加專案路徑到 Python 路徑中，以便載入模型時找到相關模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 導入訓練模組以確保 pickle 可以正確反序列化模型
try:
    import ai_utils.model_traning
    # 建立模組別名以解決 pickle 載入問題
    import sys
    sys.modules['model_traning'] = ai_utils.model_traning
except ImportError:
    print("⚠️  無法匯入 ai_utils.model_traning 模組，模型載入可能會失敗")


def load_model(model_path):
    """
    載入訓練好的模型

    參數:
        model_path (str): 模型檔案路徑

    回傳:
        dict: 包含模型和欄位資訊的字典
    """
    try:
        with open(model_path, "rb") as f:
            model_info = pickle.load(f)

        # 檢查是否為新版本模型（包含完整資訊）
        if hasattr(model_info, 'predict'):  # 舊版本只有 pipeline
            print("⚠️  載入的是舊版本模型，缺少欄位資訊")
            return {
                'pipeline': model_info,
                'feature_columns': None,
                'target_column': None
            }
        else:  # 新版本包含完整資訊
            print("✅ 載入新版本模型，包含完整欄位資訊")
            return model_info

    except FileNotFoundError:
        print(f"❌ 找不到模型檔案: {model_path}")
        return None
    except Exception as e:
        print(f"❌ 載入模型時發生錯誤: {e}")
        return None


def predict_single_product(model_info, product_data):
    """
    對單一產品進行推薦預測

    參數:
        model_info (dict): 模型資訊字典
        product_data (dict): 產品資料字典

    回傳:
        dict: 預測結果
    """
    if model_info is None:
        return {"error": "模型載入失敗"}

    pipeline = model_info['pipeline']

    # 將產品資料轉換為 DataFrame
    df = pd.DataFrame([product_data])

    try:
        # 進行預測
        prediction = pipeline.predict(df)[0]
        probability = pipeline.predict_proba(df)[0]

        return {
            "prediction": int(prediction),
            "probability_not_recommended": float(probability[0]),
            "probability_recommended": float(probability[1]),
            "recommendation": "推薦" if prediction == 1 else "不推薦"
        }

    except Exception as e:
        return {"error": f"預測時發生錯誤: {e}"}


def predict_batch_products(model_info, csv_path, output_path=None):
    """
    對批量產品進行推薦預測

    參數:
        model_info (dict): 模型資訊字典
        csv_path (str): 輸入 CSV 檔案路徑
        output_path (str): 輸出 CSV 檔案路徑（可選）

    回傳:
        pandas.DataFrame: 包含預測結果的資料框
    """
    if model_info is None:
        print("❌ 模型載入失敗")
        return None

    try:
        # 讀取資料
        df = pd.read_csv(csv_path)
        print(f"✅ 載入 {len(df)} 筆產品資料")

        pipeline = model_info['pipeline']

        # 進行預測
        predictions = pipeline.predict(df)
        probabilities = pipeline.predict_proba(df)

        # 將結果加入資料框
        df['prediction'] = predictions
        df['probability_not_recommended'] = probabilities[:, 0]
        df['probability_recommended'] = probabilities[:, 1]
        df['recommendation'] = df['prediction'].map({0: '不推薦', 1: '推薦'})

        print(f"✅ 預測完成!")
        print(f"推薦產品數量: {sum(predictions == 1)}")
        print(f"不推薦產品數量: {sum(predictions == 0)}")

        # 儲存結果
        if output_path:
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✅ 結果已儲存至: {output_path}")

        return df

    except Exception as e:
        print(f"❌ 批量預測時發生錯誤: {e}")
        return None


def show_model_info(model_info):
    """
    顯示模型資訊

    參數:
        model_info (dict): 模型資訊字典
    """
    if model_info is None:
        print("❌ 無法顯示模型資訊")
        return

    print("\n=== 模型資訊 ===")

    if 'feature_columns' in model_info and model_info['feature_columns']:
        print(f"特徵欄位數量: {len(model_info['feature_columns'])}")
        print("特徵欄位:")
        for i, col in enumerate(model_info['feature_columns'], 1):
            print(f"  {i:2d}. {col}")
    else:
        print("⚠️  特徵欄位資訊不可用（舊版本模型）")

    if 'target_column' in model_info and model_info['target_column']:
        print(f"\n目標欄位: {model_info['target_column']}")

    print(f"\n模型類型: {type(model_info['pipeline']).__name__}")


# 使用範例
if __name__ == "__main__":
    print("=== Sephora 產品推薦模型預測範例 ===\n")

    # 設定模型路徑
    model_path = "output_models/model_final.bin"

    # 載入模型
    print("📥 載入模型...")
    model_info = load_model(model_path)

    if model_info:
        # 顯示模型資訊
        show_model_info(model_info)

        # 範例 1: 單一產品預測
        print("\n" + "="*50)
        print("範例 1: 單一產品預測")
        print("="*50)

        sample_product = {
            # 根據實際訓練資料的欄位設定
            "rating": 4.2,
            "skin_tone": "fair",
            "eye_color": "blue",
            "skin_type": "combination",
            "hair_color": "brown",
            "brand_name": "Sephora Collection",
            "price_usd": 25.99,
            "child_count": 0,
            "limited_edition": 0,
            "new": 0,
            "online_only": 0,
            "out_of_stock": 0,
            "secondary_category": "Foundation",
            "sephora_exclusive": 0,
            "skin_tone_group": "Light"
        }

        print("預測產品資料:")
        for key, value in sample_product.items():
            print(f"  {key}: {value}")

        result = predict_single_product(model_info, sample_product)
        print(f"\n預測結果:")
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"  預測: {result['recommendation']}")
            print(f"  推薦機率: {result['probability_recommended']:.2%}")
            print(f"  不推薦機率: {result['probability_not_recommended']:.2%}")

        # 範例 2: 批量預測（如果有測試資料）
        print("\n" + "="*50)
        print("範例 2: 批量預測")
        print("="*50)

        test_data_path = "traning_data/train_data(top20).csv"
        if Path(test_data_path).exists():
            print(f"使用測試資料: {test_data_path}")
            results_df = predict_batch_products(
                model_info,
                test_data_path,
                output_path="output_models/predictions.csv"
            )

            if results_df is not None:
                print(f"\n前 5 筆預測結果:")
                display_cols = ['recommendation', 'probability_recommended']
                available_cols = [
                    col for col in display_cols if col in results_df.columns]
                print(results_df[available_cols].head())
        else:
            print(f"⚠️  測試資料檔案不存在: {test_data_path}")
            print("請提供包含產品資料的 CSV 檔案進行批量預測")

    print("\n" + "="*50)
    print("預測完成！")
    print("="*50)
