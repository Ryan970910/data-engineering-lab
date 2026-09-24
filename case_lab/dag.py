"""Optional manual Airflow demonstration for the independent fictional lab."""

from datetime import datetime, timezone
from airflow.sdk import dag, task


@dag(schedule=None, start_date=datetime(2026, 1, 1, tzinfo=timezone.utc), catchup=False,
     max_active_runs=1, tags=["synthetic", "learning"])
def fictional_cases():
    @task(retries=0)
    def transform():
        from case_lab.demo import run
        return run()

    @task(retries=0)
    def inspect(path):
        import json
        from pathlib import Path
        evidence = json.loads(Path(path).read_text(encoding="utf-8"))
        if not evidence["synthetic_only"] or evidence["production_parity"]:
            raise ValueError("Not a synthetic teaching artifact")
        return {"case_count": len(evidence["outputs"]), "engine": evidence["engine"]}

    inspect(transform())


fictional_cases()
