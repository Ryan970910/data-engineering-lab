# Run and explain a complete pipeline

## From a script to a pipeline
A pipeline is a sequence of transformations with explicit inputs, outputs and failure conditions. A Python function can be one stage; a folder of scripts does not automatically provide a reliable pipeline. You need to know which input version produced an output and whether later stages may proceed.

Our offline pipeline is deliberately small. Seed creates fictional CSVs. Extract validates their structure and freezes a snapshot. Match produces identity edges and decisions. Validate compares the result with the snapshot contract. Deliver writes eligible decisions to a mock receiver. The reference implementation is provided so you can observe a trustworthy baseline before replacing parts independently.

In the real project, application/bulk_import.py is the entry and dispatch boundary. Source parsers and the member API workflow have more responsibilities and external side effects. The learning pipeline demonstrates separable stages; it is not a claim that production already has these guarantees.

## Predict before running
In the baseline, eight ROI and seven Buyer records produce 15 member decisions. A decision is not an ROI–Buyer edge. The ROI–Buyer relation contains five pairs, while the member candidate relation contains 13 edges. Nine source records have exactly one member candidate, two have multiple candidates and four have none.

Write those four different grains in your notes. If you see “13 matched” in a report, ask whether it counts edges, records or people.

## Guided lab: run each boundary
Complete M04 first. In PowerShell, at the standalone course repository root:

~~~powershell
$python = ".\.venv\Scripts\python.exe"
$work = "D:/projects/data-engineering-lab/.learning-runtime/first"
& $python docs/data-engineering/lab.py seed --workspace $work
& $python docs/data-engineering/lab.py extract --workspace $work
& $python docs/data-engineering/lab.py match --workspace $work
& $python docs/data-engineering/lab.py validate --workspace $work
& $python docs/data-engineering/lab.py deliver --workspace $work
Get-Content "$work/manifest.json"
Get-Content "$work/quality.json"
Get-Content "$work/delivery.json"
~~~

Inspect the exit code immediately after a command with $LASTEXITCODE. A fresh workspace should report matched 9, ambiguous 2, unmatched 4, roi_buyer_pairs 5 and member_candidate_pairs 13. The first delivery inserts nine; a repeat delivery inserts zero and leaves nine total. If your folder already contains a modified exercise, do not force it to match these numbers: use a new folder or inspect its snapshot.

Open raw/roi.csv, manifest.json, the snapshot named by the manifest, result.json and quality.json in that order. Follow R004 through the files. Its two member candidates remain visible; no arbitrary “first member” is chosen.

## Why snapshots matter
The manifest points to a specific JSON snapshot and records its content hash. Match reads that snapshot, not the live raw CSVs. A file edit after extraction does not secretly change an in-progress batch. This separates “what arrived now” from “what this run is processing.”

A hash detects a change to the represented data, not malicious tampering by someone who can rewrite both snapshot and manifest. The current digest also includes row order. It is not a universal semantic identity for an unordered relation.

## Independent challenge
In a new workspace, run seed and extract. Record the snapshot hash. Change B002's hash in raw/buyer.csv using an editor. Predict what match will do before you extract again. Run match and validate, inspect the pair list, then rerun extract and repeat.

Write a small Python command that summarizes decisions by source and status without changing the files. Reconcile the six grouped counts back to 15 total decisions. Do not simply print the provided expected dictionary.

## Failure investigation
Edit a copy of result.json to add an invalid ROI–Buyer edge R005–B005. Run validate. It must exit nonzero with RESULT_MISMATCH. Then run match to rebuild the result and validate again. Does a previously created delivery.json prove this new attempt succeeded? No: it may belong to an earlier attempt.

<details><summary>Reasoning guide</summary>
Before re-extraction, the old snapshot still contains B002's old hash and its edge remains. After re-extraction, the new snapshot changes that edge. Phone matching to a member is independent of this hash change. Failure evidence must include the attempted command, its exit code and the relevant input hash; a stale success file is not proof of current success.
</details>

## Evidence to keep
Provide the file lineage, baseline output, before/after snapshot hashes, exact changed edge and rejected-result output. Explain why validation runs before delivery. The supplied baseline passing is an author-contract check, not proof that you can implement the pipeline unaided.
