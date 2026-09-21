# Operate your first Airflow DAG

## Read the definition before pressing Run
Open docs/data-engineering/dags/club_training.py. The @dag decorator defines a manual DAG named club_training. The @task functions define extract, transform, quality, mock_delivery and report. Passing returned values creates dependencies and transfers small workspace path strings through XCom.

The helper invokes lab.py with subprocess.run(..., check=True). A nonzero subprocess exit becomes a task failure. There are no production imports or CRM calls. Each run uses a directory derived from the Airflow run_id. Retrying a task within that run reuses its directory.

A new DAG run gets a new mock receiver database. Therefore two green DAG runs do not prove cross-run delivery deduplication. Preserve that limitation in your notes.

## Guided lab: start the local service
In Ubuntu Bash, from the public course checkout:

~~~bash
source docs/data-engineering/env.sh
source "$CLUB_LAB_ROOT/venv-airflow/bin/activate"
airflow version
airflow standalone
~~~

Keep this terminal open. Follow startup output for the local URL and authentication instructions; do not publish generated credentials. The course config sets the API host to loopback. Do not expose this development service to the internet. Stop it with Ctrl+C when finished.

In a second Ubuntu terminal, source the same environment and activate the same venv:

~~~bash
source docs/data-engineering/env.sh
source "$CLUB_LAB_ROOT/venv-airflow/bin/activate"
airflow dags list-import-errors
airflow dags list
airflow dags trigger club_training
~~~

If the DAG is paused in the UI, unpause it. Locate the triggered run and inspect the graph and each task log. Check that the report shows 9 matched, 2 ambiguous, 4 unmatched, 5 ROI–Buyer pairs and 13 member candidate edges on a fresh baseline.

Find the workspace path from the task output. Open quality.json and delivery.json there. UI green plus the correct artifact is stronger evidence than either alone.

## Why definition and execution differ
Import errors occur while Airflow discovers a DAG. Task failures happen during a run. A missing airflow.sdk import usually indicates an environment/version issue. A RESULT_MISMATCH in the quality task is a data/result issue. Clearing a task will not fix a broken import.

Airflow retries tasks according to policy. Retries do not automatically fix permanent schema errors or make an unsafe API idempotent. Inspect earlier attempts, not only the final successful one.

## Independent challenge: controlled failure
Create a learning copy of the DAG with a new dag_id and function name. Keep it in the course DAG folder. In its quality task, add a failure controlled by a marker file inside that run's workspace: on the first attempt create the marker and raise RuntimeError; on the retry perform normal validation.

Do not use a Python global counter: another process can execute the retry. Predict the task states and number of attempts before triggering. Capture the first failure, retry delay, eventual success and unchanged output contract.

For a second run, make quality fail permanently. Show that mock_delivery does not run. Explain upstream_failed versus failed. Restore the learning copy after the experiment so future runs are understandable.

## Scheduling and backfill extension
The provided DAG is manual. In a separate teaching DAG, choose a daily schedule and print the context's data_interval_start and data_interval_end. Use a fixed start date and explicitly choose catchup behavior. Before unpausing, predict how many historical intervals may be eligible.

Do not use current time as the extraction filter. Design a half-open interval query and test boundary records. Use the version's UI/CLI help for backfill controls and restrict the range to two synthetic intervals. Historical reruns require the same quality and idempotency guarantees as current runs.

## Failure investigation
Extract succeeds, but transform on another worker cannot find the returned path. What assumption did the demo make? How would object storage or a shared mounted filesystem change the artifact contract?

<details><summary>Reasoning guide</summary>
A path string is not the file. XCom transfers the reference, not the artifact contents. A single-host demo can share a local path; distributed workers need shared accessible storage, credentials and a publication protocol. Do not solve this by pushing the entire dataset into XCom.
</details>

## Evidence and sources
Submit DAG code, run ID, task attempts, import-error check, quality artifact and the blocked-delivery case. Explain the orchestration boundary without claiming production deployment.

Use the official [Airflow TaskFlow tutorial](https://airflow.apache.org/docs/apache-airflow/3.3.2/tutorial/taskflow.html) and [DAG runs reference](https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/dag-run.html). Check the installed version if menu labels differ.
