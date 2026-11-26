from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.core.logging import logger
from app.services.forecasting.feature_engineering import TimeSeriesFeatureEngineer

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    from sklearn.ensemble import GradientBoostingRegressor
    logger.warning("LightGBM not installed. Utilizing sklearn GradientBoostingRegressor fallback.")


class LightGBMForecaster:
    """
    Advanced Gradient Boosted Trees demand forecaster leveraging engineered lag features,
    rolling statistics, calendar indicators, and quantile regression for confidence intervals.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.feature_engineer = TimeSeriesFeatureEngineer()
        self.model_point = None
        self.model_lower = None
        self.model_upper = None
        self.feature_cols: List[str] = []

    def fit_predict(
        self,
        historical_df: pd.DataFrame,
        horizon_days: int = 30,
        date_col: str = "sales_date",
        target_col: str = "quantity_sold"
    ) -> pd.DataFrame:
        if historical_df.empty or len(historical_df) < 15:
            raise ValueError("Insufficient historical data for LightGBM training (minimum 15 rows required).")

        # 1. Feature Engineering on historical data
        feat_df = self.feature_engineer.create_features(
            historical_df, date_col=date_col, target_col=target_col, is_training=True
        )
        self.feature_cols = self.feature_engineer.get_feature_column_names(
            feat_df, exclude_cols=[date_col, target_col, "id", "product_id"]
        )

        X = feat_df[self.feature_cols]
        y = feat_df[target_col]

        # 2. Train Models (Point forecast, 10th percentile, 90th percentile)
        if LIGHTGBM_AVAILABLE:
            # Point predictor
            self.model_point = lgb.LGBMRegressor(
                objective="regression",
                n_estimators=120,
                learning_rate=0.05,
                num_leaves=31,
                random_state=self.random_state,
                verbose=-1
            )
            self.model_point.fit(X, y)

            # Lower quantile (0.05)
            self.model_lower = lgb.LGBMRegressor(
                objective="quantile",
                alpha=0.05,
                n_estimators=100,
                learning_rate=0.05,
                random_state=self.random_state,
                verbose=-1
            )
            self.model_lower.fit(X, y)

            # Upper quantile (0.95)
            self.model_upper = lgb.LGBMRegressor(
                objective="quantile",
                alpha=0.95,
                n_estimators=100,
                learning_rate=0.05,
                random_state=self.random_state,
                verbose=-1
            )
            self.model_upper.fit(X, y)
        else:
            # Scikit-learn fallback
            self.model_point = GradientBoostingRegressor(
                loss="squared_error", n_estimators=100, learning_rate=0.05, random_state=self.random_state
            )
            self.model_point.fit(X, y)
            
            self.model_lower = GradientBoostingRegressor(
                loss="quantile", alpha=0.05, n_estimators=80, learning_rate=0.05, random_state=self.random_state
            )
            self.model_lower.fit(X, y)

            self.model_upper = GradientBoostingRegressor(
                loss="quantile", alpha=0.95, n_estimators=80, learning_rate=0.05, random_state=self.random_state
            )
            self.model_upper.fit(X, y)

        # 3. In-sample historical predictions
        feat_df["yhat"] = np.maximum(0, self.model_point.predict(X))
        feat_df["yhat_lower"] = np.maximum(0, self.model_lower.predict(X))
        feat_df["yhat_upper"] = np.maximum(feat_df["yhat"], self.model_upper.predict(X))

        history_records = []
        for _, row in feat_df.iterrows():
            d_str = pd.to_datetime(row[date_col]).strftime("%Y-%m-%d")
            history_records.append({
                "ds": d_str,
                "yhat": round(float(row["yhat"]), 2),
                "yhat_lower": round(float(row["yhat_lower"]), 2),
                "yhat_upper": round(float(row["yhat_upper"]), 2)
            })

        # 4. Multi-step recursive out-of-sample forward forecasting
        future_records = self._recursive_forward_predict(
            feat_df, horizon_days=horizon_days, date_col=date_col, target_col=target_col
        )

        all_records = history_records + future_records
        return pd.DataFrame(all_records)

    def _recursive_forward_predict(
        self,
        current_feat_df: pd.DataFrame,
        horizon_days: int,
        date_col: str,
        target_col: str
    ) -> List[Dict[str, Any]]:
        """
        Recursively predicts day by day, updating lags and rolling stats at each step.
        """
        records = []
        working_df = current_feat_df.copy()
        last_date = pd.to_datetime(working_df[date_col].max())

        for step in range(1, horizon_days + 1):
            next_date = last_date + timedelta(days=step)
            
            # Create a placeholder row
            new_row = {
                date_col: next_date,
                target_col: 0.0, # will be populated
                "is_promotion": 0,
                "unit_price": working_df["unit_price"].iloc[-1] if "unit_price" in working_df else 0.0
            }
            
            temp_df = pd.concat([working_df, pd.DataFrame([new_row])], ignore_index=True)
            re_feat = self.feature_engineer.create_features(temp_df, date_col=date_col, target_col=target_col, is_training=False)
            
            # Extract feature vector for the newest row
            latest_x = re_feat.iloc[[-1]][self.feature_cols]
            
            pred_y = float(np.maximum(0, self.model_point.predict(latest_x)[0]))
            pred_lower = float(np.maximum(0, self.model_lower.predict(latest_x)[0]))
            pred_upper = float(max(pred_y, self.model_upper.predict(latest_x)[0]))
            
            # Update target value for recursive lag feeding
            temp_df.loc[temp_df.index[-1], target_col] = pred_y
            working_df = temp_df
            
            records.append({
                "ds": next_date.strftime("%Y-%m-%d"),
                "yhat": round(pred_y, 2),
                "yhat_lower": round(pred_lower, 2),
                "yhat_upper": round(pred_upper, 2)
            })

        return records
