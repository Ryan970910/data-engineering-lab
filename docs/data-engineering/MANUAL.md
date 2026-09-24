# Data Engineering Lab: a practical learning guide

## Start with the problem, then choose the tool
This course is for a developer who can write Python independently and knows basic SQL, but is new to data engineering, Airflow and PySpark. It starts with why data pipelines exist, not with installing a scheduler.

The case study is a membership-data workflow involving ROI, Buyer and member records. You will learn to turn business rules into contracts, write relational transformations, test quality, recover from failures and explain when orchestration or distributed computation is justified. The exercises use fictional data only.

## How to study
For small executable examples with tool-fit decisions first, open [Fictional cases](CASES.md), then the [statement-by-statement walkthrough](WALKTHROUGH.md). These invented rules are independent learning exercises, not a production migration or a business-equivalence claim.

1. Read the concept and project example.
2. Predict the result before executing commands.
3. Complete the guided lab and inspect actual artifacts.
4. Implement the independent challenge.
5. Break a controlled case and explain the failure.
6. Submit code, commands, outputs and your explanation for assessment.

Use a phone for reading, notes and concept self-checks. Use a computer for Python, SQL, Airflow and Spark. The website does not execute those runtimes. It has no account or automatic cloud sync: export progress JSON before changing browsers/devices.

Start with M00. Since you can already write Python, M04 is an environment/reproducibility bridge, not a syntax course. Do not skip the SQL and matching-contract modules: they provide the reasoning needed for Spark.

## The learning path
| Stage | Modules | What you should be able to demonstrate |
| --- | --- | --- |
| Foundations | M00–M03 | Explain lifecycle, grain, keys, contracts and batch boundaries |
| Correctness | M04–M08 | Run an isolated pipeline, implement SQL/Python matching and test failures |
| Architecture | M09–M11 | Model history, explain safe retries and choose orchestration |
| Tools | M12–M16 | Operate Airflow and implement/measure PySpark transformations |
| Integration | M17–M19 | Integrate jobs, handle changes and defend an independent capstone |

Time labels are planning estimates, not deadlines. Expect several weeks of deliberate practice. Move forward when you can explain and reproduce the result, not merely when a page is marked read.

## Get the practice files
Keep the course separate from the production checkout. In Windows PowerShell:

~~~powershell
Set-Location D:\projects
git clone https://github.com/Ryan970910/data-engineering-lab.git
Set-Location D:\projects\data-engineering-lab
py --version
py -3 -m venv .venv
& .\.venv\Scripts\python.exe -c "import sys; print(sys.executable); print(sys.version)"
~~~

If the destination already exists, inspect it; do not overwrite your exercises. You can also download the repository ZIP and extract it into a new D-drive folder. Confirm docs/data-engineering/lab.py exists.

The early labs use Python 3.9+ standard-library modules only. A normal Windows venv uses .venv\Scripts\python.exe. Linux environments are created separately in M12. Do not reuse or upgrade the production project's environment.

Create .learning-runtime for notes/scripts/data that are not final portfolio deliverables. Keep temporary files, logs, caches and large outputs on D. Before publishing a portfolio, select only original code, synthetic fixtures and compact redacted evidence.

## Source chapters
The numbered Markdown files in lessons/ are the authoritative instructional chapters. The website renders them without maintaining a second copy of the lesson text.

- [M00: Data engineering](lessons/00-data-engineering.md)
- [M01: Project case study](lessons/01-project-case-study.md)
- [M02: Records and keys](lessons/02-records-schemas-and-keys.md)
- [M03: Ingestion](lessons/03-ingestion-and-batch-design.md)
- [M04: Reproducible Python](lessons/04-python-terminal-and-git.md)
- [M05: SQL](lessons/05-sql-from-first-principles.md)
- [M06: First pipeline](lessons/06-first-pipeline.md)
- [M07: Transformation contracts](lessons/07-transformation-contracts.md)
- [M08: Quality](lessons/08-quality-and-testing.md)
- [M09: Storage and modeling](lessons/09-storage-and-modeling.md)
- [M10: Reliability](lessons/10-reliability-and-recovery.md)
- [M11: Orchestration](lessons/11-orchestration-concepts.md)
- [M12: Linux environments](lessons/12-linux-and-tool-environments.md)
- [M13: Airflow](lessons/13-airflow-hands-on.md)
- [M14: Spark foundations](lessons/14-spark-foundations.md)
- [M15: Spark matching](lessons/15-spark-matching.md)
- [M16: Spark performance](lessons/16-spark-performance.md)
- [M17: Integration](lessons/17-integrate-orchestration-and-compute.md)
- [M18: Incremental operations](lessons/18-incremental-and-observable.md)
- [M19: Capstone](lessons/19-capstone-and-portfolio.md)

## What a checkpoint means
Reading marks and multiple-choice answers are self-tracking, not verified grades. For practical assessment, submit evidence to the coach in your conversation, answer follow-up questions and solve an unseen variation. The static website cannot examine your computer or certify authorship.

See [Assessment](ASSESSMENT.md), [Glossary](GLOSSARY.md), [Troubleshooting](TROUBLESHOOTING.md) and [References](REFERENCES.md). No learner checkpoint is automatically passed.

## Safety and scope
No production imports, customer data, credentials or external delivery calls belong in the learning labs. ROI–Buyer and member matching rules remain distinct. Blank-key exclusion and ambiguity quarantine are teaching conventions, not authorized changes to production behavior.

The author can validate website behavior and offline fixtures without having installed your Linux/Airflow/Spark environment. Runtime checks and your independent implementations must be reported separately. A successful course build proves neither your mastery nor production readiness.
