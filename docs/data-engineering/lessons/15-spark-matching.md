# Implement matching with PySpark

## Preserve the contract while changing the engine
You have reasoned about the relationships in Python and SQL. Now implement the same two edge relations using DataFrames. The goal is not to translate every loop literally; it is to express the same semantics through joins, projections and identity-based deduplication.

The supplied spark_exercise.py contains an intentionally incomplete build_pairs(spark, batch). Running it unchanged raises NotImplementedError. That is a learner task, not a missing dependency. Do not replace it with lab.reference and label it Spark experience.

## Define the output first
Return two DataFrames:
- ROI–Buyer: roi_id and buyer_id, both strings.
- Member candidates: source, record_id and member_id, all strings.

The baseline expects five ROI–Buyer edges and 13 unique member edges. The checker changes data, so hardcoding counts or rows is invalid. Empty Buyer input must still yield a correctly typed empty first DataFrame.

Input fixtures are already normalized. Do not add a normalization policy or infer identity across relations.

## Guided implementation plan
Create ROI, Buyer and member DataFrames with an explicit all-string schema. Alias them before joins to avoid ambiguous name/id columns.

For ROI–Buyer, join with name equality, hash equality and usable nonblank hash/name guards. Select only ROI ID and Buyer ID under the required output names.

For member matching, add a literal source column to each source DataFrame and combine them with unionByName. Build a phone join and an email join, each requiring equal name and a usable contact. Project the same three identity columns from each branch. Union the branches and drop duplicates on those three columns.

A single OR join may be logically correct but can yield a different physical plan. Start with readable separate branches, establish correctness, then compare alternatives. Never deduplicate only on source record ID: that loses multiple members.

## Run the public checks
In Ubuntu Bash, from the standalone checkout:

~~~bash
source docs/data-engineering/env.sh
source "$CLUB_LAB_ROOT/venv-spark/bin/activate"
python docs/data-engineering/spark_exercise.py --evidence "$CLUB_LAB_ROOT/spark-evidence.json"
~~~

The five public cases cover baseline, a second GIA member, same contact with a different name, null keys and empty Buyer input. All five must pass. The evidence status deliberately says PUBLIC_CASES_PASSED_NOT_MASTERY_CERTIFICATION.

The harness collects bounded tiny fixtures to compare exact identities. Your implementation must remain DataFrame-based and must not collect or convert to pandas. Bounded test inspection and unbounded production collection are different decisions.

## Independent challenge
Write additional fixtures without copying public tests:
1. Two Buyer IDs share a name/hash, producing one-to-many ROI edges.
2. A phone match and email match point to different member IDs.
3. A contact appears under a different name.
4. Both sources reuse the same record_id string; source must preserve identity.
5. All member rows are absent.

Predict exact rows on paper, then test. Ask the coach for an unseen variant after submitting your implementation. Visible fixtures alone cannot establish independence.

Extend your solution to produce decisions for every source record. Group candidates by source and record_id, count distinct member IDs and left-join to source identities. Fill missing counts with zero, then assign statuses. Compare the conservation invariant with M08.

## Failure investigation
GIA appears twice. Did you include match_reason during deduplication? DAN contains only one member. Did you deduplicate at source grain or use a dictionary that overwrites candidates?

An “ambiguous reference” error often means both joined DataFrames have a column with the same name. Use qualified aliases and project intentionally. Renaming every input field randomly makes the schema harder to maintain.

<details><summary>Reasoning guide</summary>
Preserve distinct member identities and collapse duplicate support for the same identity. SQL UNION, a Python set and Spark dropDuplicates can express this, but only with the correct projected key. The output grain determines correct deduplication.
</details>

## Evidence to keep
Submit build_pairs, five-case output, independent fixtures, exact comparisons and an explanation of each join. Include Spark/Python/Java versions and local configuration. Explain blank keys and ambiguity.

Do not claim scale or production deployment. You have demonstrated a contract-preserving Spark transformation on synthetic cases; performance and operational claims require separate evidence.
