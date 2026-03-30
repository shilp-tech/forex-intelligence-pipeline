from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import subprocess
import os

# These are default settings that apply to every task in the DAG
# If a task fails, retry it once after waiting 5 minutes
default_args = {
    "owner":            "shilp",
    "depends_on_past":  False,
    "start_date":       datetime(2026, 3, 30),
    "retries":          1,
    "retry_delay":      timedelta(minutes=5),
}

# This creates the DAG object
# schedule="0 9 * * *" means "run at 9:00am every day"
# The format is: minute hour day month weekday
dag = DAG(
    "forex_pipeline",
    default_args=default_args,
    description="Daily Forex data pipeline",
    schedule="0 9 * * *",
    catchup=False,
)

# This is a helper function that runs a Python script
# We reuse this for every task instead of repeating code
def run_script(script_name):
    project_path = os.path.expanduser("~/forex-pipeline")
    python_path  = os.path.join(project_path, "venv/bin/python")
    script_path  = os.path.join(project_path, f"src/{script_name}")
    subprocess.run([python_path, script_path], check=True)

# TASK 1 — Fetch live Forex data from the API
task_fetch = PythonOperator(
    task_id="fetch_forex",
    python_callable=lambda: run_script("fetch_forex.py"),
    dag=dag,
)

# TASK 2 — Clean the raw data with Pandas
task_clean = PythonOperator(
    task_id="clean_forex",
    python_callable=lambda: run_script("clean_forex.py"),
    dag=dag,
)

# TASK 3 — Load clean data into AWS PostgreSQL database
task_load = PythonOperator(
    task_id="load_to_db",
    python_callable=lambda: run_script("load_to_db.py"),
    dag=dag,
)

# TASK 4 — Compute analytics and save back to database
task_analytics = PythonOperator(
    task_id="analytics",
    python_callable=lambda: run_script("analytics.py"),
    dag=dag,
)

# This defines the order of execution using >> operator
# >> means "then run" — so fetch first, then clean, then load, then analytics
task_fetch >> task_clean >> task_load >> task_analytics