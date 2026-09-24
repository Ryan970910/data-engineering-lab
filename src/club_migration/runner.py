"""Run one offline stage; all outputs stay in the private D-backed scratch area."""

import argparse
import importlib
import json
from datetime import date
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / ".learning-runtime" / "migration"
STAGES = {
    "roi-fields": "roi", "buyer-report": "buyer", "go-park-rules": "go_park",
    "townplace-rules": "townplace", "signature-home-rules": "signature_home",
    "buyer-form-match": "buyer_form", "move-in-compare": "move_in",
    "move-roi-plan": "move_roi_files", "export-roi-questions": "export_roi",
    "the-point-score": "the_point_check", "the-point-list": "the_point_list",
    "handover-transform": "handover", "loving-home": "loving_home", "update-roi-explode": "update_roi",
}


def read_job(path):
    path = Path(path).resolve()
    if not path.is_relative_to(WORK.resolve()):
        raise ValueError("Job manifests must be inside the private .learning-runtime/migration directory")
    job = json.loads(path.read_text(encoding="utf-8"))
    if job["stage"] not in STAGES:
        raise ValueError("Unsupported migration stage")
    date.fromisoformat(job["run_date"])
    for spec in job.get("inputs", {}).values():
        source = (path.parent / spec["path"]).resolve()
        if not source.is_relative_to(WORK.resolve()) or not source.is_file():
            raise ValueError("Each input must be an existing private scratch file")
        spec["path"] = str(source)
        if not isinstance(spec["schema"], str) or not spec["schema"]:
            raise ValueError("Every Spark input needs an explicit DDL schema")
    return job


def execute(job):
    module = importlib.import_module(f"club_migration.{STAGES[job['stage']]}")
    run = WORK / "runs" / uuid4().hex
    run.mkdir(parents=True)
    stage = job["stage"]
    evidence = {"stage": stage, "run_date": job["run_date"], "production_delivery": False,
                "parity_verified": False, "outputs": {}, "status": "failed"}
    spark = None
    try:
        if stage == "move-roi-plan":
            plan = module.plan(job["records"], job["target_directory"], job["run_date"])
            (run / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
            evidence["outputs"]["plan"] = {"rows": len(plan), "path": str(run / "plan.json")}
        else:
            from pyspark.sql import SparkSession, functions as F

            spark = SparkSession.builder.master("local[2]").appName(f"migration-{stage}").config(
                "spark.sql.session.timeZone", "Asia/Hong_Kong").config(
                "spark.local.dir", str(run / "spark-temp")).config("spark.ui.enabled", "false").getOrCreate()
            frames = {}
            for name, spec in job["inputs"].items():
                frame = spark.read.schema(spec["schema"]).option("mode", "FAILFAST").json(spec["path"])
                if frame.filter(F.col("_row_id").isNull()).limit(1).count():
                    raise ValueError(f"{name}: _row_id must not be null")
                if frame.groupBy("_row_id").count().filter("count > 1").limit(1).count():
                    raise ValueError(f"{name}: _row_id must preserve unique source order")
                frames[name] = frame
            run_date = date.fromisoformat(job["run_date"])
            if stage == "buyer-report":
                report, template = module.transform(frames["members"], frames["errors"], job["template_columns"])
                outputs = {"retained": report, "template": template}
            elif stage == "buyer-form-match":
                outputs = {"result": module.transform(frames["members"], frames["forms"])}
            elif stage == "move-in-compare":
                left, right = module.compare_units(frames["collection"], frames["registered"])
                outputs = {"collection_only": left, "registered_only": right}
            elif stage in {"go-park-rules", "townplace-rules", "signature-home-rules"}:
                outputs = {"result": module.transform(frames["data"], run_date.year)}
            elif stage == "the-point-list":
                outputs = {"result": module.transform(frames["data"], run_date)}
            elif stage == "loving-home":
                outputs = {"result": module.transform(frames["data"], job["special_import_ids"])}
            else:
                outputs = {"result": module.transform(frames["data"])}
            for name, frame in outputs.items():
                path = run / name
                frame.write.mode("errorifexists").parquet(str(path))
                evidence["outputs"][name] = {"path": str(path), "rows": spark.read.parquet(str(path)).count()}
        evidence["status"] = "artifact-written"
    finally:
        (run / "evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        if spark is not None:
            spark.stop()
    return str(run / "evidence.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate paths/manifest only; does not execute Spark")
    args = parser.parse_args()
    job = read_job(args.job)
    print("Manifest/path check only; no transformation executed" if args.check else execute(job))


if __name__ == "__main__":
    main()
