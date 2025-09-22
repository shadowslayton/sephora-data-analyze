import os
from sklearn.model_selection import GridSearchCV, StratifiedKFold, ParameterGrid
from sklearn.inspection import permutation_importance
import plotly.figure_factory as ff
import plotly.graph_objects as go
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_curve,
    f1_score, roc_auc_score, balanced_accuracy_score
)
from sklearn.model_selection import train_test_split, cross_val_score
from lightgbm import LGBMClassifier
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.base import BaseEstimator, TransformerMixin
import pickle
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter("ignore", pd.errors.PerformanceWarning)

# 全域停止標誌
_stop_training_flag = False


def set_stop_training_flag(stop=True):
    """設定停止訓練標誌"""
    global _stop_training_flag
    _stop_training_flag = stop
    if stop:
        print("[停止機制] 已設定停止訓練標誌")


def is_training_stopped():
    """檢查是否應該停止訓練"""
    global _stop_training_flag
    return _stop_training_flag


def reset_stop_training_flag():
    """重設停止訓練標誌"""
    global _stop_training_flag
    _stop_training_flag = False


class StoppableGridSearchCV:
    """可停止的超參數搜尋類別"""

    def __init__(self, estimator, param_grid, scoring, cv, verbose=0, n_jobs=1):
        self.estimator = estimator
        self.param_grid = param_grid
        self.scoring = scoring
        self.cv = cv
        self.verbose = verbose
        self.n_jobs = n_jobs

        # 結果儲存
        self.best_params_ = None
        self.best_score_ = -np.inf
        self.best_estimator_ = None
        self.cv_results_ = []
        self.total_combinations_ = 0
        self.completed_combinations_ = 0

    def fit(self, X, y):
        """執行可停止的網格搜尋"""
        param_list = list(ParameterGrid(self.param_grid))
        self.total_combinations_ = len(param_list)

        print(f"開始可停止的超參數搜尋，共 {self.total_combinations_} 個參數組合...")

        for i, params in enumerate(param_list):
            # 每次迭代前檢查停止標誌
            if is_training_stopped():
                print(
                    f"[停止機制] 超參數搜尋在第 {i+1}/{self.total_combinations_} 個組合時被停止")
                if self.best_params_ is not None:
                    print(f"[停止機制] 返回目前最佳結果 (分數: {self.best_score_:.4f})")
                    return self
                else:
                    print("[停止機制] 尚未完成任何參數組合，返回空結果")
                    return None

            if self.verbose > 0:
                print(f"[{i+1}/{self.total_combinations_}] 測試參數組合: {params}")

            # 設定參數並訓練模型
            model_clone = self._clone_estimator_with_params(params)

            try:
                # 執行交叉驗證
                cv_scores = cross_val_score(
                    model_clone, X, y,
                    cv=self.cv,
                    scoring=self.scoring,
                    n_jobs=1  # 設為1避免並行時的停止檢查問題
                )

                mean_score = np.mean(cv_scores)
                std_score = np.std(cv_scores)

                # 儲存結果
                self.cv_results_.append({
                    'params': params,
                    'mean_test_score': mean_score,
                    'std_test_score': std_score,
                    'cv_scores': cv_scores
                })

                # 更新最佳結果
                if mean_score > self.best_score_:
                    self.best_score_ = mean_score
                    self.best_params_ = params.copy()
                    self.best_estimator_ = model_clone

                if self.verbose > 0:
                    print(f"   分數: {mean_score:.4f} (±{std_score:.4f})")
                    if mean_score > self.best_score_:
                        print(f"   🎯 新的最佳分數!")

            except Exception as e:
                print(f"   ❌ 參數組合 {params} 訓練失敗: {str(e)}")
                continue

            self.completed_combinations_ = i + 1

            # 在每個組合完成後再次檢查停止標誌
            if is_training_stopped():
                print(
                    f"[停止機制] 超參數搜尋在完成第 {i+1}/{self.total_combinations_} 個組合後被停止")
                print(f"[停止機制] 返回目前最佳結果 (分數: {self.best_score_:.4f})")
                return self

        print(f"✅ 超參數搜尋完成，測試了 {self.completed_combinations_} 個參數組合")
        return self

    def _clone_estimator_with_params(self, params):
        """複製估計器並設定參數"""
        from sklearn.base import clone
        estimator_clone = clone(self.estimator)
        estimator_clone.set_params(**params)
        return estimator_clone


# 必要參數配置
TARGET_COLUMN = 'is_recommended'

# 資料處理參數
TEST_SIZE = 0.2
RANDOM_STATE = 42
SIMILARITY_CUTOFF = 0.6
CATEGORICAL_THRESHOLD = 10  # 整數型類別數量閾值
SIMILARITY_MATCHES_COUNT = 1  # 模糊匹配返回數量

# 模型參數
MODEL_N_ESTIMATORS = 250
MODEL_LEARNING_RATE = 0.01
MODEL_NUM_LEAVES = 60
MODEL_SCALE_POS_WEIGHT = 0.55
# 智能設定 n_jobs：如果 CPU 核心數 > 4，使用 -1，否則使用 max(1, CPU_COUNT-1)
MODEL_N_JOBS = -1
MODEL_VERBOSE = 0  # -1/0: 靜默, 1: 基本資訊, 2: 詳細資訊

# 超參數調優參數
CV_FOLDS = 5
IMPORTANCE_N_REPEATS = 5
GRID_SEARCH_VERBOSE_BASIC = 2
GRID_SEARCH_VERBOSE_DETAILED = 3
SCORING_METRIC = 'f1_macro'        # 主要評分指標：f1_macro, roc_auc, balanced_accuracy
IMPORTANCE_SCORING = 'f1_macro'    # 特徵重要性評分：建議與主要指標保持一致

# 檔案路徑參數
DEFAULT_TRAIN_DATA_PATH = "traning_data/train_data(top20).csv"
DEFAULT_MODEL_OUTPUT_PATH = "output_models/model_final.bin"

# 超參數搜尋範圍
PARAM_GRID = {
    'model__n_estimators': [250, 300],
    'model__learning_rate': [0.01, 0.005],
    'model__num_leaves': [40, 60],
    'model__scale_pos_weight': [0.55, 0.56, 0.52],
    'model__reg_alpha': [0, 0.5, 1],
}


def validate_input_parameters(**kwargs):
    """
    驗證輸入參數的合理性

    參數:
        **kwargs: 要驗證的參數字典

    回傳:
        bool: True 如果所有參數都有效
    """
    errors = []

    # 驗證測試集比例
    if 'test_size' in kwargs:
        test_size = kwargs['test_size']
        if not (0 < test_size < 1):
            errors.append(f"test_size 必須在 0 和 1 之間，但得到: {test_size}")

    # 驗證隨機種子
    if 'random_state' in kwargs:
        random_state = kwargs['random_state']
        if not isinstance(random_state, int) or random_state < 0:
            errors.append(f"random_state 必須是非負整數，但得到: {random_state}")

    # 驗證模型參數
    if 'n_estimators' in kwargs:
        n_estimators = kwargs['n_estimators']
        if not isinstance(n_estimators, int) or n_estimators <= 0:
            errors.append(f"n_estimators 必須是正整數，但得到: {n_estimators}")

    if 'learning_rate' in kwargs:
        learning_rate = kwargs['learning_rate']
        if not (0 < learning_rate <= 1):
            errors.append(f"learning_rate 必須在 0 和 1 之間，但得到: {learning_rate}")

    if errors:
        print("❌ 參數驗證失敗:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True


def load_and_validate_data(data_path, feature_columns=None, target_column=None, default_target_column=TARGET_COLUMN, exclude_columns=None):
    """
    載入和驗證資料的通用函式

    參數:
        data_path (str): 資料檔案路徑
        feature_columns (list): 特徵欄位列表
        target_column (str): 目標欄位名稱
        default_target_column (str): 預設目標欄位名稱
        exclude_columns (list): 要排除的高相關度欄位列表，防止資料洩漏

    回傳:
        tuple: (data, feature_cols, target_col) 或 (None, None, None) 如果失敗
    """
    print("開始載入資料...")
    try:
        data = pd.read_csv(data_path)
        print(f"資料載入完成，資料形狀: {data.shape}")
    except FileNotFoundError:
        print(f"❌ 找不到檔案: {data_path}")
        return None, None, None
    except Exception as e:
        print(f"❌ 載入資料時發生錯誤: {e}")
        return None, None, None

    # 自動檢測和驗證欄位
    feature_cols, target_col, missing_cols = detect_columns(
        data, feature_columns, target_column, default_target_column, exclude_columns)
    if feature_cols is None:
        print("❌ 欄位檢測失敗")
        return None, None, None

    # 驗證資料型態
    if not validate_data_types(data, feature_cols, target_col):
        print("⚠️  資料型態驗證有警告，但仍繼續執行...")

    return data, feature_cols, target_col


def create_model_pipeline(n_estimators=MODEL_N_ESTIMATORS,
                          learning_rate=MODEL_LEARNING_RATE,
                          num_leaves=MODEL_NUM_LEAVES,
                          scale_pos_weight=MODEL_SCALE_POS_WEIGHT,
                          random_state=RANDOM_STATE):
    """
    建立模型管線的通用函式

    參數:
        n_estimators (int): 樹的數量
        learning_rate (float): 學習率
        num_leaves (int): 葉子節點數
        scale_pos_weight (float): 正樣本權重
        random_state (int): 隨機種子

    回傳:
        Pipeline: 包含預處理和模型的管線
    """
    model = LGBMClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        scale_pos_weight=scale_pos_weight,
        n_jobs=MODEL_N_JOBS,
        random_state=random_state,
        verbose=MODEL_VERBOSE
    )
    return Pipeline([('DataPreprocess', DataPreprocess()), ('model', model)])


def display_evaluation_metrics(y_true, y_pred, y_proba, dataset_name=""):
    """
    顯示評估指標的通用函式

    參數:
        y_true: 真實標籤
        y_pred: 預測標籤
        y_proba: 預測機率
        dataset_name (str): 資料集名稱
    """
    balanced_acc = balanced_accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average='macro')
    roc_auc = roc_auc_score(y_true, y_proba)

    print(f"\n=== {dataset_name}評估結果 ===")
    print(f"Balanced Accuracy: {balanced_acc:.4f}")
    print(f"F1-macro: {f1_macro:.4f}")
    print(f"ROC-AUC: {roc_auc:.4f}")
    print("\n分類報告：")
    print(classification_report(y_true, y_pred))

    return {
        'balanced_accuracy': balanced_acc,
        'f1_macro': f1_macro,
        'roc_auc': roc_auc
    }


def detect_columns(data, feature_columns=None, target_column=None, default_target_column=TARGET_COLUMN, exclude_columns=None):
    """
    自動檢測和驗證資料欄位

    參數:
        data (DataFrame): 輸入資料
        feature_columns (list): 指定的特徵欄位，None表示自動推斷（使用除目標欄位外的所有欄位）
        target_column (str): 指定的目標欄位，None表示使用必要的目標欄位
        default_target_column (str): 預設目標欄位名稱
        exclude_columns (list): 要排除的高相關度欄位列表，避免資料洩漏，如 ['rating'] (相關度0.885)

    回傳:
        tuple: (feature_columns, target_column, missing_columns)
    """
    available_columns = data.columns.tolist()

    # 設定目標欄位
    if target_column is None:
        target_column = default_target_column

    # 重要防呆：檢查目標欄位是否被包含在排除欄位中
    if exclude_columns and target_column in exclude_columns:
        print(f"❌ 參數衝突錯誤！")
        print(f"目標欄位 '{target_column}' 不能同時被指定為排除欄位")
        print(f"排除欄位列表: {exclude_columns}")
        print(f"請從排除欄位中移除目標欄位，或者更改目標欄位")
        return None, None, None

    # 自動推斷特徵欄位或使用指定欄位
    if feature_columns is None:
        # 準備要排除的欄位列表
        columns_to_exclude = [target_column]
        if exclude_columns:
            columns_to_exclude.extend(exclude_columns)

        # 自動使用所有欄位，排除目標欄位和指定排除的欄位
        feature_columns = [
            col for col in available_columns if col not in columns_to_exclude]
        print(f"🤖 自動推斷特徵欄位: {len(feature_columns)} 個欄位")
        if exclude_columns:
            print(f"   排除欄位: {columns_to_exclude}")
        print(f"   特徵欄位: {feature_columns}")

    # 驗證目標欄位是否存在
    if target_column not in available_columns:
        print(f"❌ 目標欄位檢查失敗！")
        print(f"可用欄位: {available_columns}")
        print(f"缺少目標欄位: {target_column}")
        return None, None, [target_column]

    # 檢查缺少的欄位
    all_required_columns = feature_columns + [target_column]
    missing_columns = [
        col for col in all_required_columns if col not in available_columns]

    if missing_columns:
        print(f"❌ 資料欄位檢查失敗！")
        print(f"可用欄位: {available_columns}")
        print(f"缺少欄位: {missing_columns}")
        print(f"需要欄位: {all_required_columns}")

        # 嘗試智能匹配相似欄位名稱
        suggestions = suggest_column_mapping(
            available_columns, missing_columns)
        if suggestions:
            print("\n💡 可能的欄位對應建議:")
            for missing, suggestion in suggestions.items():
                print(f"  {missing} -> {suggestion}")

        return None, None, missing_columns

    print(f"✅ 資料欄位檢查通過！")
    print(f"特徵欄位: {feature_columns}")
    print(f"目標欄位: {target_column}")

    return feature_columns, target_column, []


def suggest_column_mapping(available_columns, missing_columns,
                           cutoff=SIMILARITY_CUTOFF,
                           matches_count=SIMILARITY_MATCHES_COUNT):
    """
    智能建議欄位對應

    參數:
        available_columns (list): 可用的欄位列表
        missing_columns (list): 缺少的欄位列表
        cutoff (float): 模糊匹配的相似度閾值
        matches_count (int): 返回的匹配數量
    """
    import difflib
    suggestions = {}

    for missing in missing_columns:
        # 使用模糊匹配找相似的欄位名稱
        matches = difflib.get_close_matches(
            missing, available_columns, n=matches_count, cutoff=cutoff
        )
        if matches:
            suggestions[missing] = matches[0]

    return suggestions


def validate_data_types(data, feature_columns, target_column):
    """
    驗證資料型態
    """
    issues = []

    # 檢查目標變數
    if target_column in data.columns:
        target_values = data[target_column].dropna().unique()
        if not all(val in [0, 1, True, False] for val in target_values):
            issues.append(
                f"目標變數 '{target_column}' 不是二元分類格式 (應為 0/1 或 True/False)")

    # 檢查特徵欄位的基本資訊
    print(f"\n📊 資料概覽:")
    print(f"資料形狀: {data.shape}")
    print(f"目標變數分布:")
    print(data[target_column].value_counts())

    if issues:
        print(f"⚠️  資料型態警告:")
        for issue in issues:
            print(f"  - {issue}")

    return len(issues) == 0


class DataPreprocess(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.scaler = {}
        self.fillna_value = {}
        self.onehotencode_value = {}
        self.field_names = []
        self.final_field_names = []

    def fit(self, X, y=None, field_names=None):
        self.__init__()
        if field_names is None:
            self.field_names = X.columns.tolist()
        else:
            self.field_names = field_names

        for fname in self.field_names:
            # 自動補空值
            if (X[fname].dtype == object) or (X[fname].dtype == str):  # 字串型態欄位
                self.fillna_value[fname] = X[fname].mode()[0]  # 補眾數
                # self.fillna_value[fname] = 'np.nan'
                # self.fillna_value[fname] = np.nan # 維持空值
            elif X[fname].dtype == bool:  # 布林型態
                self.fillna_value[fname] = X[fname].mode()[0]  # 補眾數
            else:  # 數字型態
                self.fillna_value[fname] = X[fname].median()  # 補中位數

            # 自動尺度轉換(scaling)
            if (X[fname].dtype == object) or (X[fname].dtype == str):  # 字串型態欄位
                pass  # 不用轉換
            elif X[fname].dtype == bool:  # 布林型態
                pass  # 不用轉換
            else:  # 數字型態
                vc = X[fname].value_counts()
                if X[fname].isin([0, 1]).all():  # 當數值只有0跟1
                    pass  # 不用轉換
                # 是否簡單的整數型類別且數量小於閾值
                elif pd.api.types.is_integer_dtype(X[fname]) and X[fname].nunique() <= CATEGORICAL_THRESHOLD:
                    self.scaler[fname] = MinMaxScaler()
                    self.scaler[fname].fit(X[[fname]])
                else:  # 其他的數字型態
                    self.scaler[fname] = RobustScaler()
                    self.scaler[fname].fit(X[[fname]])

            # 自動編碼
            if (X[fname].dtype == object) or (X[fname].dtype == str):  # 字串型態欄位, onehotencode
                field_value = X[fname].value_counts().index
                self.onehotencode_value[fname] = field_value
                for value in field_value:
                    fn = fname+"_"+value
                    # data[fn] = (data[fname] == value).astype('int8')
                    self.final_field_names.append(fn)
            elif X[fname].dtype == bool:  # 布林型態 轉成0跟1
                # data[fname] = data[fname].astype(int)
                self.final_field_names.append(fname)
            else:  # 數字型態 不用重新編碼
                self.final_field_names.append(fname)

        return self

    def transform(self, X):
        # 如果輸入的data是dict，要先轉成dataframe
        if isinstance(X, dict):
            for fname in self.field_names:
                if fname in X:
                    X[fname] = [X[fname]]
                else:
                    X[fname] = [np.nan]
            data = pd.DataFrame(X)
        else:  # 將資料複製一份，不修改原本的資料
            data = X.copy()

        for fname in self.field_names:
            # 自動補空值
            if data[fname].isnull().any():  # 有空值
                # if fname in self.fillna_value:
                data[fname] = data[fname].fillna(self.fillna_value[fname])

            # 自動尺度轉換(scaling)
            if fname in self.scaler:
                data[fname] = self.scaler[fname].transform(data[[fname]])

            # 自動編碼
            if (data[fname].dtype == object) or (data[fname].dtype == str):  # 字串型態欄位, onehotencode
                if fname in self.onehotencode_value:
                    field_value = self.onehotencode_value[fname]
                    for value in field_value:
                        fn = fname+"_"+value
                        data[fn] = (data[fname] == value).astype('int8')
            elif data[fname].dtype == bool:  # 布林型態 轉成0跟1
                data[fname] = data[fname].astype(int)
            else:  # 數字型態 不用重新編碼
                pass
        return data[self.final_field_names]

    def save(self, file_name):
        with open(file_name, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(file_name):
        with open(file_name, "rb") as f:
            return pickle.load(f)


def train_model(data_path=DEFAULT_TRAIN_DATA_PATH,
                output_path=DEFAULT_MODEL_OUTPUT_PATH,
                show_plots=True,
                feature_columns=None,
                target_column=None,
                default_target_column=TARGET_COLUMN,
                exclude_columns=None,
                test_size=TEST_SIZE,
                random_state=RANDOM_STATE,
                n_estimators=MODEL_N_ESTIMATORS,
                learning_rate=MODEL_LEARNING_RATE,
                num_leaves=MODEL_NUM_LEAVES,
                scale_pos_weight=MODEL_SCALE_POS_WEIGHT,
                n_repeats=IMPORTANCE_N_REPEATS,
                plot_width=600,
                plot_height=500,
                plot_height_square=600):
    """
    訓練 Sephora 產品推薦模型

    參數:
        data_path (str): 訓練資料路徑
        output_path (str): 模型輸出路徑
        show_plots (bool): 是否顯示圖表
        feature_columns (list): 特徵欄位列表，None表示自動推斷
        target_column (str): 目標欄位名稱，None表示使用預設
        default_target_column (str): 預設目標欄位名稱
        exclude_columns (list): 要排除的高相關度欄位列表，避免資料洩漏，如 ['rating'] (相關度0.885)
        test_size (float): 測試集比例
        random_state (int): 隨機種子
        n_estimators (int): 模型樹的數量
        learning_rate (float): 學習率
        num_leaves (int): 葉子節點數
        scale_pos_weight (float): 正樣本權重
        n_repeats (int): 特徵重要性計算重複次數
        plot_width (int): 圖表寬度
        plot_height (int): 圖表高度
        plot_height_square (int): 方形圖表高度

    回傳:
        dict: 包含模型和評估結果的字典，如果被停止則回傳 None
    """
    # 首先檢查是否已經被請求停止
    if is_training_stopped():
        print("[停止機制] 訓練在開始前被停止")
        return None

    # 載入和驗證資料
    data, feature_cols, target_col = load_and_validate_data(
        data_path, feature_columns, target_column, default_target_column, exclude_columns)
    if data is None or feature_cols is None or target_col is None:
        return None

    # 檢查停止標誌
    if is_training_stopped():
        print("[停止機制] 訓練在資料載入後被停止")
        return None    # 準備特徵和目標變數
    try:
        X = data[feature_cols]
        y = data[target_col]
        y = y.astype(int)
    except KeyError as e:
        print(f"❌ 提取欄位時發生錯誤: {e}")
        return None
    except Exception as e:
        print(f"❌ 資料處理時發生錯誤: {e}")
        return None

    # 計算類別權重
    num_class_1 = np.sum(y == 1)
    num_class_0 = np.sum(y == 0)
    scale_pos_weight_value = num_class_0 / num_class_1
    print(f"計算出的 scale_pos_weight 值：{scale_pos_weight_value}")

    # 建立模型管線
    pipe = create_model_pipeline(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        scale_pos_weight=scale_pos_weight,
        random_state=random_state
    )

    # 分割資料
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y)

    # 檢查停止標誌
    if is_training_stopped():
        print("[停止機制] 訓練在資料分割後被停止")
        return None

    print("開始訓練模型...")
    print("[注意] 模型訓練階段無法中途停止，請等待完成...")
    pipe.fit(X_train, y_train)
    print("模型訓練完成!")

    # 檢查停止標誌
    if is_training_stopped():
        print("[停止機制] 訓練在模型訓練後被停止")
        return None

    # 評估模型
    prediction_train = pipe.predict(X_train)
    proba_train = pipe.predict_proba(X_train)[:, 1]
    train_metrics = display_evaluation_metrics(
        y_train, prediction_train, proba_train, "訓練組")

    prediction_valid = pipe.predict(X_valid)
    proba_valid = pipe.predict_proba(X_valid)[:, 1]
    valid_metrics = display_evaluation_metrics(
        y_valid, prediction_valid, proba_valid, "驗證組")

    # 顯示圖表
    if show_plots:
        # ROC 曲線 - 訓練組
        fpr_train, tpr_train, _ = roc_curve(y_train, proba_train)
        roc_fig_train = go.Figure()
        roc_fig_train.add_trace(go.Scatter(
            x=fpr_train, y=tpr_train,
            mode='lines',
            name=f'ROC 曲線 (AUC = {train_metrics["roc_auc"]:.3f})',
            line=dict(color='blue', width=2)
        ))
        roc_fig_train.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='lines',
            name='隨機猜測',
            line=dict(color='red', dash='dash')
        ))
        roc_fig_train.update_layout(
            title='訓練組 ROC 曲線',
            xaxis_title='偽陽性率 (False Positive Rate)',
            yaxis_title='真陽性率 (True Positive Rate)',
            width=plot_width,
            height=plot_height
        )
        roc_fig_train.show()

        # ROC 曲線 - 驗證組
        fpr_valid, tpr_valid, _ = roc_curve(y_valid, proba_valid)
        roc_fig_valid = go.Figure()
        roc_fig_valid.add_trace(go.Scatter(
            x=fpr_valid, y=tpr_valid,
            mode='lines',
            name=f'ROC 曲線 (AUC = {valid_metrics["roc_auc"]:.3f})',
            line=dict(color='green', width=2)
        ))
        roc_fig_valid.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='lines',
            name='隨機猜測',
            line=dict(color='red', dash='dash')
        ))
        roc_fig_valid.update_layout(
            title='驗證組 ROC 曲線',
            xaxis_title='偽陽性率 (False Positive Rate)',
            yaxis_title='真陽性率 (True Positive Rate)',
            width=plot_width,
            height=plot_height
        )
        roc_fig_valid.show()

        # 混淆矩陣
        cm = confusion_matrix(y_valid, prediction_valid)
        cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

        labels = [[f"{num}<br>({perc:.1f}%)" for num, perc in zip(row, perc_row)]
                  for row, perc_row in zip(cm, cm_percent)]

        fig = ff.create_annotated_heatmap(
            z=cm_percent,
            x=["Predicted 0", "Predicted 1"],
            y=["True 0", "True 1"],
            annotation_text=labels,
            colorscale="Blues",
            showscale=True
        )
        fig.update_layout(
            title="驗證組混淆矩陣 (Count & %)",
            xaxis_title="Predicted Label",
            yaxis_title="True Label",
            yaxis_autorange='reversed',
            width=plot_width,
            height=plot_height_square
        )
        fig.show()

    # 用全部資料重新訓練最終模型
    print("\n用全部資料重新訓練最終模型...")

    # 檢查停止標誌
    if is_training_stopped():
        print("[停止機制] 訓練在最終模型訓練前被停止")
        return None

    print("[注意] 最終模型訓練階段無法中途停止，請等待完成...")
    pipe.fit(X, y)

    # 檢查停止標誌
    if is_training_stopped():
        print("[停止機制] 訓練在最終模型訓練後被停止")
        return None

    # 儲存模型和欄位資訊
    model_info = {
        'pipeline': pipe,
        'feature_columns': feature_cols,
        'target_column': target_col
    }

    with open(output_path, "wb") as f:
        pickle.dump(model_info, f)
    print(f"模型已儲存至: {output_path}")
    print(f"包含欄位資訊: 特徵欄位={len(feature_cols)}個, 目標欄位='{target_col}'")

    # 特徵重要性分析
    print("\n計算特徵重要性...")

    # 檢查停止標誌
    if is_training_stopped():
        print("[停止機制] 訓練在特徵重要性計算前被停止")
        return None

    print("[注意] 特徵重要性計算階段無法中途停止，請等待完成...")
    result = permutation_importance(
        pipe, X, y, scoring=IMPORTANCE_SCORING, n_repeats=n_repeats, random_state=random_state)

    importances = getattr(result, 'importances_mean')
    # 使用預處理器的最終欄位名稱而不是原始欄位名稱
    preprocessor = pipe.named_steps['DataPreprocess']
    features = preprocessor.final_field_names

    feature_importance = list(zip(features, importances))
    feature_importance_sorted = sorted(
        feature_importance, key=lambda x: x[1], reverse=True)

    print("\n=== 特徵重要性排序 ===")
    for feature, importance in feature_importance_sorted:
        print(f"{feature}: {importance:.4f}")

    # 回傳結果
    results = {
        'model': pipe,
        'feature_columns': feature_cols,
        'target_column': target_col,
        'train_metrics': train_metrics,
        'valid_metrics': valid_metrics,
        'feature_importance': feature_importance_sorted
    }

    return results


def hyperparameter_tuning(data_path=DEFAULT_TRAIN_DATA_PATH,
                          quick_mode=False,
                          feature_columns=None,
                          target_column=None,
                          default_target_column=TARGET_COLUMN,
                          test_size=TEST_SIZE,
                          random_state=RANDOM_STATE,
                          cv_folds=CV_FOLDS,
                          param_grid=None,
                          exclude_columns=None):
    """
    執行超參數調優

    參數:
        data_path (str): 訓練資料路徑
        quick_mode (bool): 快速模式，使用較少參數組合
        feature_columns (list): 特徵欄位列表，None表示自動推斷
        target_column (str): 目標欄位名稱，None表示使用預設
        default_target_column (str): 預設目標欄位名稱
        test_size (float): 測試集比例
        random_state (int): 隨機種子
        cv_folds (int): 交叉驗證折數
        param_grid (dict): 參數搜尋網格，None表示使用預設
        exclude_columns (list): 要排除的高相關度欄位列表，如 ['rating'] (相關度0.885)，None表示不排除任何欄位

    回傳:
        dict: 最佳參數和模型，如果被停止則回傳 None
    """
    print("開始超參數調優...")

    # 載入和驗證資料
    data, feature_cols, target_col = load_and_validate_data(
        data_path, feature_columns, target_column, default_target_column, exclude_columns)
    if data is None or feature_cols is None or target_col is None:
        return None

    # 檢查停止標誌
    if is_training_stopped():
        print("[停止機制] 超參數調優在資料載入後被停止")
        return None

    # 準備特徵和目標變數
    try:
        X = data[feature_cols]
        y = data[target_col]
        y = y.astype(int)
    except Exception as e:
        print(f"❌ 資料處理時發生錯誤: {e}")
        return None

    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y)

    model = LGBMClassifier(n_jobs=MODEL_N_JOBS,
                           random_state=random_state, verbose=MODEL_VERBOSE)
    pipe = Pipeline([('DataPreprocess', DataPreprocess()), ('model', model)])

    # 使用傳入的參數網格或預設網格
    if param_grid is None:
        param_grid = PARAM_GRID

    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True,
                         random_state=random_state)

    # 使用可停止的網格搜尋
    grid_search = StoppableGridSearchCV(
        estimator=pipe,
        param_grid=param_grid,
        scoring=SCORING_METRIC,
        cv=cv,
        verbose=2,  # 顯示詳細進度
        n_jobs=1    # 使用單執行緒確保停止機制正常運作
    )

    # 計算總組合數
    total_combinations = (len(param_grid['model__n_estimators']) *
                          len(param_grid['model__learning_rate']) *
                          len(param_grid['model__num_leaves']) *
                          len(param_grid['model__scale_pos_weight']) *
                          len(param_grid['model__reg_alpha']))
    total_fits = total_combinations * cv_folds

    print(f"\n=== 超參數調優配置 ===")
    print(f"參數組合數：{total_combinations} 個")
    print(f"交叉驗證：{cv_folds} fold")
    print(f"總計算次數：{total_fits} 次模型訓練")
    print(f"開始時間：{pd.Timestamp.now().strftime('%H:%M:%S')}")

    print(f"\n參數搜尋範圍：")
    for param, values in param_grid.items():
        print(f"  {param}: {values}")

    print(f"\n開始執行超參數搜尋...")
    print("=" * 50)

    # 檢查停止標誌
    if is_training_stopped():
        print("[停止機制] 超參數調優在網格搜尋前被停止")
        return None

    print("✅ 現在支援中途停止超參數搜尋!")
    result = grid_search.fit(X_train, y_train)

    # 檢查是否因停止而提前結束
    if result is None:
        print("[停止機制] 超參數調優被使用者停止，未完成任何參數組合")
        return None

    # 檢查停止標誌
    if is_training_stopped():
        print("[停止機制] 超參數調優在網格搜尋後被停止")
        # 如果有部分結果，仍然返回最佳結果
        if grid_search.best_params_ is not None:
            print(
                f"[停止機制] 返回部分搜尋結果 (完成 {grid_search.completed_combinations_}/{grid_search.total_combinations_} 個組合)")
        else:
            return None

    print("=" * 50)
    print(f"超參數搜尋完成時間：{pd.Timestamp.now().strftime('%H:%M:%S')}")
    print("=" * 50)

    # 確保有有效的結果
    if grid_search.best_params_ is None or grid_search.best_estimator_ is None:
        print("❌ 超參數搜尋未產生有效結果")
        return None

    print("最佳參數組合:", grid_search.best_params_)
    print("最佳 f1_macro 分數:", grid_search.best_score_)

    best_model = grid_search.best_estimator_

    # 檢查停止標誌，如果被停止則跳過驗證步驟
    if not is_training_stopped():
        y_pred = best_model.predict(X_valid)
        print("\n最佳模型在驗證組的表現:")
        print(classification_report(y_valid, y_pred))
    else:
        print("\n[停止機制] 跳過模型驗證步驟")

    return {
        'best_params': grid_search.best_params_,
        'best_score': grid_search.best_score_,
        'best_model': best_model,
        'feature_columns': feature_cols,
        'target_column': target_col
    }


def load_model_with_info(model_path, default_target_column=TARGET_COLUMN):
    """
    載入模型和欄位資訊

    參數:
        model_path (str): 模型檔案路徑
        default_target_column (str): 預設目標欄位名稱

    回傳:
        dict: 包含模型和欄位資訊的字典
    """
    try:
        with open(model_path, "rb") as f:
            model_info = pickle.load(f)

        # 兼容舊版本模型檔案（只有 pipeline）
        if hasattr(model_info, 'predict'):  # 這是舊版本的 pipeline 物件
            print("⚠️  載入的是舊版本模型，缺少欄位資訊，需要手動指定特徵欄位")
            return {
                'pipeline': model_info,
                'feature_columns': None,  # 需要手動指定
                'target_column': default_target_column
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


# 主程式執行區塊
if __name__ == "__main__":
    print("=== Sephora 產品推薦模型訓練 ===")

    # 選擇要執行的功能
    choice = input("請選擇功能 (1: 訓練模型, 2: 超參數調優, 3: 兩者都執行): ")

    if choice == "1":
        results = train_model()
        print("\n模型訓練完成!")

    elif choice == "2":
        tuning_results = hyperparameter_tuning()
        print("\n超參數調優完成!")

    elif choice == "3":
        # 先執行超參數調優
        tuning_results = hyperparameter_tuning()

        if tuning_results:
            print("\n現在用最佳參數訓練最終模型...")

            # 提取最佳參數
            best_params = tuning_results['best_params']

            # 用最佳參數訓練模型
            results = train_model(
                n_estimators=best_params.get(
                    'model__n_estimators', MODEL_N_ESTIMATORS),
                learning_rate=best_params.get(
                    'model__learning_rate', MODEL_LEARNING_RATE),
                num_leaves=best_params.get(
                    'model__num_leaves', MODEL_NUM_LEAVES),
                scale_pos_weight=best_params.get(
                    'model__scale_pos_weight', MODEL_SCALE_POS_WEIGHT)
            )

            print(f"\n🎯 使用的最佳參數:")
            for param, value in best_params.items():
                clean_param = param.replace('model__', '')
                print(f"  {clean_param}: {value}")

            print("\n所有訓練完成!")
        else:
            print("❌ 超參數調優失敗，無法繼續訓練")

    else:
        print("無效的選擇，請輸入 1, 2 或 3")
