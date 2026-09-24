# Actual validation evidence: 2026-09-24

## Executed

The isolated D-drive environment uses Python 3.9.25, PySpark 4.0.1 and Temurin Java 17.0.20.1. It does not install packages into production Python.

Command: `scripts/run_migration_checks.ps1 -LegacyRoot <private-checkout> -LegacyPython <private-python.exe>`.

Result: **19 tests, 0 failures, 0 errors, 0 skipped**, in 57.887 seconds:

- Thirteen tests execute real Spark actions over the restored business-derived stages.
- One differential test compares every report/template/questionnaire field and row with selected actual legacy functions on synthetic boundary inputs. The reference runs in the original Python interpreter with pandas 2.3.3, independent of the new environment's pandas 2.2.3.
- Five strict artifact-comparison tests cover equal files, changed values at the same row count, null/type/order/duplicate/field differences, self-comparison rejection and XLSX cells.

Local evidence: `.learning-runtime/migration-check-20260924-205348/evidence.json` and `tests.txt`. They explicitly record `airflow_executed: false` and `full_business_workflows_verified: false`.

All real migration modules also imported without production-package dependencies or installed Spark in a separate interpreter. The DAG was syntax-parsed only, not executed.

## Failed attempts retained, not hidden

- First Python 3.12 Spark attempt: all thirteen tests errored because Python workers crashed. A successful JVM count alone was not accepted.
- Python 3.9 isolated the concrete worker import error: the zipped PySpark resource lookup constructed a backslash-containing path to error-conditions.json.
- The successful Windows test runner loads the already-installed unpacked PySpark package via an opt-in path bootstrap. It does not mock Spark or rewrite its execution engine.
- The original reference-test environment initially inherited the Spark bootstrap. This was corrected by removing those path overrides from the reference subprocess, and the full strict suite was rerun with verified legacy pandas 2.3.3.

## Not yet verified

- Full raw-input-to-final-output workflows, all business branches, complete development/production parity and approved real-data equivalence.
- Airflow installation, DAG import and actual task execution. Windows WSL and VirtualMachinePlatform were enabled with exit 3010 (restart required); no automatic restart occurred.
- The user confirmed that real input and legacy expected-output files have NOT yet been copied into the designated directory.
- End-to-end Spark CLI artifact writes, full workbook adapters, production database/API delivery and a 500,000-member benchmark.

Passing selected stage tests is not full business acceptance. Production entry points and business source remain unchanged. No customer data, credentials, internal runtime configuration or real exception-record IDs were added to the public source.
