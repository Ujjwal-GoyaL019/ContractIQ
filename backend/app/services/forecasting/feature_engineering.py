from typing import Tuple, List, Optional
import pandas as pd
import numpy as np


class TimeSeriesFeatureEngineer:
    """
    Constructs rich temporal, lagged, and rolling window features
    for gradient boosted tree forecasting (LightGBM) and regression baselines.
    """

    @staticmethod
    def create_features(
        df: pd.DataFrame,
        date_col: str = "sales_date",
        target_col: str = "quantity_sold",
        is_training: bool = True
    ) -> pd.DataFrame:
        df = df.copy()
        
        # Ensure proper datetime format and sorting
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(by=date_col).reset_index(drop=True)

        # 1. Calendar / Temporal features
        df["day_of_week"] = df[date_col].dt.dayofweek
        df["day_of_month"] = df[date_col].dt.day
        df["month"] = df[date_col].dt.month
        df["quarter"] = df[date_col].dt.quarter
        df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)
        df["day_of_year"] = df[date_col].dt.dayofyear
        
        # Cyclical transformations for seasonality
        df["sin_day_of_week"] = np.sin(2 * np.pi * df["day_of_week"] / 7.0)
        df["cos_day_of_week"] = np.cos(2 * np.pi * df["day_of_week"] / 7.0)
        df["sin_month"] = np.sin(2 * np.pi * df["month"] / 12.0)
        df["cos_month"] = np.cos(2 * np.pi * df["month"] / 12.0)

        # 2. Lag features (t-1, t-2, t-7, t-14, t-21, t-30)
        lags = [1, 2, 3, 7, 14, 21, 28, 30]
        for lag in lags:
            df[f"lag_{lag}"] = df[target_col].shift(lag)

        # 3. Rolling Window Statistics
        # Note: shift(1) avoids data leakage
        shifted_target = df[target_col].shift(1)
        
        for window in [7, 14, 30]:
            df[f"rolling_mean_{window}"] = shifted_target.rolling(window=window, min_periods=1).mean()
            df[f"rolling_std_{window}"] = shifted_target.rolling(window=window, min_periods=1).std().fillna(0)
            df[f"rolling_min_{window}"] = shifted_target.rolling(window=window, min_periods=1).min()
            df[f"rolling_max_{window}"] = shifted_target.rolling(window=window, min_periods=1).max()

        # Exponentially Weighted Moving Average (EWMA)
        df["ewma_7"] = shifted_target.ewm(span=7, min_periods=1).mean()
        df["ewma_14"] = shifted_target.ewm(span=14, min_periods=1).mean()

        # 4. Exogenous promotional & pricing features if present
        if "is_promotion" not in df.columns:
            df["is_promotion"] = 0
        else:
            df["is_promotion"] = df["is_promotion"].astype(int)

        if "unit_price" in df.columns:
            mean_price = df["unit_price"].mean()
            df["price_ratio"] = df["unit_price"] / (mean_price if mean_price > 0 else 1.0)
        else:
            df["price_ratio"] = 1.0

        # Fill any remaining NaNs from early lag shifts with backward/forward fill or zero
        feature_cols = [c for c in df.columns if c not in [date_col, target_col, "id", "product_id"]]
        df[feature_cols] = df[feature_cols].bfill().fillna(0)

        return df

    @staticmethod
    def get_feature_column_names(df: pd.DataFrame, exclude_cols: Optional[List[str]] = None) -> List[str]:
        if exclude_cols is None:
            exclude_cols = ["sales_date", "date", "ds", "quantity_sold", "y", "id", "product_id"]
        return [c for c in df.columns if c not in exclude_cols]
