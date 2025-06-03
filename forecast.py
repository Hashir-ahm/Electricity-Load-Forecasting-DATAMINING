# backend/forecast.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

def get_forecast(city, start_ts, end_ts, models):
    df = pd.read_csv('clustered_electricity_demand.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    sub = df[(df['city'] == city) & (df['datetime'] >= start_ts) & (df['datetime'] <= end_ts)]
    sub = sub.sort_values('datetime').dropna(subset=['demand'])
    if sub.empty:
        return {'dates': [], 'actual': [], 'predictions': {}}
    # Use weather features for regression
    features = ['temperature','humidity','windSpeed']
    X = sub[features].values
    y = sub['demand'].values
    # Train-test split (80/20)
    split = int(0.8 * len(y))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    dates_test = sub['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()[split:]
    result = {'dates': dates_test, 'actual': y_test.tolist(), 'predictions': {}}
    # Linear Regression
    if 'linear' in models:
        lr = LinearRegression().fit(X_train, y_train)
        y_pred_lr = lr.predict(X_test)
        result['predictions']['Linear Regression'] = np.round(y_pred_lr,2).tolist()
    # Random Forest
    if 'rf' in models:
        rf = RandomForestRegressor(n_estimators=50, random_state=0).fit(X_train, y_train)
        y_pred_rf = rf.predict(X_test)
        result['predictions']['Random Forest'] = np.round(y_pred_rf,2).tolist()
    return result