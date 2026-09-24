# AI Handoff

## Current focus
- 2026-09-24: correct the earlier substitution of fictional cases for real business migrations.
- User explicitly authorized isolated D-drive Java/Spark/Airflow/Linux setup and publication of real business logic/field mappings; exclude credentials, internal configuration, customer records and real exception-record IDs.
- Production entry points and behavior must remain unchanged until complete comparison and a separate approved cutover.
- All learning work belongs here, not in the production repository.

## Actual code and scope
- src/club_migration: restored independent real stages for ROI, Buyer, Go Park, Townplace, Signature Home and the other previously implemented slices.
- contracts.py contains only twelve reviewed literal schema/rule declarations. No production package import.
- Loving Home requires special_import_ids through a private job manifest; do not restore actual record IDs into public code.
- dags/club_migration.py coordinates a selected real stage and artifact check, not a complete business workflow.
- docs/migration: real module/tool choices, statement walkthrough and exact validation limits.
- case_lab remains fictional introductory material, NOT migration or parity evidence.
- Original private archive remains ignored and untouched.

## Verified this turn
- D-drive portable Temurin Java 17.0.20.1 and isolated PySpark 4.0.1 environments installed; production Python unchanged.
- Strict script: scripts/run_migration_checks.ps1 -LegacyRoot <private-checkout> -LegacyPython <production-python.exe>.
- 19 tests passed, 0 errors/failures/skips: 13 actual Spark stage tests, 1 all-field differential test for selected real Buyer report/template and ROI questionnaire functions, 5 artifact-comparison checks.
- Golden reference subprocess uses original pandas 2.3.3; Spark environment pandas 2.2.3. Path overrides are removed from the reference subprocess.
- Evidence: .learning-runtime/migration-check-20260924-205348/evidence.json and tests.txt.
- Modules import without production dependencies; DAG syntax only, NOT Airflow execution.
- Native Windows worker failures retained in logs. Python 3.9 tests use opt-in scripts/spark_windows/sitecustomize.py to load installed unpacked PySpark, avoiding its zipped resource path failure.

## Blockers and incomplete work
- WSL and VirtualMachinePlatform enabled successfully, both exit 3010: Windows restart required. No automatic restart performed. No Linux distribution/Airflow installed yet.
- User confirmed real acceptance inputs and legacy outputs have NOT been copied in yet. Designated checkout: D:/projects/data-engineering-lab.
- Full raw-input adapters, complete final outputs, ROI-Buyer matching path, remaining workflow branches, dev/production comparisons and all other source coverage are NOT complete.
- No full workflow parity, Spark CLI output-write proof, real-data comparison or 500k benchmark claimed.
- Approximately 500,000 is member-master size, not per-job size. Explain tool fit first; do not force Spark.
- Keep environment downloads, caches, logs and intermediate data in ignored D-drive .learning-runtime; acceptance data in ignored validation-data.
- No production DB/API writes or source file moves/copies to business destinations.
- GitHub Projects linkage remains unverified: token lacks read:project.

## Next step
1. User restarts Windows manually, then verify WSL readiness and install a named D-backed Ubuntu learning distribution and isolated Airflow/Spark environment. Confirm supported versions from official docs.
2. Obtain exact anonymized input and expected-output filenames. Do not generate fictional records and label them real acceptance data.
3. Continue true legacy tracing and complete source-owned input/output adapters. Preserve all exempted matching/contact/address behavior and output contracts.
4. Execute real DAG tasks and full old-versus-new artifact comparisons; keep each workflow explicitly incomplete until all required branches and outputs are verified.
5. Keep English statement explanations beside the actual code; preserve failures and skips honestly.
