# Sources, versions and verification boundaries

## How to use references
Read the course explanation first, perform the small experiment, then consult the official reference for exact API behavior. Documentation is a normal engineering tool, not evidence of failure. Avoid copying an entire solution without understanding its contract.

Installation targets were checked against official documentation during the September 2026 course revision. Pinning a teaching version improves reproducibility; it is not a promise that dependencies never change. If the installed version differs, report it and consult that version's documentation.

## Core learning references
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html): Python's SQLite interface and transaction behavior. Some APIs vary by Python version.
- [SQLite SELECT](https://www.sqlite.org/lang_select.html): joins, compound queries and SELECT semantics.
- [SQLite expressions](https://www.sqlite.org/lang_expr.html): NULL and expression behavior.
- [PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html): optional next step for shared relational systems.
- [DuckDB Parquet overview](https://duckdb.org/docs/stable/data/parquet/overview.html): optional local analytical exploration, not a core dependency.
- [Git book](https://git-scm.com/book/en/v2): reproducible code history and safe local workflows.

## Airflow and Linux
- [WSL basic commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands): inspect installation, distributions and location support.
- [Airflow 3.3.2 installation](https://airflow.apache.org/docs/apache-airflow/3.3.2/installation/installing-from-pypi.html): release/Python-specific constraints.
- [Airflow 3.3.2 TaskFlow](https://airflow.apache.org/docs/apache-airflow/3.3.2/tutorial/taskflow.html): Python task definitions and dependencies.
- [Airflow DAG runs](https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/dag-run.html): run and data-interval concepts.
- [Airflow best practices](https://airflow.apache.org/docs/apache-airflow/3.3.2/best-practices.html): lightweight definitions and task design.

The target is Ubuntu 24.04 / Python 3.12 / Airflow 3.3.2 in an isolated learning environment. The example uses the Airflow 3 SDK. Do not mix an Airflow 2 tutorial's imports with this code without an explicit migration.

## Spark
- [Spark 4.0.1 installation](https://spark.apache.org/docs/4.0.1/api/python/getting_started/install.html): Python/JVM requirements.
- [DataFrame quickstart](https://spark.apache.org/docs/4.0.1/api/python/getting_started/quickstart_df.html): schema, expressions and actions.
- [Cluster overview](https://spark.apache.org/docs/4.0.1/cluster-overview.html): driver/executor roles.
- [SQL performance tuning](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html): joins, partitions, caching and adaptive execution.

The teaching target is PySpark 4.0.1 with Java 17, in a separate Python 3.12 environment. Local[2] is a local learning configuration, not a two-machine cluster.

## Beyond the core path
Learn tools only after identifying a requirement:
- dbt can organize SQL transformations and tests when a SQL analytical platform is in scope.
- PostgreSQL can provide a shared transactional store; DuckDB can simplify local analytics.
- Kafka-like event platforms address ongoing event transport, not automatically correct stream processing.
- Container tooling can make runtime packaging more repeatable but does not remove storage, security or business-contract decisions.
- Cloud object storage, table formats and catalogs become relevant when shared durable analytical datasets are needed.

These are optional future directions, not required installations or claimed hands-on achievements in this course.

## What has and has not been validated
Website/browser checks test navigation, self-check feedback, notes, imports/exports and responsive rendering. Offline author checks test the supplied Python pipeline and SQL helper. These are distinct from:
- installing WSL on your machine;
- starting the Airflow scheduler/UI and executing tasks;
- starting a Spark JVM and running your implementation;
- independent learner assessment;
- production deployment, scale or private-system integration.

Airflow and Spark runtime validation must be recorded when actually performed. The learner Spark function deliberately remains incomplete. The static website cannot run Python, SQL, Airflow or Spark in your browser.

## Publication boundary
This public course contains original instructional material, fictional fixtures and safe practice scripts only. It does not publish production source code or private repository history. Project architecture is discussed as a case study; business behavior is not modified by the lessons.
