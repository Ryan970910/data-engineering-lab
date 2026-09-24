# Author validation — English curriculum revision

Date: 2026-09-21. These are author checks, not learner grades.

## Actually executed
Windows project Python 3.9.25, offline and synthetic only:

~~~powershell
& .\.venv\python.exe -m unittest discover -s tests -p test_course_sql.py -v
& .\.venv\python.exe docs/data-engineering/verify_course.py --workspace .learning-runtime/course-v2-python
~~~

Nine SQL tests passed: baseline counts, exact relations, changed hash, empty Buyer, null/multiple members, incorrect identity/duplicate/column rejection, write/attach/pragma rejection, CTE support and actual CLI snapshot/nonzero-failure behavior.

Seven pipeline checks passed: Python syntax; exact five ROI–Buyer and 13 member edges; repeated delivery adds zero; snapshot pinning; malformed schema and duplicate-ID subprocess failures; failure after commit followed by safe retry with nine total records.

Evidence: .learning-runtime/course-v2-python/verification.json. The unit test output is also present in the task execution record. Runtime data stays under D-drive .learning-runtime and is not published.

## Not executed or certified
- WSL installation or Linux package installation.
- Airflow service, scheduler, UI, real DAG import or retries.
- Spark JVM or learner build_pairs implementation.
- Learner independent work, oral explanation, unseen variants or graduation.
- Production integration, scaling, CRM delivery or business-rule changes.

AST parsing of Airflow/Spark files is syntax verification only. The Spark scaffold intentionally raises NotImplementedError until the learner implements it.

The course links official version-specific documentation. Documentation verification is not runtime verification. Website behavior is recorded separately in docs/learning/VALIDATION.md.
