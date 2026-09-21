# Use SQL to describe relationships

## Why learn SQL before a distributed engine?

SQL expresses a question about relations: choose columns, restrict rows, combine compatible records and summarize groups. A database engine chooses an execution strategy. Understanding this declarative model makes Spark joins and analytical modeling easier later.

You know basic queries; this module extends that foundation into join cardinality, missing values, CTEs and exact-result testing. You will use Python's built-in SQLite, not a remote database. The supplied sql_lab.py loads only the synthetic snapshot into an in-memory database. Learner queries are restricted to reading.

Available tables are source_records(source, record_id, name, hkid_hash, phone, email) and members(member_id, name, hkid_hash, phone, email). Blank values become SQL NULL. There are 15 source records and eight members in the baseline.

## Read one query precisely

~~~sql
SELECT source, COUNT(*) AS record_count
FROM source_records
GROUP BY source
ORDER BY source;
~~~

FROM identifies the relation. GROUP BY forms one group per source value. COUNT(*) counts rows, including rows with NULL fields. AS names the result column. ORDER BY makes presentation deterministic; without it, SQL does not promise your preferred row order.

Run this query, which is the runner's default, in PowerShell:

~~~powershell
$work = "D:/projects/data-engineering-lab/.learning-runtime/sql"
& .\.venv\Scripts\python.exe docs/data-engineering/sql_lab.py --workspace $work
~~~

Expect buyer with 7 and roi with 8. The lab creates a baseline snapshot only when the workspace has no manifest; later queries use that pinned snapshot. Use a new workspace for an independent baseline.

WHERE filters rows before aggregation. HAVING filters aggregate groups afterward. COUNT(phone) counts non-NULL phones, while COUNT(*) counts rows. Neither automatically counts unique people.

## Joins are predicates, not magic lookups

~~~sql
SELECT r.record_id AS roi_id, b.record_id AS buyer_id
FROM source_records AS r
JOIN source_records AS b
  ON r.name = b.name AND r.hkid_hash = b.hkid_hash
WHERE r.source = 'roi'
  AND b.source = 'buyer'
  AND r.hkid_hash IS NOT NULL
ORDER BY roi_id, buyer_id;
~~~

The same relation appears twice with aliases r and b. JOIN tests the predicate for compatible pairs. The baseline returns five edges: R001–B001, R002–B002, R004–B004, R006–B006 and R007–B007.

An inner join returns matching pairs. A left join preserves every left row and fills unmatched right fields with NULL. A condition on the right table in WHERE can accidentally remove those unmatched rows and defeat that preservation.

NULL is not tested with = NULL. Use IS NULL. Do not replace a missing contact with a common placeholder just to make a join easier.

## Guided lab: execute and check a query

Save the join above in .learning-runtime/roi_buyer.sql using your editor. Run:

~~~powershell
& .\.venv\Scripts\python.exe docs/data-engineering/sql_lab.py --workspace $work --query-file .learning-runtime/roi_buyer.sql --expect roi-buyer
~~~

The checker compares exact identity rows and column names, not only the number of rows.

Now change only one Buyer hash in a copied workspace's raw CSV, extract that workspace again, predict which edge disappears and rerun. The expected checker follows the snapshot rather than hardcoding a five-row answer.

## UNION, CTEs and deduplication

For member matching, build a phone branch and an email branch. Each must require name equality and a non-missing contact. UNION removes identical projected rows; UNION ALL retains them. If you add a match_reason column, two reasons become different rows even when the identity edge is the same. Decide the output grain before choosing deduplication columns.

A common table expression, introduced with WITH, names an intermediate query. It helps you reason in stages; it does not automatically promise persistent storage or faster execution.

After building unique candidates, group by source and record_id and count distinct member_id. Join those counts back to every source record so zero-candidate rows are not lost. A CASE expression can label 0 as unmatched, 1 as matched and larger values as ambiguous.

## Independent challenge

Write .learning-runtime/member_candidates.sql returning exactly source, record_id, member_id for the authorized member rule. Run with --expect member-candidates. The baseline has 13 unique edges, not 13 unique matched source records.

Write a second query that preserves all 15 source records and assigns a candidate count. Explain why a left join is needed. Do not call the Python reference matcher as your SQL implementation.

For an extension, use ROW_NUMBER() OVER (PARTITION BY source, record_id ORDER BY ingested_at DESC, version_id DESC) on your own versioned fixture to select the latest version. Explain why the final tie-breaker must be deterministic and why this rule is not appropriate for arbitrarily choosing a member candidate.

## Failure investigation

Both phone and email match GIA to M007, but your query reports two members. Explain support evidence versus candidate identity, then fix projection/deduplication. Predict what happens when a genuinely different M009 has the same contacts.

<details><summary>Reasoning guide</summary>
R007–M007 is one edge even with two supporting conditions. M009 would be another edge because member identity differs. Deduplicating only source IDs loses ambiguity; deduplicating all columns including reason can manufacture it. Match the three identity columns; keep reasons separately if needed.
</details>

## Evidence to keep

Submit both query files, exact rows, a NULL example and the changed-input result. Explain your join and grouping grain. The public checker is an aid; the coach will ask you to solve a new variation.
