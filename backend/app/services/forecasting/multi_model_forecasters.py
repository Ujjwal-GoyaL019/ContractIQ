from typing import List, Dict, Any
from datetime import timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

from app.services.forecasting.feature_engineering import TimeSeriesFeatureEngineer
from app.core.logging import logger

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("xgboost not installed. XGBoostForecaster will use sklearn fallback.")


class _BaseRecursiveTreeForecaster:
    """
    Shared recursive multi-step lag forecasting engine for tabular ML models
    (XGBoost, Random Forest, Ridge Regression).
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.feature_engineer = TimeSeriesFeatureEngineer()
        self.feature_cols: List[str] = []
        self.model = None
        self.residual_std: float = 1.0

    def _build_model(self):
        raise NotImplementedError

    def _predict_with_bounds(self, X: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        preds = np.maximum(0.0, self.model.predict(X))
        lower = np.maximum(0.0, preds - 1.645 * self.residual_std)
        upper = np.maximum(preds, preds + 1.645 * self.residual_std)
        return preds, lower, upper

    def fit_predict(
        self,
        historical_df: pd.DataFrame,
        horizon_days: int = 30,
        date_col: str = "sales_date",
        target_col: str = "quantity_sold",
    ) -> pd.DataFrame:
        if historical_df.empty or len(historical_df) < 15:
            raise ValueError("Insufficient historical data (minimum 15 rows required).")

        feat_df = self.feature_engineer.create_features(
            historical_df, date_col=date_col, target_col=target_col, is_training=True
        )
        self.feature_cols = self.feature_engineer.get_feature_column_names(
            feat_df, exclude_cols=[date_col, target_col, "id", "product_id"]
        )

        X = feat_df[self.feature_cols]
        y = feat_df[target_col].values.astype(float)

        self.model = self._build_model()
        self.model.fit(X, y)

        in_sample = np.maximum(0.0, self.model.predict(X))
        residuals = y - in_sample
        self.residual_std = float(np.std(residuals)) if len(residuals) > 1 else 1.0
        if self.residual_std < 0.5:
            # Avoid unrealistically tight in-sample residual collapse on tree models
            self.residual_std = max(0.5, float(np.std(y) * 0.25))

        yhat_in, lower_in, upper_in = self._predict_with_bounds(X)

        records: List[Dict[str, Any]] = []
        for idx, (_, row) in enumerate(feat_df.iterrows()):
            records.append({
                "ds": pd.to_datetime(row[date_col]).strftime("%Y-%m-%d"),
                "yhat": round(float(yhat_in[idx]), 2),
                "yhat_lower": round(float(lower_in[idx]), 2),
                "yhat_upper": round(float(upper_in[idx]), 2),
            })

        working_df = feat_df.copy()
        last_date = pd.to_datetime(working_df[date_col].max())

        for step in range(1, horizon_days + 1):
            next_date = last_date + timedelta(days=step)
            new_row = {
                date_col: next_date,
                target_col: 0.0,
                "is_promotion": 0,
                "unit_price": working_df["unit_price"].iloc[-1] if "unit_price" in working_df else 0.0,
            }
            temp_df = pd.concat([working_df, pd.DataFrame([new_row])], ignore_index=True)
            re_feat = self.feature_engineer.create_features(
                temp_df, date_col=date_col, target_col=target_col, is_training=False
            )
            latest_x = re_feat.iloc[[-1]][self.feature_cols]
            p_y, p_lo, p_hi = self._predict_with_bounds(latest_x)

            temp_df.loc[temp_df.index[-1], target_col] = float(p_y[0])
            working_df = temp_df

            records.append({
                "ds": next_date.strftime("%Y-%m-%d"),
                "yhat": round(float(p_y[0]), 2),
                "yhat_lower": round(float(p_lo[0]), 2),
                "yhat_upper": round(float(p_hi[0]), 2),
            })

        return pd.DataFrame(records)


class XGBoostForecaster(_BaseRecursiveTreeForecaster):
    """
    Depth-wise Regularized Gradient Boosted Trees forecaster powered by XGBoost.
    """

    def _build_model(self):
        if XGBOOST_AVAILABLE:
            return xgb.XGBRegressor(
                n_estimators=120,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                reg_alpha=0.1,
                reg_lambda=1.0,
                random_state=self.random_state,
                verbosity=0,
                n_jobs=1,
            )
        return RandomForestRegressor(n_estimators=80, max_depth=8, random_state=self.random_state, n_jobs=1)


class RandomForestForecaster(_BaseRecursiveTreeForecaster):
    """
    Bagged Decision Tree Ensemble forecaster using empirical per-tree quantiles (P10/P90)
    for non-parametric prediction intervals.
    """

    def _build_model(self):
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_leaf=3,
            random_state=self.random_state,
            n_jobs=1,
        )

    def _predict_with_bounds(self, X: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Compute per-tree distribution across all 100 estimators for empirical quantiles
        X_arr = X.values
        tree_preds = np.array([est.predict(X_arr) for est in self.model.estimators_])
        mean_pred = np.maximum(0.0, np.mean(tree_preds, axis=0))
        lower_q = np.maximum(0.0, np.percentile(tree_preds, 10, axis=0))
        upper_q = np.maximum(mean_pred, np.percentile(tree_preds, 90, axis=0) + 0.5 * self.residual_std)
        return mean_pred, lower_q, upper_q


class RidgeLagForecaster(_BaseRecursiveTreeForecaster):
    """
    L2-Regularized Linear Autoregressive forecaster over engineered lag & seasonal features.
    """

    def _build_model(self):
        return make_pipeline(StandardScaler(), Ridge(alpha=5.0))
