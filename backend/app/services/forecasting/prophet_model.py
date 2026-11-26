from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.core.logging import logger

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("Prophet package is not installed. Falling back to seasonal exponential smoothing.")


class ProphetForecaster:
    """
    Forecasting model using Facebook Prophet for baseline interpretable
    time-series demand forecasting with holiday & seasonal decompositions.
    """

    def __init__(self, interval_width: float = 0.95):
        self.interval_width = interval_width
        self.model = None

    def fit_predict(
        self,
        historical_df: pd.DataFrame,
        horizon_days: int = 30,
        date_col: str = "sales_date",
        target_col: str = "quantity_sold"
    ) -> pd.DataFrame:
        """
        Fit model on historical sales and forecast forward by horizon_days.
        Returns DataFrame with columns: ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
        """
        if historical_df.empty or len(historical_df) < 5:
            raise ValueError("Insufficient historical data for forecasting (at least 5 data points required).")

        # Prepare prophet input format: 'ds' and 'y'
        df = historical_df[[date_col, target_col]].copy()
        df = df.rename(columns={date_col: "ds", target_col: "y"})
        df["ds"] = pd.to_datetime(df["ds"])
        df = df.sort_values(by="ds").reset_index(drop=True)

        if PROPHET_AVAILABLE:
            try:
                # Suppress cmdstanpy / prophet logs
                self.model = Prophet(
                    interval_width=self.interval_width,
                    weekly_seasonality=True,
                    yearly_seasonality=True if len(df) > 180 else False,
                    daily_seasonality=False,
                )
                
                # Add country holidays if series has sufficient history
                if len(df) > 90:
                    try:
                        self.model.add_country_holidays(country_name="US")
                    except Exception:
                        pass
                
                self.model.fit(df)
                
                # Create future dataframe
                future = self.model.make_future_dataframe(periods=horizon_days, freq="D")
                forecast = self.model.predict(future)
                
                # Clip negative forecasts to zero
                forecast["yhat"] = forecast["yhat"].clip(lower=0)
                forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
                forecast["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)
                
                # Extract results
                result_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
                result_df["ds"] = pd.to_datetime(result_df["ds"]).dt.strftime("%Y-%m-%d")
                return result_df

            except Exception as e:
                logger.warning(f"Prophet fitting encountered error: {e}. Utilizing fallback seasonal smoother.")

        # Fallback seasonal forecasting algorithm
        return self._fallback_forecast(df, horizon_days)

    def _fallback_forecast(self, df: pd.DataFrame, horizon_days: int) -> pd.DataFrame:
        """
        Robust statistical seasonal decomposition fallback (Day-of-week seasonality + EWMA trend)
        when Prophet binary dependencies are absent.
        """
        df["day_of_week"] = df["ds"].dt.dayofweek
        
        # Calculate day-of-week seasonal multiplier
        overall_mean = df["y"].mean() if df["y"].mean() > 0 else 1.0
        dow_means = df.groupby("day_of_week")["y"].mean()
        dow_multipliers = {dow: (mean / overall_mean) for dow, mean in dow_means.items()}
        
        # Calculate recent level / trend via exponential smoothing
        recent_level = df["y"].ewm(span=14).mean().iloc[-1]
        rolling_std = df["y"].rolling(14, min_periods=1).std().iloc[-1] or (overall_mean * 0.15)
        
        last_date = df["ds"].max()
        records = []
        
        # Add historical in-sample fitted values
        for _, row in df.iterrows():
            d = row["ds"]
            actual_y = row["y"]
            dow = d.dayofweek
            mult = dow_multipliers.get(dow, 1.0)
            fitted = max(0.0, float(recent_level * mult * 0.5 + actual_y * 0.5))
            records.append({
                "ds": d.strftime("%Y-%m-%d"),
                "yhat": round(fitted, 2),
                "yhat_lower": max(0.0, round(fitted - 1.96 * rolling_std, 2)),
                "yhat_upper": round(fitted + 1.96 * rolling_std, 2)
            })

        # Add forward forecast dates
        for i in range(1, horizon_days + 1):
            future_date = last_date + timedelta(days=i)
            dow = future_date.dayofweek
            mult = dow_multipliers.get(dow, 1.0)
            
            # Predict demand with slight random variation and day-of-week seasonality
            pred = max(0.0, float(recent_level * mult))
            lower = max(0.0, float(pred - 1.96 * rolling_std * (1 + i * 0.01)))
            upper = float(pred + 1.96 * rolling_std * (1 + i * 0.01))
            
            records.append({
                "ds": future_date.strftime("%Y-%m-%d"),
                "yhat": round(pred, 2),
                "yhat_lower": round(lower, 2),
                "yhat_upper": round(upper, 2)
            })
            
        return pd.DataFrame(records)
