# Repository boundary

This repository is the single home for the public learning website and its editable sources.

## Moved here

The English course, synthetic Python/SQL exercises, course SQL tests, website build and browser checks, curriculum/quizzes, and learning-site design documents now live together here. Generated root assets support GitHub Pages; authoring sources remain in their documented directories.

## Rewritten, not published verbatim

The optional case lab uses fourteen invented reference transformations, five optional Spark implementations and a manual Airflow example. They teach transformation shapes such as joins, deterministic deduplication, reshaping and safe file planning.

These are deliberately not the proprietary migration implementation, mappings, constants, schemas or business equivalence tests. The original private experimental implementation is preserved only in an ignored local archive and its original private Git history. Do not publish either.

## Data and operational boundaries

- Fixtures are fictional; contact examples use reserved example.invalid addresses.
- There is no production package import, database connection, API delivery or customer-file access.
- Python/SQL are the baseline. Choose Spark only after measuring a relevant bottleneck.
- Airflow coordinates repeatable tasks; it does not make Python transformations distributed.
- Logs, caches, archives, downloads and generated evidence stay in ignored .learning-runtime on D:.
- Source controls and tests are independent of any production checkout.
