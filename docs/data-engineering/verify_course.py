"""Offline author checks. Does not certify Airflow/Spark or learner competence."""
import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

from lab import seed, extract, match, validate, deliver, read

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", required=True, type=Path)
    root = parser.parse_args().workspace.resolve()
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError("Choose a new empty verification directory")
    passed = []
    def record(label):
        passed.append(label)
        print("PASS", label)

    course = Path(__file__).parent
    for path in course.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    record("python_syntax_only_not_airflow_or_spark_runtime")
    baseline = root / "baseline"
    seed(baseline)
    extract(baseline)
    result = match(baseline)
    assert result["roi_buyer"] == [["R001", "B001"], ["R002", "B002"], ["R004", "B004"], ["R006", "B006"], ["R007", "B007"]]
    assert result["member_candidates"] == [
        ["buyer", "B002", "M002"], ["buyer", "B003", "M003"],
        ["buyer", "B004", "M004"], ["buyer", "B004", "M005"],
        ["buyer", "B005", "M006"], ["buyer", "B007", "M007"],
        ["roi", "R001", "M001"], ["roi", "R002", "M002"],
        ["roi", "R003", "M003"], ["roi", "R004", "M004"],
        ["roi", "R004", "M005"], ["roi", "R005", "M006"], ["roi", "R007", "M007"],
    ]
    record("all_5_roi_buyer_and_13_member_edges_exact")
    assert validate(baseline)["matched"] == 9
    assert deliver(baseline) == {"inserted": 9, "total": 9}
    assert deliver(baseline) == {"inserted": 0, "total": 9}
    record("delivery_repeat_adds_zero")
    changed = baseline / "raw" / "roi.csv"
    changed.write_text(changed.read_text().replace("hash-a", "hash-new"), encoding="utf-8")
    assert match(baseline) == result
    extract(baseline)
    assert len(match(baseline)["roi_buyer"]) == 4
    record("snapshot_pins_input_until_explicit_extract")

    for scenario, mutation, marker in [
        ("schema", lambda s: s.replace("hkid_hash", "hkid", 1), "SCHEMA_ERROR"),
        ("duplicate_id", lambda s: s + s.splitlines()[1] + "\n", "ID_ERROR"),
    ]:
        work = root / scenario
        seed(work)
        path = work / "raw" / "roi.csv"
        path.write_text(mutation(path.read_text()), encoding="utf-8")
        completed = subprocess.run([sys.executable, str(course / "lab.py"), "extract", "--workspace", str(work)], capture_output=True, text=True)
        assert completed.returncode != 0 and marker in completed.stderr
        record(scenario + "_fails_with_nonzero_exit")

    work = root / "committed_timeout"
    first = subprocess.run([sys.executable, str(course / "lab.py"), "run", "--workspace", str(work), "--fail-after-commit"], capture_output=True, text=True)
    assert first.returncode != 0 and "SIMULATED_TIMEOUT" in first.stderr
    second = subprocess.run([sys.executable, str(course / "lab.py"), "deliver", "--workspace", str(work)], capture_output=True, text=True)
    assert second.returncode == 0 and json.loads(second.stdout) == {"inserted": 0, "total": 9}
    record("real_subprocess_failed_after_commit_then_recovered")

    summary = {"python": sys.version, "passed": passed,
               "not_executed": ["WSL installation", "Airflow service and UI", "PySpark JVM", "learner Spark solution"],
               "learner_status": "NOT_ASSESSED"}
    (root / "verification.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("EVIDENCE", root / "verification.json")

if __name__ == "__main__":
    main()
