import argparse, datetime
import mlflow
import pandas as pd
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY = "http://localhost:9091"
JOB_NAME = "ml_predict"

def push_status(status: int):
    registry = CollectorRegistry()
    g = Gauge('batch_job_status', '0=failed,1=success', ['job'], registry=registry)
    g.labels(job=JOB_NAME).set(status)
    push_to_gateway(PUSHGATEWAY, job=JOB_NAME, registry=registry)

def main(predict_date: str):
    try:
        client = mlflow.tracking.MlflowClient()
        latest_runs = client.search_runs(experiment_ids=['0'], order_by=["start_time DESC"], max_results=1)
        if not latest_runs:
            print("No model found")
            push_status(0)
            return
        run_id = latest_runs[0].info.run_id
        model_uri = f"runs:/{run_id}/model"
        model = mlflow.pyfunc.load_model(model_uri)

        # placeholder: load data for prediction
        import numpy as np
        X_pred = np.random.rand(10, 13)  # dummy features
        preds = model.predict(X_pred)
        # insert preds into SQL Server...
        push_status(1)
    except Exception as e:
        push_status(0)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--predict_date", type=str, default="auto")
    args = parser.parse_args()
    main(args.predict_date)