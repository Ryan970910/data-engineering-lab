# Understand orchestration before Airflow

## Computation and coordination are different jobs
Your matcher calculates relationships. An orchestrator decides when to invoke stages, which dependencies must succeed, how to record state and when to retry. It should not contain a second copy of every source's processing logic.

This mirrors the desired production architecture: bulk-import coordinates source-specific modules; ROI logic belongs to ROI, Buyer logic to Buyer. Airflow adds durable orchestration capabilities, not permission to duplicate or change those business rules.

A simple Python entry point is often enough for a small manual workflow. A cron-like timer can start a command on a schedule. Airflow becomes useful when dependencies, repeated schedules, task-level recovery and operational visibility justify its installation and maintenance.

## DAGs and task instances
A directed acyclic graph is a graph whose arrows have direction and no cycle. An edge extract → match means match depends on extract. It does not mean rows flow through the scheduler's memory.

A DAG definition is a reusable plan. A DAG run is one execution of that plan. A task instance is one task in one run. A retry is another attempt of that task instance, not automatically a completely new pipeline with new input.

For the course, extract → match → validate → deliver → report is intentionally linear. Independent sources could be extracted in parallel, followed by a join stage, but parallelism is safe only when dependencies and resource limits are correct.

## Pass references, not datasets
A task can write a snapshot and pass its path or object URI to the next task. Airflow XCom is appropriate for small coordination values, not millions of records. A returned local path works only if the next task can access the same filesystem.

Our sample assumes one host with shared local storage. A multi-worker deployment needs shared storage and consistent permissions. Moving the same code to distributed workers without changing the artifact contract can cause “file not found” even when the first task succeeded.

## Time has several meanings
Wall-clock execution time tells you when a task ran. Event time tells you when a business event occurred. A data interval tells a scheduled pipeline which range of data it is responsible for. Late execution does not necessarily mean it should process “today.”

If an hourly run is retried tomorrow, reading datetime.now() to choose the source window can silently process the wrong interval. Bind the input selection to the run's intended interval or explicit parameters. Store timezone-aware boundaries and decide whether ranges are half-open, such as [start, end), to avoid boundary double counting.

The supplied DAG is manual, with schedule=None and catchup=False. It does not demonstrate a scheduled backfill just because Airflow supports one.

## Guided lab: design on paper
Draw the five stages with each input/output artifact and failure policy. Mark which stage may produce external effects. Suppose validate fails: should report run as a success report? Should delivery proceed? Explain the default dependency behavior and distinguish an always-run diagnostic report from a success-only report.

Create a state table for success, failed and upstream_failed. A downstream task prevented from running is not the same as a task that ran and raised an exception.

## Independent challenge
Write a one-page architecture decision record comparing:
1. One Python command invoked manually.
2. A scheduled operating-system command.
3. Airflow tasks with artifact boundaries.

Use concrete criteria: frequency, number of dependencies, operator needs, recovery granularity, deployment effort and secrets management. Recommend one for the tiny lab and one for a hypothetical daily multi-source operation. It is acceptable to conclude that Airflow is unnecessary for a small manual job.

## Failure investigation
A developer places database reads and API calls at the top level of a DAG module. Explain why repeated DAG parsing can unexpectedly repeat work, slow scheduler processing or expose failures before a run exists.

<details><summary>Reasoning guide</summary>
The scheduler parses DAG definitions to discover structure. Put execution-time I/O inside tasks, and keep the definition lightweight. A top-level import must not itself launch the business workflow. This is an architectural boundary, not merely an Airflow coding style preference.
</details>

## Evidence to keep
Submit the DAG sketch, task-state explanation, time-window example and decision record. Before installing Airflow, explain what it will coordinate and what it will not compute for you.
