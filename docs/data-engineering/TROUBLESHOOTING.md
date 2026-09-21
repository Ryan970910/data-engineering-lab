# Troubleshoot by finding the failing boundary

## A repeatable method
Record the exact command, terminal type, working directory, interpreter, input identity, exit code and first relevant error. Separate environment problems from data-contract problems and orchestration problems.

Change one hypothesis at a time. Reproduce with the smallest synthetic case. Keep a working baseline and use a new workspace for destructive test fixtures. Do not “fix” a mismatch by deleting the assertion.

## Python and paths
**ModuleNotFoundError:** print sys.executable and run that interpreter's -m pip show package. An installed package in another venv does not help. The standard-library labs need no third-party package installation.

**Cannot find Python:** check py --version in Windows. A new Windows venv normally uses .venv\Scripts\python.exe; Ubuntu uses venv/bin/python. Do not guess the production environment's path.

**File not found:** inspect the current directory and complete path. A WSL /mnt/d path and a PowerShell D:\ path are representations in different operating environments.

**PowerShell activation blocked:** the early labs invoke the interpreter explicitly; activation is not required. Do not weaken machine-wide execution policy merely to run one exercise.

## Data and SQL
**SCHEMA_ERROR:** compare the exact CSV header, including order and accidental whitespace, against id,name,hkid_hash,phone,email. Document any evolution policy instead of accepting unknown inputs silently.

**ID_ERROR:** identify duplicate or missing IDs within the source. Do not drop one arbitrarily to make the test pass.

**SNAPSHOT_HASH_MISMATCH:** the manifest-bound content changed. Restore a trustworthy snapshot or intentionally extract a corrected batch; do not edit the hash to hide the discrepancy.

**RESULT_MISMATCH / ROW_MISMATCH:** compare exact tuples. Check grain, blank-key guards, name equality, deduplication columns and ambiguous candidates. Equal counts can hide different rows.

**COLUMN_MISMATCH:** alias SQL output exactly as the contract expects, in the declared order.

**SQL not authorized:** sql_lab.py allows read-only statements in an in-memory fixture. CREATE, UPDATE, DELETE, ATTACH and PRAGMA are not learner query operations. Use a separate explicitly designed analytics lab for DDL exercises.

**Raw edits have no effect:** match and SQL read the pinned snapshot. Run extract deliberately to create/select a new snapshot, then rerun the transformation.

## WSL and packages
**WSL missing / restart required:** follow Microsoft's current instructions and preserve D-drive placement. Do not unregister an existing distribution.

**--location unsupported:** check wsl --help and the installed WSL version. Do not silently install a large distribution onto C.

**Shell reports carriage-return errors:** save env.sh with LF line endings. Repository attributes specify LF for shell files.

**Airflow dependency conflict:** confirm Python 3.12 and matching 3.3.2 constraints. Save pip check output. Keep Spark in its separate venv.

## Airflow
**DAG absent:** check the activated environment, AIRFLOW__CORE__DAGS_FOLDER and airflow dags list-import-errors. Confirm the file is in the configured folder and has no import-time failures.

**Run remains queued:** inspect whether the DAG is paused and whether the standalone service/scheduler is running. Triggering and executing are distinct events.

**Downstream upstream_failed:** inspect the upstream task's failed attempts first. This state can correctly indicate delivery was prevented.

**Task green despite traceback:** ensure the subprocess exits nonzero and is invoked with check=True. Printed error text is not a failure signal.

**File visible in one task only:** the demo assumes shared single-host storage. A returned path is not transferred file content.

**New run inserted nine again:** each demo run has a different receiver database. That is not the same as retrying delivery against one receiver.

## Spark
**NotImplementedError from build_pairs:** implement M15's learner function. It is intentionally not solved for you.

**JAVA_GATEWAY_EXITED:** inspect Java version/JAVA_HOME and startup stderr. Confirm the active Spark venv and loopback settings. Do not start by changing matching logic.

**Cannot infer schema:** use an explicit schema for empty or all-null fixtures.

**Ambiguous reference:** qualify joined columns using DataFrame aliases and select output fields intentionally.

**Driver memory exhaustion:** investigate collect, toPandas or a large Python-side input list. Use bounded samples and distributed writes/aggregation.

**Unexpected duplicate rows:** inspect join cardinality and identity grain before trying more executor memory.

**Slow tiny job:** account for JVM startup and scheduling. Measure equal actions repeatedly; Python/SQL may be the appropriate tool.

## Website and learning records
**Course does not load:** use the hosted URL or an HTTP server, not a file:// HTML tab. Refresh and inspect network availability.

**Progress disappeared:** records are browser-local. Import a previous exported JSON backup. There is no server account from which to recover deleted browser storage.

**Old course notes:** version-1 notes remain in their old local-storage key. The notebook offers a raw backup; they are not converted into passes for the revised curriculum.

**All self-checks correct but practical assessment pending:** that is expected. Submit implementation evidence and solve an unseen variant with the coach.

## Ask for help with useful evidence
Send the module, command, environment, compact output and what you expected. Redact private data and secrets. Say what you have actually run versus what you inferred. This lets the coach diagnose the boundary instead of guessing from a cropped error screenshot.
