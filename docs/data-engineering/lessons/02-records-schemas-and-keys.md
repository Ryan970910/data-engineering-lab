# Records, schemas, keys and grain

## A row has a meaning

Before writing a join, finish this sentence: **one row represents ...** This is the table's grain. In the source table, one row represents one ROI or Buyer application record. In a member table, one row represents one member record. In the candidate table, one row represents a possible link from one source record to one member.

Confusing these grains causes familiar bugs: counting candidates as people, deduplicating different applications by name, or grouping away an unresolved match. Correct code at the wrong grain still produces the wrong business answer.

A schema describes fields and their types. A contract adds meaning: required values, uniqueness, permitted changes, interpretation and ownership. A string column called id does not tell you whether its value is unique globally, per source or only per file.

## Our small model

| Relation | Grain | Identity key |
|---|---|---|
| source_records | One source application | source + record_id |
| members | One member | member_id |
| roi_buyer_pairs | One permitted ROI–Buyer relationship | roi_id + buyer_id |
| member_candidates | One possible source–member relationship | source + record_id + member_id |
| decisions | One decision per source application | source + record_id |
| deliveries | One accepted mock operation | operation_key |

A **primary key** identifies a row in a relation. A **foreign key** refers to a key in another relation. A **composite key** uses several fields. A **natural key** comes from the domain; a **surrogate key** is assigned for technical identity. Neither naming convention proves that the key is correct.

In our combined source relation, source is part of the identity because two producers may both use record ID 001. The original fixture uses visibly different R and B prefixes, but that convenience should not hide the general requirement.

## Types are part of correctness

Keep phone and identity values as strings. Numeric conversion can remove leading zeros, lose formatting or introduce scientific notation. A field can contain only digits and still be an identifier rather than a quantity.

Distinguish empty string, whitespace, NULL/Python None and a placeholder value. Two missing values do not prove that two people share a phone. SQL comparisons with NULL usually produce an unknown result; Python's None equality behaves differently. Specify the contract rather than assume each engine's defaults mean the same thing.

The reference pipeline requires an exact CSV header, non-empty unique source IDs and a non-blank name. It assumes contact normalization has already happened. The SQL lab converts blank strings to NULL for teaching SQL missing-value semantics. That representation change is deliberate and documented, not a new production cleansing rule.

## Worked example: cardinality

Suppose ROI R004 can match members M004 and M005. A join produces two candidate rows. Grouping by source and record ID should count **distinct member IDs**, not the number of supporting reasons.

Now suppose both phone and email link R007 to M007. There are two reasons but one candidate identity edge. If you UNION ALL the two branches and count rows, R007 might falsely appear ambiguous. Deduplicate on the identity edge first, or count distinct candidate members.

A one-to-many relationship is not automatically an error. It becomes an error if the consumer expects one-to-one and the pipeline silently chooses a row.

## Schema evolution

Adding an optional field, renaming a required field and changing a field's type are different events. A strict reader may intentionally reject all unexpected schema changes. A more flexible reader may accept additive optional fields while failing on missing keys. The choice should be tested, versioned and communicated.

Never “fix” a missing hkid_hash field by substituting phone without authorization. That is not schema compatibility; it changes the identity rule.

## Guided lab: reason before running

Make a five-row handwritten table: R001/ADA/hash-a/phone 100; B001/ADA/hash-a/phone 999; R004/DAN with phone 400 and email dan@example.invalid; M004/DAN with phone 400 and another email; M005/DAN with another phone and email dan@example.invalid.

Write the expected relationship edges for each permitted rule. Annotate the grain and identity key of each output. Explain why the absence of a member row for ADA in this five-row sample is different from a failed ROI–Buyer pair.

## Independent challenge

Create a contract for a new source containing source, record_id, name, phone and email. Include types, uniqueness scope, missing-value policy and schema version. Give one compatible change, one incompatible change and one plausible-looking change that silently alters meaning.

## Failure investigation

A developer fixes duplicate join output using dropDuplicates(["name"]). Explain which valid records can be lost and why the result might still have a plausible total count. Construct two different source applications with the same name to demonstrate the loss.

<details><summary>Reasoning guide</summary>
A name is not a unique source key. Deduplicating by name collapses different applications and possibly different people. Validate the exact identity edge set, not just its size. Schema checks detect shape; semantic checks detect whether relationships still satisfy the authorized rules.
</details>

## Evidence to keep

Submit a data dictionary, the six grains in your own words, your worked edges and a duplicate-counterexample fixture. A coach may replace the IDs or add a second candidate; predict the output before running code.
