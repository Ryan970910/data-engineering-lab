# Choose the engine before rewriting a script

This standalone case lab uses invented rules and fictional records. It is not a
copy of a private business implementation and does not claim production parity.
The examples retain useful problem shapes: registrations, member reconciliation,
file handling, nested responses and reports. Names, schemas, eligibility rules,
identifiers and fixtures are public teaching contracts, not customer definitions.

Start with this assessment, then read [the statement walkthrough](WALKTHROUGH.md).
The full source, DAG and tests are in the course repository's `case_lab/` and
`tests/` folders. No second checkout or production Python package is required.

## The decision comes first

Airflow coordinates unattended work, dependencies and recovery. It does not make
a string parser faster. Spark executes distributed table transformations; it does
not make every workflow worth distributing. Python, pandas, SQL or an existing
scheduler may be the simpler correct tool.

A membership master of approximately 500,000 rows is a **planning scenario**, not
a per-task row count or performance benchmark. A form with twenty people may need
only a small indexed query. A duplicate-heavy full-table join may produce far more
rows than either input. Measure extraction, memory, joins, Python helper cost and
output separately. Do not claim a speedup before measuring equivalent results.

## Fourteen cases, fourteen explicit decisions

| Case / reference function | Business-shaped question | Simplest baseline and Airflow fit | Spark decision |
|---|---|---|---|
| Interest questionnaire / `interest_answers` | How do repeated choices become one stable answer list? | Python string processing. Airflow only if part of recurring ingestion. | No need for one form; optional at measured historical-batch scale. |
| Retained member / `retained_members` | Which row wins for a repeated name in this fictional contract? | SQL window or Python sort; Airflow can pin a recurring snapshot. | A useful window exercise; consider for genuinely large offline joins, not a tiny filtered query. |
| Event signup / `event_signup` | Does a row meet an invented age-plus-consent rule? | Python/pandas conditions; optional recurring validation gate. | Simple column expressions do not by themselves justify an engine change. |
| Residency signup / `residency_signup` | Which rows need missing-email review? | Python normalization; scheduler only for repeated feeds. | Keep Python unless batch cost is measured. |
| Lease signup / `lease_signup` | Is a date interval valid and how long is it? | Python dates or SQL. Airflow can manage input readiness. | Date arithmetic alone is not sufficient justification. |
| Form/member lookup / `form_candidates` | Which nonblank name/contact keys produce candidates? | Filtered SQL first. The tiny reference intentionally uses nested loops. | Stronger candidate if the actual join is large; preserve duplicates and key rules. |
| Move-in reconciliation / `missing_units` | Which expected units were not observed? | Sets/pandas or source-side anti join. Airflow can run exception reporting. | Optional anti-join comparison at portfolio scale. |
| File plan / `file_plan` | What destinations would be used without copying files? | Standard-library path handling; Airflow may coordinate a later approved copy. | Do not use Spark for filenames or two file copies. |
| Response export / `flatten_answers` | How does nested JSON become a table? | Python for modest responses; Airflow for recurring extraction. | Consider only for large landed data; no HTTP calls in executor functions. |
| Name overlap / `name_score` | How much of the right-hand syllable multiset is represented? | Python Counter. Coordinate only as part of a larger workflow. | Distribute the candidate join only if needed; a tiny scoring function is not a justification. |
| Monthly eligibility / `monthly_list` | Which rows fall in the previous calendar month? | SQL/pandas date filter. Recurrence makes Airflow relevant. | Filtering one modest file does not require Spark. |
| Handover grid / `handover_cells` | How does a unit grid become long-form rows? | Python/pandas reshape; no scheduler needed for one interactive workbook. | Optional unpivot lesson, not a production recommendation. |
| Writing entry / `writing_entries` | Does a delimited record match a declared schema? | Python split and validation. Airflow only if a feed depends on it. | Do not introduce a cluster for three fields. |
| Reference expansion / `expand_references` | How does one record expand to multiple references? | Python/SQL. Airflow may order downstream processing. | A useful explode lesson at measured scale; do not perform database updates inside it. |

These examples intentionally make different choices from any historical private
implementation: the questionnaire is lowercase whitespace tokens, the writing
entry has three fields, the report interval is a calendar month, references use
commas, and filenames are sorted. Never present these as legacy-compatible ports.

## Run without installing Spark or Airflow

From an existing Python environment at the lab repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:TEMP = "$PWD/.learning-runtime/tmp"
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force $env:TEMP | Out-Null
python -m case_lab.demo
python -m unittest discover -s tests -v
```

The first command runs fourteen real Python transformations and returns a private
local evidence path. It does not read a business workbook or contact a database.
`engine: python` must not be reported as Spark success. The tests skip Spark and
Airflow explicitly when absent; no installation is triggered.

Use an existing interpreter's full path if `python` is not on PATH. The examples
use the standard library. The optional Spark comparisons target Spark 4.0.1 and
the optional DAG targets Airflow 3; neither environment is installed by this lab.

## Learn by predicting, breaking and proving

For each case: predict the output; run it; explain each expression; modify one
fictional fixture; write a failing test; correct your implementation; record the
result and its limits. Fourteen correct supplied examples are not independent mastery.

1. Why is a blank email prohibited from matching another blank email?
2. What happens when two member rows have the same join date? Why add `id` as a tie-break?
3. Why can duplicate contact keys multiply candidate rows? Construct such a fixture.
4. Why does a blank handover cell still produce a row?
5. What changes if the report end becomes inclusive instead of exclusive?
6. Why is copying a file in a retried task different from constructing a plan?
7. Which of these cases should stay in Python at a small input size, and why?

After the runtime is available, compare Spark outputs against the tiny Python
reference on independent fixtures and several partition counts. A skipped test,
successful import or a displayed DAG is not proof that its tasks executed.

## Optional Airflow exercise

Put this repository on the worker's PYTHONPATH and configure the DAG folder to its
`case_lab/` directory in your separate learning environment. `fictional_cases` is
manual: `transform` writes a fictional artifact, then `inspect` checks its marker.
This first DAG intentionally executes Python, demonstrating that Airflow does not
require Spark. It has no real delivery step. Do not enable production credentials.

Keep runtime folders on D (or the corresponding mounted D path). The single-host
DAG assumes both tasks see the same filesystem; it is not a distributed deployment.

## Public boundary

This repository owns its lessons, site builder, tests and fictional cases. Public
history was not imported from another repository. Archived private experiments and
old local runtime evidence are excluded from Git and the site build. A public
course should demonstrate concepts without exposing private rules or customer data.
