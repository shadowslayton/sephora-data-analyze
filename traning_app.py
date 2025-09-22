#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sephora 產品推薦模型訓練應用程式介面
提供圖形化介面來設定參數並執行模型訓練
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

# 匯入重構後的模組
from app_utils.parameter_validator import ParameterValidator
from app_utils.config_manager import ConfigManager
from app_utils.gui_builder import GuiBuilder
from app_utils.app_constants import PARAM_MAPPING, BEST_PARAMS_MAPPING


class ModelTrainingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sephora 產品推薦模型訓練器")
        self.root.geometry("900x800")  # 縮小高度，因為移除了狀態顯示區域

        # 建立參數映射字典
        self.param_mapping = PARAM_MAPPING

        # 設定預設參數值
        self.setup_default_values()

        # 訓練狀態
        self.is_training = False
        self.training_thread = None

        # GUI 元件初始化（將在 create_widgets 中建立）
        self.run_button = None
        self.stop_button = None
        self.reset_button = None
        self.import_button = None
        self.export_button = None
        self.browse_train_data_button = None
        self.browse_output_folder_button = None

        # 初始化輔助物件
        self.validator = ParameterValidator(self)
        self.config_manager = ConfigManager(self)
        self.gui_builder = GuiBuilder(self)

        # 註冊驗證函式
        self.register_validation_functions()

        # 建立介面
        self.create_widgets()

    def setup_default_values(self):
        """設定預設參數值"""
        # 基本設定參數
        self.target_column = tk.StringVar(value="")
        self.exclude_columns = tk.StringVar(value="")

        # 資料處理參數
        self.test_size = tk.DoubleVar(value=0.2)
        self.random_state = tk.IntVar(value=42)
        self.similarity_cutoff = tk.DoubleVar(value=0.6)
        self.categorical_threshold = tk.IntVar(value=10)
        self.similarity_matches_count = tk.IntVar(value=1)

        # 模型參數
        self.model_n_estimators = tk.IntVar(value=250)
        self.model_learning_rate = tk.DoubleVar(value=0.01)
        self.model_num_leaves = tk.IntVar(value=60)
        self.model_scale_pos_weight = tk.DoubleVar(value=0.55)
        self.model_n_jobs = tk.IntVar(value=-1)
        self.model_verbose = tk.IntVar(value=0)

        # 超參數調優參數
        self.cv_folds = tk.IntVar(value=5)
        self.importance_n_repeats = tk.IntVar(value=5)
        self.grid_search_verbose_basic = tk.IntVar(value=2)
        self.grid_search_verbose_detailed = tk.IntVar(value=3)
        self.scoring_metric = tk.StringVar(value='f1_macro')
        self.importance_scoring = tk.StringVar(value='f1_macro')

        # 檔案路徑參數
        self.train_data_path = tk.StringVar(value="")
        self.model_output_folder = tk.StringVar(value="")
        self.model_filename = tk.StringVar(value="")

        # 運行模式
        self.run_mode = tk.StringVar(value="1")

    def register_validation_functions(self):
        """註冊輸入驗證函式"""
        # 註冊驗證函式到 tkinter
        self.validate_float = (self.root.register(
            self.validator.validate_float_input), '%P', '%W')
        self.validate_int = (self.root.register(
            self.validator.validate_int_input), '%P', '%W')
        self.validate_positive_float = (self.root.register(
            self.validator.validate_positive_float_input), '%P', '%W')
        self.validate_positive_int = (self.root.register(
            self.validator.validate_positive_int_input), '%P', '%W')
        self.validate_ratio = (self.root.register(
            self.validator.validate_ratio_input), '%P', '%W')
        self.validate_learning_rate = (self.root.register(
            self.validator.validate_learning_rate_input), '%P', '%W')
        self.validate_n_estimators = (self.root.register(
            self.validator.validate_n_estimators_input), '%P', '%W')
        self.validate_num_leaves = (self.root.register(
            self.validator.validate_num_leaves_input), '%P', '%W')
        self.validate_cv_folds = (self.root.register(
            self.validator.validate_cv_folds_input), '%P', '%W')

    def create_widgets(self):
        """建立介面元件"""
        # 建立主要的可捲動區域
        scrollable_frame = self.gui_builder.create_scrollable_frame(self.root)

        # 在可捲動區域中建立所有參數區塊
        self.gui_builder.create_data_processing_group(scrollable_frame)
        self.gui_builder.create_model_parameters_group(scrollable_frame)
        self.gui_builder.create_tuning_parameters_group(scrollable_frame)
        self.gui_builder.create_file_paths_group(scrollable_frame)

        # 執行控制面板
        self.gui_builder.create_control_panel(self.root)

    def browse_train_data(self):
        """瀏覽訓練資料檔案"""
        filename = filedialog.askopenfilename(
            title="選擇訓練資料檔案",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.train_data_path.set(filename)

    def browse_model_output_folder(self):
        """瀏覽模型輸出資料夾"""
        folder = filedialog.askdirectory(
            title="選擇模型輸出資料夾"
        )
        if folder:
            self.model_output_folder.set(folder)

    def update_status(self, message):
        """更新狀態顯示到 console"""
        print(f"[狀態] {message}")

    def print_console_hint(self):
        """顯示提示使用者查看 console 的對話框"""
        messagebox.showinfo(
            "執行中",
            "模型訓練已開始！\n\n" +
            "詳細執行過程和結果將顯示在 Console 視窗中。\n" +
            "請查看執行此程式的終端機視窗來監控進度。"
        )

    def run_training(self):
        """執行訓練"""
        if self.is_training:
            return

        # 驗證參數
        errors = self.validator.validate_all_parameters()
        if errors:
            error_msg = "參數驗證失敗:\n" + \
                "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("參數錯誤", error_msg)
            return

        # 設定訓練狀態和按鈕
        self.is_training = True

        # 立即更新UI狀態（在主執行緒中）
        self._disable_all_buttons_except_stop()

        # 顯示提示訊息
        self.print_console_hint()

        # 在新執行緒中執行訓練
        self.training_thread = threading.Thread(
            target=self._run_training_thread)
        self.training_thread.daemon = True
        self.training_thread.start()

    def _run_training_thread(self):
        """在背景執行緒中執行訓練"""
        try:
            # 重設模組的停止標誌
            from ai_utils import model_traning
            model_traning.reset_stop_training_flag()

            self.update_status("=== 開始執行 Sephora 產品推薦模型訓練 ===")
            self.update_status(f"運行模式: {self.run_mode.get()}")

            # 檢查是否被請求停止
            if not self.is_training:
                self.update_status("訓練已被停止")
                return

            # 產生臨時配置檔案
            config_code = self.config_manager.generate_config_code()

            # 直接匯入模型訓練模組（避免 pickle 問題）
            from ai_utils import model_traning

            # 執行配置程式碼來更新模組中的全域變數
            exec(config_code, model_traning.__dict__)

            # 根據選擇的模式執行相應的功能
            # 解析排除欄位列表
            exclude_cols = None
            if self.exclude_columns.get().strip():
                exclude_cols = [
                    col.strip() for col in self.exclude_columns.get().split(',') if col.strip()]

            # 檢查是否被請求停止
            if not self.is_training:
                self.update_status("訓練已被停止")
                return

            if self.run_mode.get() == "1":
                self.update_status("執行模式: 僅訓練模型")
                # 明確傳遞輸出路徑和排除欄位
                output_path = os.path.join(
                    self.model_output_folder.get(), self.model_filename.get())
                results = model_traning.train_model(
                    output_path=output_path, exclude_columns=exclude_cols)
                self.update_status("模型訓練完成!")

            elif self.run_mode.get() == "2":
                self.update_status("執行模式: 僅超參數調優")

                # 檢查是否被請求停止
                if not self.is_training:
                    self.update_status("訓練已被停止")
                    return

                tuning_results = model_traning.hyperparameter_tuning(
                    exclude_columns=exclude_cols)

                # 檢查是否被請求停止
                if not self.is_training:
                    self.update_status("訓練已被停止")
                    return

                if tuning_results and 'best_params' in tuning_results:
                    self.update_status("超參數調優完成!")

                    # 顯示最佳參數
                    best_params = tuning_results['best_params']
                    self.update_status("\n🎯 找到的最佳參數:")
                    for param, value in best_params.items():
                        clean_param = param.replace('model__', '')
                        self.update_status(f"  {clean_param}: {value}")

                    # 自動回填最佳參數到GUI欄位
                    self.apply_best_parameters(best_params)
                else:
                    self.update_status("❌ 超參數調優失敗或未返回結果")

            elif self.run_mode.get() == "3":
                self.update_status("執行模式: 先超參數調優，再訓練模型")

                # 檢查是否被請求停止
                if not self.is_training:
                    self.update_status("訓練已被停止")
                    return

                # 先執行超參數調優
                tuning_results = model_traning.hyperparameter_tuning(
                    exclude_columns=exclude_cols)

                if tuning_results:
                    # 檢查是否被請求停止
                    if not self.is_training:
                        self.update_status("訓練已被停止")
                        return

                    # 提取最佳參數
                    best_params = tuning_results['best_params']

                    # 顯示最佳參數
                    self.update_status("\n🎯 找到的最佳參數:")
                    for param, value in best_params.items():
                        clean_param = param.replace('model__', '')
                        self.update_status(f"  {clean_param}: {value}")

                    # 自動回填最佳參數到GUI欄位
                    self.apply_best_parameters(best_params)

                    self.update_status("\n現在用最佳參數訓練最終模型...")

                    # 檢查是否被請求停止
                    if not self.is_training:
                        self.update_status("訓練已被停止")
                        return

                    # 用最佳參數訓練模型
                    output_path = os.path.join(
                        self.model_output_folder.get(), self.model_filename.get())
                    results = model_traning.train_model(
                        output_path=output_path,
                        exclude_columns=exclude_cols,
                        n_estimators=best_params.get(
                            'model__n_estimators', model_traning.MODEL_N_ESTIMATORS),
                        learning_rate=best_params.get(
                            'model__learning_rate', model_traning.MODEL_LEARNING_RATE),
                        num_leaves=best_params.get(
                            'model__num_leaves', model_traning.MODEL_NUM_LEAVES),
                        scale_pos_weight=best_params.get(
                            'model__scale_pos_weight', model_traning.MODEL_SCALE_POS_WEIGHT)
                    )

                    self.update_status("\n所有訓練完成!")
                else:
                    self.update_status("❌ 超參數調優失敗，無法繼續訓練")

            self.update_status("=== 執行完成 ===")

        except Exception as e:
            self.update_status(f"❌ 執行過程中發生錯誤: {str(e)}")

        finally:
            # 重置UI狀態
            self.root.after(0, self._reset_ui_state)

    def _disable_all_buttons_except_stop(self):
        """禁用所有按鈕，除了停止按鈕"""
        buttons_to_disable = [
            self.run_button,
            self.reset_button,
            self.import_button,
            self.export_button,
            self.browse_train_data_button,
            self.browse_output_folder_button
        ]

        for button in buttons_to_disable:
            if button:
                button.config(state="disabled")

        # 啟用停止按鈕
        if self.stop_button:
            self.stop_button.config(state="normal")

    def _enable_all_buttons_except_stop(self):
        """啟用所有按鈕，除了停止按鈕"""
        buttons_to_enable = [
            self.run_button,
            self.reset_button,
            self.import_button,
            self.export_button,
            self.browse_train_data_button,
            self.browse_output_folder_button
        ]

        for button in buttons_to_enable:
            if button:
                button.config(state="normal")

        # 禁用停止按鈕
        if self.stop_button:
            self.stop_button.config(state="disabled")

    def _reset_ui_state(self):
        """重設UI狀態"""
        self.is_training = False
        self._enable_all_buttons_except_stop()

        # 顯示執行完成訊息
        messagebox.showinfo("執行完成", "模型訓練任務已完成！\n請查看 Console 視窗獲取詳細結果。")

    def apply_best_parameters(self, best_params):
        """自動回填最佳參數到GUI欄位"""
        print("\n🔄 自動回填最佳參數到介面欄位...")

        updated_params = []

        # 使用常數中的參數映射
        for param_key, value in best_params.items():
            if param_key in BEST_PARAMS_MAPPING:
                gui_attr, param_type = BEST_PARAMS_MAPPING[param_key]

                # 檢查GUI變數是否存在
                if hasattr(self, gui_attr):
                    try:
                        # 根據類型轉換數值
                        if param_type == 'int':
                            converted_value = int(value)
                        elif param_type == 'float':
                            converted_value = float(value)
                        else:
                            converted_value = value

                        # 使用root.after確保在主執行緒中更新GUI
                        def update_param(attr=gui_attr, val=converted_value, name=param_key):
                            getattr(self, attr).set(val)

                        self.root.after(0, update_param)
                        updated_params.append(
                            f"{param_key.replace('model__', '')}: {value}")

                    except (ValueError, TypeError) as e:
                        print(f"⚠️ 參數 {param_key} 回填失敗: {str(e)}")

        if updated_params:
            print("✅ 已自動回填以下參數:")
            for param in updated_params:
                print(f"   • {param}")
            print("🎯 您可以在介面上看到更新後的參數值")
        else:
            print("⚠️ 沒有找到可回填的參數")

    def stop_training(self):
        """停止訓練"""
        print("[狀態] 使用者請求停止訓練...")

        if self.is_training:
            self.is_training = False
            self.update_status("⏹️ 正在停止訓練任務...")

            # 通知模型訓練模組停止
            try:
                from ai_utils import model_traning
                model_traning.set_stop_training_flag(True)
                print("[狀態] 已向訓練模組發送停止信號")
            except ImportError:
                print("[警告] 無法載入 model_traning 模組，僅設定 GUI 停止標誌")

            # 立即重設UI狀態，不等待執行緒結束
            self._reset_ui_state_without_popup()

            # 如果執行緒還在執行，等待一小段時間讓它自然結束
            if self.training_thread and self.training_thread.is_alive():
                self.root.after(1000, self._check_thread_status)
        else:
            print("[狀態] 目前沒有進行中的訓練任務")

    def _check_thread_status(self):
        """檢查執行緒狀態"""
        if self.training_thread and self.training_thread.is_alive():
            print("[狀態] 等待訓練任務結束...")
            self.root.after(1000, self._check_thread_status)
        else:
            print("[狀態] 訓練任務已停止")

    def _reset_ui_state_without_popup(self):
        """重設UI狀態（不顯示完成訊息）"""
        self.is_training = False
        self._enable_all_buttons_except_stop()

    def reset_params(self):
        """重設所有參數為預設值"""
        if messagebox.askyesno("確認重設", "確定要重設所有參數為預設值嗎？"):
            self.config_manager.reset_to_defaults()
            print("[狀態] 參數已重設為預設值")
            messagebox.showinfo("重設完成", "所有參數已重設為預設值")

    def export_config(self):
        """匯出配置到檔案"""
        filename = filedialog.asksaveasfilename(
            title="匯出配置檔案",
            defaultextension=".config",
            filetypes=[("Config files", "*.config"),
                       ("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config_manager.export_config(filename)
                print(f"[狀態] 配置已匯出到: {filename}")
                messagebox.showinfo("匯出成功", f"配置已成功匯出到:\n{filename}")
            except Exception as e:
                messagebox.showerror("錯誤", str(e))

    def import_config(self):
        """從檔案匯入配置"""
        filename = filedialog.askopenfilename(
            title="匯入配置檔案",
            filetypes=[("Config files", "*.config"),
                       ("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            try:
                updated_count = self.config_manager.import_config(filename)
                print(f"[狀態] 成功更新 {updated_count} 個參數")
                print(f"[狀態] 配置已從檔案匯入: {filename}")
                messagebox.showinfo("匯入成功", f"成功更新 {updated_count} 個參數")
            except Exception as e:
                messagebox.showerror("錯誤", str(e))


def main():
    """主程式入口"""
    print("=== Sephora 產品推薦模型訓練器啟動中 ===")

    # 檢查是否能匯入必要的模組（適用於開發和打包環境）
    try:
        print("正在匯入 ai_utils 模組...")
        from ai_utils import model_traning
        print("ai_utils 模組匯入成功")

        print("正在建立 tkinter 根視窗...")
        root = tk.Tk()
        print("tkinter 根視窗建立成功")

        print("正在初始化應用程式...")
        app = ModelTrainingApp(root)
        print("應用程式初始化完成")

        # 設定應用程式圖示（如果有的話）
        try:
            root.iconbitmap('icon.ico')  # 可選
        except:
            pass

        # 確保視窗在最前面
        root.lift()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))

        print("正在啟動 GUI 主迴圈...")
        print("如果您看到這個訊息但沒有看到視窗，請檢查工作列或嘗試使用 Alt+Tab 切換視窗")

        # 執行應用程式
        root.mainloop()
        print("應用程式已正常結束")

    except ImportError as e:
        print(f"❌ 無法載入必要的模組: {e}")
        print("請確認您在正確的目錄中執行此程式")
        input("按 Enter 鍵退出...")  # 讓使用者看到錯誤訊息
    except Exception as e:
        print(f"❌ 應用程式啟動時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        input("按 Enter 鍵退出...")  # 讓使用者看到錯誤訊息


if __name__ == "__main__":
    main()
