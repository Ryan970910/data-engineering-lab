# Connect Airflow to a Spark job

## Keep ownership boundaries clear
Airflow owns scheduling and task state. Spark owns transformation. Storage owns durable artifacts. A validator owns acceptance. The receiver owns safe effects. Combining tools does not remove these boundaries.

Do not paste the entire matcher into a DAG definition. Package a runnable job with input/output arguments, then invoke it from a task. A CLI is a simple integration contract.

This is a new synthetic exercise, not a wrapper around production bulk-import. Production interactive inputs and external effects require separate design before scheduling.

## Define a job contract
Design .learning-runtime/spark_job.py with --snapshot, --output-dir and --run-id. It reads a manifest-bound synthetic snapshot, calls your matching transformation and writes outputs plus metadata.

Success includes exact schema, snapshot hash, code version, counts and zero exit. Failure includes nonzero exit and no published success marker. Never emit a marker before artifacts are validated.

A consumer discovering a folder during a write may read partial data. Locally, write into an attempt-specific staging directory, validate, then publish a manifest pointing to the complete immutable attempt. Filesystem rename atomicity and object-storage publication semantics differ; do not assume one universal protocol.

## Guided lab: separate environments
Airflow need not install PySpark just to launch a subprocess. In a task body, resolve Spark's interpreter explicitly:

~~~python
import os
import subprocess
from pathlib import Path

root = Path(os.environ["CLUB_LAB_ROOT"])
spark_python = root / "venv-spark" / "bin" / "python"
job = root / "spark_job.py"
subprocess.run(
    [str(spark_python), str(job),
     "--snapshot", snapshot_path,
     "--output-dir", output_dir,
     "--run-id", run_id],
    check=True,
)
~~~

This is a task fragment, not a standalone script: snapshot_path, output_dir and run_id come from your contract. Use it after the job works independently. Avoid shell=True and string concatenation.

Both processes must inherit Java and runtime settings. Log versions, not secrets. This assumes the Airflow host can execute Spark; a production cluster needs an appropriate submission interface and access controls.

## Independent challenge
Create a new learning DAG with extract, spark_transform, quality and mock_delivery. Reuse a run-scoped snapshot reference; do not reread changing raw files mid-run.

Write Spark edge artifacts. Implement an adapter to build the lab's decision/result contract, then validate exact output on the bounded fixture before mock delivery. Integration is not complete if the DAG still runs only the Python reference.

Prove that M15's function is invoked: record its version and inject an exception there. The transformation task must fail and delivery must not run. Restore it and rerun safely.

## Failure matrix
Test failure before Spark starts, during transformation, invalid schema, missing artifact, failure before publication and lost response after receiver commit. State which artifacts can remain and what is safe to retry.

A retry reuses the intended snapshot. Attempt ID may change while logical run/input identity stays fixed. Keep them distinct so retry does not silently become a new business operation.

## Failure investigation
The job catches an exception and exits zero. Airflow goes green; quality reads an earlier attempt's output. Identify incorrect error propagation and stale artifact selection. Fix both.

<details><summary>Reasoning guide</summary>
A manifest must identify the exact run/input/code/output combination. Existence is weaker than validity for this run. The orchestrator observes status, so failures must propagate. Validation must reject missing, stale or incompatible artifacts.
</details>

## Evidence to keep
Submit job, DAG, contract, direct CLI output, successful run and injected-failure run. Include attempts, hashes and receiver results. State single-host synthetic integration, not production-scale orchestration.
