#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 元件建構器
負責建立和組織GUI介面元件
"""

import tkinter as tk
from tkinter import ttk
from .tooltip import ToolTip
from .app_constants import PARAM_DESCRIPTIONS


class GuiBuilder:
    """GUI 建構器類別"""

    def __init__(self, app_instance):
        """
        初始化GUI建構器

        Args:
            app_instance: 應用程式實例，用於存取GUI變數
        """
        self.app = app_instance

    def create_label_with_tooltip(self, parent, text, param_key, row, column, sticky="w", padx=5, pady=5):
        """建立帶有工具提示的標籤"""
        # 建立包含標籤和問號的框架
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=row, column=column,
                         sticky=sticky, padx=padx, pady=pady)

        # 建立標籤
        label = ttk.Label(label_frame, text=text)
        label.pack(side=tk.LEFT)

        # 建立幫助圖示 - 使用更美觀的圓形問號
        help_label = ttk.Label(label_frame, text="ⓘ",
                               foreground="#0078d4", cursor="hand2",
                               font=("Segoe UI Symbol", 12))
        help_label.pack(side=tk.LEFT, padx=(2, 0))

        # 添加工具提示
        if param_key in PARAM_DESCRIPTIONS:
            ToolTip(help_label, PARAM_DESCRIPTIONS[param_key])

        return label_frame

    def create_scrollable_frame(self, parent):
        """建立可捲動的主框架"""
        # 建立主要的可捲動區域
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 建立捲動畫布
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(
            main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 添加滑鼠滾輪支援
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # 打包捲動元件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame

    def create_data_processing_group(self, parent):
        """建立資料處理參數區塊"""
        data_group = ttk.LabelFrame(parent, text="資料處理參數")
        data_group.pack(fill=tk.X, padx=5, pady=5)

        # 測試集比例
        self.create_label_with_tooltip(
            data_group, "測試集比例 (TEST_SIZE):", "TEST_SIZE", 0, 0)
        ttk.Entry(data_group, textvariable=self.app.test_size, width=15,
                  validate='key', validatecommand=self.app.validate_ratio).grid(
            row=0, column=1, padx=5, pady=5)

        # 隨機種子
        self.create_label_with_tooltip(
            data_group, "隨機種子 (RANDOM_STATE):", "RANDOM_STATE", 0, 2)
        ttk.Entry(data_group, textvariable=self.app.random_state, width=15,
                  validate='key', validatecommand=self.app.validate_positive_int).grid(
            row=0, column=3, padx=5, pady=5)

        # 相似度閾值
        self.create_label_with_tooltip(
            data_group, "相似度閾值 (SIMILARITY_CUTOFF):", "SIMILARITY_CUTOFF", 1, 0)
        ttk.Entry(data_group, textvariable=self.app.similarity_cutoff, width=15,
                  validate='key', validatecommand=self.app.validate_ratio).grid(
            row=1, column=1, padx=5, pady=5)

        # 類別閾值
        self.create_label_with_tooltip(
            data_group, "類別數量閾值 (CATEGORICAL_THRESHOLD):", "CATEGORICAL_THRESHOLD", 1, 2)
        ttk.Entry(data_group, textvariable=self.app.categorical_threshold, width=15,
                  validate='key', validatecommand=self.app.validate_positive_int).grid(
            row=1, column=3, padx=5, pady=5)

        # 相似度匹配數量
        self.create_label_with_tooltip(
            data_group, "模糊匹配返回數量 (SIMILARITY_MATCHES_COUNT):", "SIMILARITY_MATCHES_COUNT", 2, 0)
        ttk.Entry(data_group, textvariable=self.app.similarity_matches_count, width=15,
                  validate='key', validatecommand=self.app.validate_positive_int).grid(
            row=2, column=1, padx=5, pady=5)

    def create_model_parameters_group(self, parent):
        """建立模型參數區塊"""
        model_group = ttk.LabelFrame(parent, text="模型參數")
        model_group.pack(fill=tk.X, padx=5, pady=5)

        # 樹的數量
        self.create_label_with_tooltip(
            model_group, "樹的數量 (N_ESTIMATORS):", "MODEL_N_ESTIMATORS", 0, 0)
        ttk.Entry(model_group, textvariable=self.app.model_n_estimators, width=15,
                  validate='key', validatecommand=self.app.validate_n_estimators).grid(
            row=0, column=1, padx=5, pady=5)

        # 學習率
        self.create_label_with_tooltip(
            model_group, "學習率 (LEARNING_RATE):", "MODEL_LEARNING_RATE", 0, 2)
        ttk.Entry(model_group, textvariable=self.app.model_learning_rate, width=15,
                  validate='key', validatecommand=self.app.validate_learning_rate).grid(
            row=0, column=3, padx=5, pady=5)

        # 葉子節點數
        self.create_label_with_tooltip(
            model_group, "葉子節點數 (NUM_LEAVES):", "MODEL_NUM_LEAVES", 1, 0)
        ttk.Entry(model_group, textvariable=self.app.model_num_leaves, width=15,
                  validate='key', validatecommand=self.app.validate_num_leaves).grid(
            row=1, column=1, padx=5, pady=5)

        # 正例權重
        self.create_label_with_tooltip(
            model_group, "正例權重 (SCALE_POS_WEIGHT):", "MODEL_SCALE_POS_WEIGHT", 1, 2)
        ttk.Entry(model_group, textvariable=self.app.model_scale_pos_weight, width=15,
                  validate='key', validatecommand=self.app.validate_positive_float).grid(
            row=1, column=3, padx=5, pady=5)

        # 並行工作數
        self.create_label_with_tooltip(
            model_group, "並行工作數 (N_JOBS):", "MODEL_N_JOBS", 2, 0)
        n_jobs_combo = ttk.Combobox(model_group, textvariable=self.app.model_n_jobs,
                                    values=["-1", "1", "2", "4", "8", "16"], width=12, state="readonly")
        n_jobs_combo.grid(row=2, column=1, padx=5, pady=5)

        # 詳細程度
        self.create_label_with_tooltip(
            model_group, "詳細程度 (VERBOSE):", "MODEL_VERBOSE", 2, 2)
        verbose_combo = ttk.Combobox(model_group, textvariable=self.app.model_verbose,
                                     values=["-1", "0", "1", "2"], width=12, state="readonly")
        verbose_combo.grid(row=2, column=3, padx=5, pady=5)

    def create_tuning_parameters_group(self, parent):
        """建立超參數調優參數區塊"""
        tuning_group = ttk.LabelFrame(parent, text="超參數調優參數")
        tuning_group.pack(fill=tk.X, padx=5, pady=5)

        # 交叉驗證折數
        self.create_label_with_tooltip(
            tuning_group, "交叉驗證折數 (CV_FOLDS):", "CV_FOLDS", 0, 0)
        ttk.Entry(tuning_group, textvariable=self.app.cv_folds, width=15,
                  validate='key', validatecommand=self.app.validate_cv_folds).grid(
            row=0, column=1, padx=5, pady=5)

        # 特徵重要性重複次數
        self.create_label_with_tooltip(
            tuning_group, "特徵重要性重複次數 (IMPORTANCE_N_REPEATS):", "IMPORTANCE_N_REPEATS", 0, 2)
        ttk.Entry(tuning_group, textvariable=self.app.importance_n_repeats, width=15,
                  validate='key', validatecommand=self.app.validate_positive_int).grid(
            row=0, column=3, padx=5, pady=5)

        # 網格搜尋詳細程度（基本）
        self.create_label_with_tooltip(
            tuning_group, "網格搜尋詳細程度-基本:", "GRID_SEARCH_VERBOSE_BASIC", 1, 0)
        ttk.Entry(tuning_group, textvariable=self.app.grid_search_verbose_basic, width=15,
                  validate='key', validatecommand=self.app.validate_positive_int).grid(
            row=1, column=1, padx=5, pady=5)

        # 網格搜尋詳細程度（詳細）
        self.create_label_with_tooltip(
            tuning_group, "網格搜尋詳細程度-詳細:", "GRID_SEARCH_VERBOSE_DETAILED", 1, 2)
        ttk.Entry(tuning_group, textvariable=self.app.grid_search_verbose_detailed, width=15,
                  validate='key', validatecommand=self.app.validate_positive_int).grid(
            row=1, column=3, padx=5, pady=5)

        # 評分指標
        self.create_label_with_tooltip(
            tuning_group, "主要評分指標 (SCORING_METRIC):", "SCORING_METRIC", 2, 0)
        scoring_combo = ttk.Combobox(tuning_group, textvariable=self.app.scoring_metric,
                                     values=['f1_macro', 'roc_auc',
                                             'balanced_accuracy'],
                                     width=12, state="readonly")
        scoring_combo.grid(row=2, column=1, padx=5, pady=5)

        # 特徵重要性評分
        self.create_label_with_tooltip(
            tuning_group, "特徵重要性評分 (IMPORTANCE_SCORING):", "IMPORTANCE_SCORING", 2, 2)
        importance_combo = ttk.Combobox(tuning_group, textvariable=self.app.importance_scoring,
                                        values=['f1_macro', 'roc_auc',
                                                'balanced_accuracy'],
                                        width=12, state="readonly")
        importance_combo.grid(row=2, column=3, padx=5, pady=5)

    def create_file_paths_group(self, parent):
        """建立檔案路徑參數區塊"""
        files_group = ttk.LabelFrame(parent, text="檔案路徑參數")
        files_group.pack(fill=tk.X, padx=5, pady=5)

        # 訓練資料路徑
        self.create_label_with_tooltip(
            files_group, "訓練資料路徑:", "TRAIN_DATA_PATH", 0, 0)
        ttk.Entry(files_group, textvariable=self.app.train_data_path, width=40).grid(
            row=0, column=1, padx=5, pady=5, columnspan=2)
        self.app.browse_train_data_button = ttk.Button(
            files_group, text="瀏覽", command=self.app.browse_train_data)
        self.app.browse_train_data_button.grid(row=0, column=3, padx=5, pady=5)

        # 目標欄位名稱
        self.create_label_with_tooltip(
            files_group, "目標欄位名稱 (TARGET_COLUMN):", "TARGET_COLUMN", 1, 0)
        ttk.Entry(files_group, textvariable=self.app.target_column, width=40).grid(
            row=1, column=1, padx=5, pady=5, columnspan=2)

        # 排除欄位
        self.create_label_with_tooltip(
            files_group, "排除欄位 (EXCLUDE_COLUMNS):", "EXCLUDE_COLUMNS", 2, 0)
        ttk.Entry(files_group, textvariable=self.app.exclude_columns, width=40).grid(
            row=2, column=1, padx=5, pady=5, columnspan=2)

        # 模型輸出資料夾
        self.create_label_with_tooltip(
            files_group, "模型輸出資料夾:", "MODEL_OUTPUT_FOLDER", 3, 0)
        ttk.Entry(files_group, textvariable=self.app.model_output_folder, width=40).grid(
            row=3, column=1, padx=5, pady=5, columnspan=2)
        self.app.browse_output_folder_button = ttk.Button(
            files_group, text="瀏覽", command=self.app.browse_model_output_folder)
        self.app.browse_output_folder_button.grid(
            row=3, column=3, padx=5, pady=5)

        # 模型檔案名稱
        self.create_label_with_tooltip(
            files_group, "模型檔案名稱 (請包含副檔名):", "MODEL_FILENAME", 4, 0)
        ttk.Entry(files_group, textvariable=self.app.model_filename, width=40).grid(
            row=4, column=1, padx=5, pady=5, columnspan=2)

    def create_control_panel(self, parent):
        """建立執行控制面板"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 運行模式選擇
        mode_frame = ttk.LabelFrame(control_frame, text="運行模式選擇")
        mode_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(mode_frame, text="1: 僅訓練模型", variable=self.app.run_mode, value="1").pack(
            anchor="w", padx=10, pady=2)
        ttk.Radiobutton(mode_frame, text="2: 僅超參數調優", variable=self.app.run_mode, value="2").pack(
            anchor="w", padx=10, pady=2)
        ttk.Radiobutton(mode_frame, text="3: 超參數優調並訓練模型", variable=self.app.run_mode, value="3").pack(
            anchor="w", padx=10, pady=2)

        # 執行按鈕
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.app.run_button = ttk.Button(
            button_frame, text="開始執行", command=self.app.run_training)
        self.app.run_button.pack(side=tk.LEFT, padx=5)

        self.app.stop_button = ttk.Button(
            button_frame, text="停止執行", command=self.app.stop_training, state="disabled")
        self.app.stop_button.pack(side=tk.LEFT, padx=5)

        self.app.reset_button = ttk.Button(
            button_frame, text="重設參數", command=self.app.reset_params)
        self.app.reset_button.pack(side=tk.LEFT, padx=5)

        self.app.import_button = ttk.Button(
            button_frame, text="匯入設定", command=self.app.import_config)
        self.app.import_button.pack(side=tk.LEFT, padx=5)

        self.app.export_button = ttk.Button(
            button_frame, text="匯出設定", command=self.app.export_config)
        self.app.export_button.pack(side=tk.LEFT, padx=5)

        # 顯示 console 提示訊息
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill=tk.X, pady=5)

        info_label = ttk.Label(info_frame,
                               text="💡 執行過程中的詳細訊息將顯示在 Console 視窗中",
                               foreground="blue")
        info_label.pack(pady=5)
