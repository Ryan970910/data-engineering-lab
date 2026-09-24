# AI Handoff

## Current focus
- 2026-09-24: standalone public learning repository; production code remains private and separate.
- User selected public-safe sanitization, not publication of proprietary migration code.
- English instruction; learner writes Python independently and knows basic SQL.
- Explain tool fit before every case. A 500,000-row member master is not per-job volume.

## Source ownership
- docs/data-engineering: original twenty-module course and synthetic exercises.
- docs/learning: editable website sources, build and browser verification.
- case_lab: invented cases, optional Spark/Airflow examples and statement walkthroughs.
- tests: independent ordinary-Python checks and optional runtime checks.
- Root website artifacts are generated. Build into .learning-runtime/site-build.
- Do not copy or push private history, archives, production modules or customer records.

## Verification / limits
- See docs/learning/VALIDATION.md and ignored local verification evidence.
- Missing Spark/Airflow runtimes must stay visibly skipped, never called passed.
- The fictional exercises make no production-equivalence or performance claim.
- Browser quizzes do not certify hands-on learner mastery.

## Constraints
- Environment setup is PAUSED: no WSL/Java/Spark/Airflow installation or services without user approval.
- Runtime evidence, caches and the non-public original archive stay in ignored .learning-runtime on D:.
- Keep core.autocrlf=false for site artifact hashes.
- GitHub Projects linkage could not be verified with the current token; do not expand scopes silently.

## Next step
- Read README.md, case_lab/CASES.md and WALKTHROUGH.md.
- Ask the learner to justify a tool and predict an unseen case before running it.
- Assess submitted code, output and explanation, not completion clicks.
- Rebuild, run unit/author/browser checks and inspect screenshots before publication.
