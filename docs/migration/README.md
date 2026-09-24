# Real project migration: implementation and evidence

This is the actual business-derived migration track, not the fictional `case_lab`.
[Read the English statement-by-statement walkthrough](WALKTHROUGH.md) beside the actual source.
Source lives in `src/club_migration/`; the Airflow DAG is `dags/club_migration.py`.
Neither imports the production package. The production UI and entry points remain unchanged.

## Choose the tool before moving a module

Airflow coordinates repeatable tasks, dependencies and evidence. Spark handles relational transformations only where measurements justify its overhead. A roughly 500,000-row member master is not the per-job volume. Benchmark equivalent outputs before recommending a production cutover.

| Module | Implemented real boundary | Why this engine / what remains |
| --- | --- | --- |
| roi | Field projection, property count, questionnaire rules | Spark expressions/UDF preserve existing semantics; full phone/name/address preparation, serial reservation and final V2 payload are still incomplete. |
| buyer | Retained/terminated joins, flags, dates, deterministic survivors, template columns | SQL or Spark can implement table operations; input extraction, workbook outputs and the separate ROI-Buyer matching path remain incomplete. |
| go_park | Title, age, consent and remarks on prepared rows | Cheap row rules normally favor Python; Spark is a comparison implementation, not a scale claim. |
| townplace | Age, STAR fields and remarks | Preserve its distinct under-age rule; shared input cleansing remains outside this stage. |
| signature_home | Age, STAR fields and remarks | Preserve its policy rather than merging it into Townplace behavior. |
| buyer_form | Name/contact membership lookup and conditional fill | Measure the full member extraction/join; small form batches may be better served by indexed SQL. |
| move_in | Normalized unit keys and null-safe anti-joins | Relational comparison fits SQL/Spark; remaining reports and workbook adapters are incomplete. |
| move_roi_files | Ordered file selection and rename plan | Ordinary Python; Spark offers no benefit. The plan does not copy files or insert database rows. |
| export_roi | Questionnaire response flattening | Spark is optional for large response batches; network retrieval belongs outside transformations. |
| the_point_check | Duplicate-aware name-segment score | Keep the legacy Python scoring rule in a UDF; name preparation and report joins remain incomplete. |
| the_point_list | Half-month window, membership flags and compatibility hash | Test time boundaries and exact hash behavior; workbook decryption and output remain separate. |
| handover | Cell-coordinate unpivot | Small workbooks favor Python; Spark stage does not yet replace workbook ingestion/output. |
| loving_home | Real DETAILS expansion and text replacements | Mostly string parsing, so Python remains the baseline. Actual record exception IDs must be supplied privately, never embedded in public source. |
| update_roi | Reference explosion, column names and null cleanup | SQL/Spark can express expansion; database mutation is not part of this offline stage. |

## What is and is not delivered

These are real but PARTIAL transformation stages. Restoring them does not finish all business workflows. There is no production cutover, automatic schedule, database write, API delivery or customer-file copy. The runner always distinguishes artifact creation from verified business equivalence.

The legacy behavior is the baseline, including the user-exempted matching/contact/address quirks. Do not silently fix business rules while migrating. Production and development paths both require complete comparison before acceptance.

## Run actual Spark checks

Use an isolated interpreter with the pinned Spark extra and Java 17+. Set JAVA_HOME, PYSPARK_PYTHON and PYTHONPATH to this checkout's src directory. Keep TEMP, SPARK_LOCAL_DIRS and all logs on D: (or the D-backed Linux filesystem).

```sh
python -m unittest discover -s tests/migration -v
python -m club_migration.runner .learning-runtime/migration/job.json
```

The job manifest and its explicitly typed JSONL inputs must be inside ignored `.learning-runtime/migration/`. Each input row needs an explicit, unique `_row_id`. `--check` validates the manifest only; it does not run Spark. For Loving Home, `special_import_ids` is a required private manifest field; supply the approved list, or an explicitly empty list for a case with no exceptions.

The DAG uses CLUB_MIGRATION_ROOT and CLUB_SPARK_PYTHON. A successful DAG import is not a successful DAG execution, and successful artifact creation is not a full business-result comparison.

On the prepared Windows machine, run `scripts/run_migration_checks.ps1 -LegacyRoot <private-checkout> -LegacyPython <private-python.exe>` in a fresh PowerShell process. It uses the isolated D-drive Python 3.9/Spark environment, applies an opt-in unpacked-package path workaround for the observed Windows zip-resource error, executes real Spark actions and the original legacy interpreter, and fails if any migration test is skipped. It writes a timestamped evidence.json and raw log under .learning-runtime. This does not execute Airflow.

`test_legacy_parity.py` compares all output columns and values from selected actual Buyer report/template and ROI questionnaire functions. It extracts only those pure functions from the private checkout; it never imports the production module or calls its database/API entry points. These synthetic-input differential tests still do not cover every business branch or whole workflows.

For complete supplied artifacts, run `python -m club_migration.validation <expected> <actual> --report .learning-runtime/comparison.json`. This checks values, types, order and structure, not just counts. It never labels an artifact match as whole-workflow certification. Reports omit customer cell values and remain ignored. CSV types remain text; XLSX formats/formulas are compared; Parquet schema and ordered rows are strict. Cross-format normalization is not silently applied.

## Acceptance gates

1. Complete all raw input adapters, business transformations and final output adapters for each workflow and environment.
2. Run actual Spark actions and Airflow tasks; skipped tests do not pass this gate.
3. Execute old and new paths on the same approved, anonymized input snapshots and pinned time/configuration.
4. Compare every output field, null, duplicate, matching relation, row order where contractual, and workbook/table structure.
5. Report each mismatch without silently weakening comparisons. No production-ready label until every required gate passes.

Keep approved real input/expected-output artifacts in ignored `validation-data/` or `.learning-runtime/`, not Git. The directory name alone is not a fixture; exact input and expected-output files still need to be supplied.
