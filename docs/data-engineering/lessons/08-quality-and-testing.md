# Make data quality executable

## Quality is fitness for a use
A file can be valid CSV and still be unsuitable for matching. A nonempty phone may be stale. A unique record ID does not imply a unique person. Quality rules should protect a downstream decision, not merely produce a reassuring percentage.

Distinguish completeness, validity, uniqueness, consistency, freshness and accuracy. This lab can check structure, identity uniqueness and rule consistency. It cannot establish that fictional contacts belong to real people. Do not label a schema test “accuracy verification.”

## Decide the failure policy
Some failures invalidate the entire batch: a missing required column or a corrupted snapshot means interpretation is unsafe. Some can be isolated to records if the contract allows it. Ambiguous candidate records are preserved and excluded from mock delivery here; they are not silently deleted.

For each rule, write its scope, severity, response and evidence. “Phone is missing” may be allowed when email is usable. “Both contact channels absent” may produce an unmatched result, not a corrupt file. “Duplicate source ID” prevents reliable identity tracking and is rejected by this lab's extraction.

A production quarantine should retain a reason code and a safe reference to the original record, with access controls and a resolution workflow. It must not become an unmonitored dump of personal information.

## Test at several boundaries
Unit tests target one transformation using small fixtures. Contract tests check schema, keys and output semantics. Integration tests exercise connected stages and artifacts. Regression tests retain known tricky cases. End-to-end tests include the actual entry point and receiver behavior.

A test suite passing means only that the tested conditions passed. It does not mean every dependency, machine or business dataset works. This distinction matters because an import-only “dry run” did not previously catch every runtime dependency in the desktop project.

## Guided lab: use the author check honestly
In PowerShell, choose a new empty folder:

~~~powershell
& .\.venv\Scripts\python.exe docs/data-engineering/verify_course.py --workspace D:/projects/data-engineering-lab/.learning-runtime/author-check
~~~

Read its console output and verification.json. It checks the supplied baseline, snapshot pinning, schema/ID rejection and committed-failure recovery. It explicitly does not certify your Spark solution, Airflow installation or mastery.

Now inspect the tests themselves. For each assertion, name the defect it would detect and one defect it would miss. Syntax checks of a DAG cannot prove the scheduler can import it with installed dependencies.

## Independent challenge
Write unittest cases for your M07 matcher. Include different names with the same contact, blank contacts on both sides, one matching contact, two reasons for one member, two different members, empty Buyer input and input reordering.

For file-level tests, create separate temporary workspaces under .learning-runtime/tests. Never mutate the only baseline folder repeatedly and then depend on test order. Use a fixed seed for generated cases and report that seed.

Add a conservation assertion: every ROI/Buyer source identity produces exactly one decision, and matched + ambiguous + unmatched equals the number of source records. This catches losses that an edge-count test can miss.

## Schema evolution is a policy
Suppose a vendor adds a marketing_opt_in column. The current extractor expects an exact ordered header and will fail. That behavior is intentional and conservative, not automatically a bug. An evolution policy might accept additive optional fields while still rejecting renamed identity fields. Implement such a policy only in your independent learning code, version the contract and test old/new inputs.

Backward compatibility means new code can read older data under the chosen contract. Forward compatibility means old consumers can tolerate a newer representation. Neither is achieved simply by catching all exceptions.

## Failure investigation
Remove the email header in a copied fixture, add a duplicate ROI ID in another, and corrupt a snapshot in a third. Predict the failing stage and downstream behavior for each. Capture nonzero exits and show that you did not treat stale quality.json as the current outcome.

<details><summary>Reasoning guide</summary>
Malformed schema and duplicate IDs should fail during extraction. Snapshot tampering should fail when the manifest-bound snapshot is read. Catching the exception and continuing to delivery would defeat the safety boundary. Recovery requires fixing the input or restoring a trustworthy snapshot, then rerunning the relevant stages.
</details>

## Evidence to keep
Submit tests, a rule/policy table, one deliberately failing test and its fix, and a coverage statement in plain English. Do not equate a percentage coverage metric with complete behavioral coverage.
