# Validation scope

## Historical baseline

The prior course deployment was verified on 2026-09-21 at public commit 5d8b632439db91d24f62deaff9a4d9234f4005ef: twenty modules, sixty questions, nine SQL tests, seven offline author checks, and twenty-eight browser routes at desktop/mobile widths.

Those historical checks do not certify later edits.

## Repository separation

The lab now owns its authoring sources, fictional exercises, tests and site build. The two new fictional-case reference pages extend coverage to thirty routes. Runtime artifacts and raw verification logs stay under the ignored .learning-runtime directory in the standalone D-drive checkout.

Reproduce current checks using docs/learning/README.md. Browser evidence is written to course-v2-qa/verification.json and course-v2-qa-live/verification.json inside .learning-runtime. Inspect desktop/mobile screenshots as well as machine assertions.

## Executed after separation (2026-09-24)

- Independent Python suite: 27 discovered, 25 passed, 2 skipped (Spark/Airflow unavailable).
- Seven synthetic offline author checks passed, including real failing subprocess/recovery cases.
- Site build: 51 allowlisted artifacts, 27 content pages, 20 chapters and 60 questions.
- Real Chromium: all 30 routes at 1440px and 390px, all questions, persistence/import/export, clipboard, mobile menu, failure states and exact served artifact hashes passed.
- Desktop home and mobile SQL-lesson screenshots were visually inspected; no clipping observed in those reviewed views.

## Explicit limits

The new case rules are invented teaching contracts, not copied production behavior. No production parity, customer-data processing or performance benchmark is claimed. A member master of approximately 500,000 rows does not by itself justify Spark.

No WSL, Java, Spark or Airflow installation was resumed during repository separation. Missing optional runtimes produce explicit skipped tests. Syntax/import checks are narrower than a real successful DAG execution.

Browser self-checks do not certify learner mastery. No checkpoint is marked passed for the learner.
