"""Airflow 3 single-host demonstration, synthetic data only."""
import os
from datetime import timedelta
from pathlib import Path
import pendulum
from airflow.sdk import dag, task, get_current_context

@dag(
    dag_id="club_training",
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Hong_Kong"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(seconds=15)},
    tags=["training", "synthetic"],
)
def club_training():
    def execute(stage, workspace):
        import subprocess
        import sys
        script = Path(os.environ["CLUB_COURSE"]) / "lab.py"
        subprocess.run([sys.executable, str(script), stage, "--workspace", workspace], check=True)

    @task
    def extract():
        import hashlib
        context = get_current_context()
        run_key = hashlib.sha256(context["run_id"].encode()).hexdigest()[:24]
        root = str(Path(os.environ["CLUB_LAB_ROOT"]) / "airflow-runs" / run_key)
        execute("seed", root)
        execute("extract", root)
        return root

    @task
    def transform(root):
        execute("match", root)
        return root

    @task
    def quality(root):
        execute("validate", root)
        return root

    @task
    def mock_delivery(root):
        execute("deliver", root)
        return root

    @task
    def report(root):
        import json
        summary = json.loads((Path(root) / "quality.json").read_text())
        print({"workspace": root, "quality": summary})

    report(mock_delivery(quality(transform(extract()))))

club_training()
