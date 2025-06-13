import argparse, os, traceback
import mlflow
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY = "http://localhost:9091"
JOB_NAME = "ml_train"

def push_status(status: int):
    registry = CollectorRegistry()
    g = Gauge('batch_job_status', '0=failed,1=success', ['job'], registry=registry)
    g.labels(job=JOB_NAME).set(status)
    push_to_gateway(PUSHGATEWAY, job=JOB_NAME, registry=registry)

def main(n_estimators):
    try:
        # placeholder: load processed data from SQL Server
        # df = pd.read_sql(...)
        # dummy data
        from sklearn.datasets import load_boston
        X, y = load_boston(return_X_y=True)
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        mlflow.lightgbm.autolog()
        with mlflow.start_run():
            model = lgb.LGBMRegressor(n_estimators=n_estimators)
            model.fit(X_train, y_train)
            score = model.score(X_val, y_val)
            mlflow.log_metric('val_score', score)
        push_status(1)
    except Exception as e:
        push_status(0)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_estimators", type=int, default=200)
    args = parser.parse_args()
    main(args.n_estimators)