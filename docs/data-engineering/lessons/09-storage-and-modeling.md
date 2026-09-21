# Choose storage and model the data

## Start with the question, not the product
An operational database usually serves small reads and writes with transactional guarantees. An analytical store usually serves scans and aggregations across history. These are workload descriptions, not absolute categories. Your project's member updates are operational; a monthly report on candidate ambiguity is analytical.

A data warehouse emphasizes managed analytical tables and SQL. A data lake keeps files or objects in flexible formats and requires deliberate metadata, quality and access control. A lakehouse adds table-management capabilities over file/object storage through specific technologies. A folder containing CSV files is not automatically a governed lakehouse.

For this small course, files and SQLite are enough to learn the boundaries. DuckDB can be an optional local analytical engine. PostgreSQL can be a later shared transactional store. Neither is required before understanding grain and contracts.

## Model history explicitly
Imagine a table matching_run with run_id, snapshot_hash, code_version, started_at and status. A candidate_edge table records run_id, source, record_id and member_id. A record_decision table records run_id, source, record_id, status and candidate_count.

The run_id in the key matters: R004 can have different candidates in different snapshots. A table keyed only by record_id would overwrite historical evidence or combine unrelated runs. A separate delivery_attempt table can record operation identity, attempt time and outcome without confusing an attempt with a delivered business operation.

Do not store real name/phone/hash in every analytical table just because they exist upstream. Stable pseudonymous identifiers and restricted lineage may be sufficient. A hashed identifier can still be sensitive and linkable.

## Normalization versus analytical modeling
Normalization separates facts to reduce inconsistent updates. A dimensional model organizes measurements around a declared fact grain and descriptive dimensions. A star schema is useful for recurring business questions, not compulsory for every pipeline.

For an educational quality dashboard, a fact table could have one row per run, source and decision status with record_count. Date and source can be dimensions. You must be able to explain why summing record_count is meaningful across those dimensions, and why counting candidate edges is a different metric.

A slowly changing dimension Type 1 overwrites a value; Type 2 preserves versions with validity intervals. Learn the trade-off before introducing it. The supplied baseline does not implement SCD handling.

## Files, columns and partitions
CSV is easy to inspect but needs explicit schema interpretation and has weak type metadata. JSON supports nested structures but is verbose. Parquet stores typed columns with compression and can let engines skip irrelevant columns and row groups. Parquet alone does not provide a multi-file transaction log or universal upsert semantics.

Partitioning groups data by a field such as business_date. It can reduce scans if queries filter that field. Partitioning by a near-unique phone creates many tiny directories/files and exposes sensitive keys. More partitions are not automatically better.

Small files increase listing, scheduling and metadata overhead. One giant file may limit parallelism. Choose layout using measured data size and access patterns, not a fixed “enterprise” number.

## Guided lab: design before building
Draw the three tables above. Underline the complete primary key for each. Write two SQL questions: “What fraction of source records was ambiguous in one run?” and “Which source identities changed status between two runs?”

Calculate the first metric from decisions, not from candidate edges. Explain the denominator and what happens when the source has zero records. Avoid converting an undefined ratio into a misleading perfect-quality score.

## Independent challenge
Create a separate SQLite analytics database in .learning-runtime/analytics. Load two synthetic runs into tables with run_id included in every relevant key. Write a join comparing status changes, and prove that reloading a run does not double its rows.

Keep this separate from mock_crm.sqlite, which represents a receiver's operational state. Document why a table used for delivery deduplication is not necessarily your reporting model.

As an optional extension after M14, write decisions to Parquet and read only source and status. Compare schema preservation and file size with JSON. For tiny data, do not claim the smaller file or faster single timing proves production superiority.

## Failure investigation
Your dashboard says there are 13 matched records because it counts rows in member_candidates. Rebuild it using record decisions. Then add a second run and explain why forgetting run_id doubles or mixes metrics.

<details><summary>Reasoning guide</summary>
Candidate edges describe possible links, not final eligible records. The baseline has 13 edges but nine matched records. Historical metrics require both the correct grain and the correct run scope. A database engine cannot infer the intended business denominator.
</details>

## Evidence to keep
Submit the table diagram, DDL, two-run queries, metric definitions and one rejected storage design with reasons. State which features you actually implemented and which remain design proposals.
