# Data Engineering Lab

An English, concept-first course for a Python developer with basic SQL. Twenty modules connect a fictional membership-data case study to SQL, reliable pipelines, Airflow, PySpark and an evidence-led capstone.

Study: https://ryan970910.github.io/data-engineering-lab/

Start with docs/data-engineering/MANUAL.md. Run exercises in an isolated D-drive checkout. All fixtures are fictional. No business source, private configuration, customer data or private repository history is published.

Browser reading/self-checks do not certify practical mastery. Submit code, outputs and explanations to a coach for an unseen-variant assessment. Airflow/Spark runtime must be verified in your learning environment; the Spark exercise is intentionally incomplete.

## This repository owns the complete lab

- `docs/data-engineering/`: English course chapters and Python/SQL exercises.
- `docs/learning/`: website sources, curriculum, quizzes, build and browser checks.
- `case_lab/`: fourteen invented Python cases, five optional Spark transformations, an optional Airflow DAG, and English tool-choice/statement walkthroughs.
- `tests/`: independent course and case checks. No production checkout is required.
- `DESIGN.md`, `PRODUCT.md`, `.impeccable/`: learning-site design context.

Start the case track at [tool choices](case_lab/CASES.md), then [code walkthrough](case_lab/WALKTHROUGH.md).

From this repository root:

```sh
python -m unittest discover -s tests -v
python -m case_lab.demo
python docs/data-engineering/verify_course.py --workspace .learning-runtime/fresh-author-check
node docs/learning/build.mjs
node docs/learning/verify.mjs
```

The author-check folder must be new. Website dependencies/setup are documented in [the authoring guide](docs/learning/README.md). No environment installation is performed by the Python demo.

Root HTML/CSS/JavaScript, course.json, manifest.json and two case-reference copies in docs/data-engineering are generated for GitHub Pages. Edit the sources, build to `.learning-runtime/site-build`, verify, then copy only manifest-listed artifacts to the root. Preserve authoring sources when publishing.

All runtime output, logs, caches and private local archives belong in ignored `.learning-runtime/` on D:. Never publish that directory, credentials, customer records or private repository history. Fictional cases do not prove production parity. Spark/Airflow tests are explicitly skipped when those runtimes are unavailable; a skip is not a pass.
