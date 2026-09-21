# Turn matching rules into transformation contracts

## Separate business meaning from implementation
A business rule says which relationships are allowed. An implementation chooses loops, indexes, SQL or Spark to calculate them. Changing the engine must not silently change the rule. Faster incorrect results are still incorrect.

For this project, ROI and Buyer match on name plus hashed HKID. ROI or Buyer and a member match on name plus phone, or name plus email. These are two different relations. Do not reuse a convenient “universal person key” to calculate both.

The course uses already-normalized synthetic strings. Its exclusion of blank matching keys and quarantine of ambiguous candidates are explicit teaching policies. They do not authorize modifications to production normalization, matching or handling rules.

## Specify inputs, outputs and invariants
A useful contract includes field names and types, the row grain, missing-value semantics, identity columns, duplicate behavior and error behavior. For ROI–Buyer output, each row is one (roi_id, buyer_id) edge. For member candidates, each row is one (source, record_id, member_id) edge.

A candidate edge is evidence of a permitted relationship. A decision summarizes how many distinct member identities a source record has. Zero means unmatched; one means matched; more than one means ambiguous in this lab. Never lose unmatched records just because you started from an inner join.

Consider DAN. Phone identifies M004; email identifies M005. Both are legitimate candidates under the teaching rule. Choosing the first one is not a harmless performance optimization. Consider GIA: phone and email both support M007. Two reasons do not mean two candidates.

## A worked algorithm
First construct an index from (name, nonblank hash) to a list of Buyer IDs. For each ROI record, find all Buyers under that key. Use a list rather than a single ID because the input contract has not guaranteed one record per key.

For members, build separate (name, phone) and (name, email) indexes, excluding empty keys. For each ROI or Buyer record, union the member IDs from both indexes. Emit unique identity edges and one decision for each input record.

The reference uses nested loops for readability. An indexed implementation can reduce repeated comparisons, but its memory use grows with the index. It still needs identical outputs on duplicates, blanks and one-to-many relationships.

## Guided lab: trace by hand
Without running code, predict outcomes for these cases:
- ADA: ROI and Buyer have the same name and hash but different contacts.
- CARA: same name and email, different ROI/Buyer hashes.
- ERIN: matching name and phone, blank hashes.
- FINN: matching name and hash, but no member contact.
- GIA: both contact branches reach the same member.

Check result.json from M06. Explain each relation separately. In particular, ADA's Buyer does not inherit the ROI's member automatically: transitive inference is not part of the stated rule.

## Independent challenge
Create .learning-runtime/matcher.py with a pure function build_pairs(batch). It must return both exact edge sets without importing or calling lab.reference. Write it using Python dictionaries and sets.

Use the supplied reference only in tests as an oracle. Compare sorted full tuples, not lengths. Then write at least one hand-authored expected fixture so a shared mistake in your understanding and the reference comparison would be visible.

Add M009 with GIA's name and contacts. Predict that both GIA source records become ambiguous. Reorder all input lists and show that the set of edges and decisions does not change, even though the current snapshot hash may change.

## Failure investigation
A colleague deduplicates member candidates by (source, record_id) because “one output per input is simpler.” Create the smallest fixture proving the bug. Another colleague lowercases names inside the matcher. Explain why normalization policy is a separate business decision, even if the synthetic uppercase fixtures still pass.

<details><summary>Reasoning guide</summary>
Two members sharing a source's contact key produce two distinct identity edges. Deduplication at source-record grain erases the ambiguity. Normalization changes which keys compare equal; preserving the original production behavior requires an explicitly approved contract and regression fixtures.
</details>

## Evidence to keep
Submit your pure function, independent tests, exact baseline comparison, the M009 variant and a short contract document. State complexity and memory assumptions without claiming a distributed system is necessary for 23 tiny records. Be ready to implement an unseen variant while explaining your decisions.
