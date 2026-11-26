import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from app.services.forecasting.feature_engineering import TimeSeriesFeatureEngineer
from app.services.forecasting.prophet_model import ProphetForecaster
from app.services.forecasting.lightgbm_model import LightGBMForecaster
from app.services.forecasting.evaluator import ForecastEvaluator


def create_sample_sales_data(n_days=100):
    start = date(2025, 1, 1)
    dates = [start + timedelta(days=i) for i in range(n_days)]
    # Daily sales with 7-day cyclical pattern
    sales = [int(20 + 10 * np.sin(2 * np.pi * i / 7.0) + np.random.randint(0, 5)) for i in range(n_days)]
    return pd.DataFrame({
        "sales_date": dates,
        "quantity_sold": sales,
        "is_promotion": [1 if i % 15 == 0 else 0 for i in range(n_days)],
        "unit_price": [15.0] * n_days
    })


def test_feature_engineering():
    df = create_sample_sales_data(60)
    feat_df = TimeSeriesFeatureEngineer.create_features(df)
    
    assert "day_of_week" in feat_df.columns
    assert "lag_1" in feat_df.columns
    assert "lag_7" in feat_df.columns
    assert "rolling_mean_7" in feat_df.columns
    assert "rolling_std_7" in feat_df.columns
    assert len(feat_df) == len(df)
    assert not feat_df["rolling_mean_7"].isna().any()


def test_prophet_forecaster():
    df = create_sample_sales_data(90)
    forecaster = ProphetForecaster()
    pred_df = forecaster.fit_predict(df, horizon_days=14)
    
    assert len(pred_df) >= 14
    assert "ds" in pred_df.columns
    assert "yhat" in pred_df.columns
    assert "yhat_lower" in pred_df.columns
    assert "yhat_upper" in pred_df.columns
    # Check reasonable forecast values
    assert pred_df["yhat"].iloc[-1] >= 0
    assert (pred_df["yhat_upper"] >= pred_df["yhat_lower"]).all()


def test_lightgbm_forecaster():
    df = create_sample_sales_data(90)
    forecaster = LightGBMForecaster()
    pred_df = forecaster.fit_predict(df, horizon_days=14)
    
    assert len(pred_df) >= 14
    assert "ds" in pred_df.columns
    assert "yhat" in pred_df.columns
    assert "yhat_lower" in pred_df.columns
    assert "yhat_upper" in pred_df.columns
    assert pred_df["yhat"].iloc[-1] >= 0


def test_evaluator_metrics():
    y_true = np.array([20, 25, 30, 22, 28])
    y_pred = np.array([22, 24, 28, 20, 30])
    
    metrics = ForecastEvaluator.calculate_metrics(y_true, y_pred)
    assert "mape" in metrics
    assert "rmse" in metrics
    assert "mae" in metrics
    assert "wape" in metrics
    assert metrics["mae"] > 0
    assert metrics["rmse"] >= metrics["mae"]
