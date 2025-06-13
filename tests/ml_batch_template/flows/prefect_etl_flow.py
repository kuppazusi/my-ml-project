"""
Prefect flow: Extract + Transform + Load
-------------------------------------------------
* Reads source Excel/CSV
* Transforms data
* Inserts into SQL Server
* Pushes success metric to Prometheus Pushgateway
"""
import subprocess, sys, os, traceback
from datetime import datetime
from pathlib import Path

from prefect import task, flow, get_run_logger
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY = "http://localhost:9091"  # adjust if pushgateway hosted elsewhere

def push_status(job_name: str, status: int):
    registry = CollectorRegistry()
    g = Gauge('batch_job_status', '0=failed,1=success', ['job'], registry=registry)
    g.labels(job=job_name).set(status)
    push_to_gateway(PUSHGATEWAY, job=job_name, registry=registry)

@task
def extract():
    # Placeholder: copy or read raw files
    logger = get_run_logger()
    logger.info("Extract step - implement data gathering here.")

@task
def transform():
    logger = get_run_logger()
    logger.info("Transform step - implement cleaning/feature engineering here.")

@task
def load():
    logger = get_run_logger()
    logger.info("Load step - insert into SQL Server via pyodbc / sqlalchemy.")

@flow(name="weekly_etl_flow")
def run_flow():
    job_name = "prefect_etl"
    try:
        extract()
        transform()
        load()
        push_status(job_name, 1)
    except Exception as e:
        push_status(job_name, 0)
        raise

if __name__ == "__main__":
    run_flow()