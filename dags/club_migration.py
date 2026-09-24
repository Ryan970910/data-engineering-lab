"""Manual real-stage runner; no customer API or production database writes."""
from datetime import datetime, timezone
from airflow.sdk import Param, dag, task


@dag(schedule=None, start_date=datetime(2026, 1, 1, tzinfo=timezone.utc), catchup=False,
     max_active_runs=1, tags=["migration", "offline"],
     params={"job": Param("", type="string", description="Private job manifest path")})
def club_migration():
    @task(retries=0)
    def run_stage():
        import os
        import subprocess
        from pathlib import Path
        from airflow.sdk import get_current_context

        root = Path(os.environ["CLUB_MIGRATION_ROOT"]).resolve()
        python = Path(os.environ["CLUB_SPARK_PYTHON"])
        if not python.is_absolute() or not python.is_file():
            raise ValueError("CLUB_SPARK_PYTHON must be an existing isolated interpreter")
        scratch = root / ".learning-runtime" / "migration" / "tmp"
        scratch.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, PYTHONPATH=str(root / "src"), PYTHONDONTWRITEBYTECODE="1",
                   TEMP=str(scratch), TMP=str(scratch), TMPDIR=str(scratch))
        job = get_current_context()["params"]["job"]
        result = subprocess.run([str(python), "-m", "club_migration.runner", job],
                                cwd=root, env=env, check=True, text=True, capture_output=True)
        return result.stdout.strip().splitlines()[-1]

    @task(retries=0)
    def verify_artifact(evidence_path):
        import json
        from pathlib import Path

        evidence = json.loads(Path(evidence_path).read_text(encoding="utf-8"))
        if evidence["status"] != "artifact-written" or evidence["production_delivery"]:
            raise ValueError("Offline artifact contract failed")
        return {"status": evidence["status"], "parity_verified": evidence["parity_verified"]}

    verify_artifact(run_stage())


club_migration()
