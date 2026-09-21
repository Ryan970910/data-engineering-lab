# Process changes and make operations observable

## Full refresh versus increment
A full refresh recomputes from a complete snapshot. An incremental pipeline processes changes since a checkpoint. It can save time but introduces state, late arrivals, updates, deletions and recovery complexity.

First define identity, source change signals, ordering and reconciliation. A small nightly snapshot may be simpler and safer.

Change data capture captures insert/update/delete events from a source change mechanism, often its transaction log. Polling WHERE updated_at > watermark has different guarantees. Do not label a timestamp filter log-based CDC.

## Watermarks are contracts
Two records share a timestamp; failure happens after only one commits. Advancing past that timestamp can lose the second. A compound cursor such as (updated_at, stable_id) can provide deterministic order if the source supports that contract.

Late events may have older event times. An overlap window rereads recent data, but needs safe merge/deduplication. It is not a universal guarantee: define tolerated lateness and periodic reconciliation.

Advance a checkpoint only after durable output commits. If output and checkpoint cannot commit atomically, design a replay-safe protocol. A checkpoint claims completed work, not merely the last observed row.

## Guided lab: reason about a timeline
Create five synthetic events with event_id, entity_id, version, event_time, ingested_at, operation and payload. Include two updates for an entity, equal timestamps for different entities, a late event and a delete.

Write expected final state before coding. Decide whether higher version or later ingestion wins and how conflicts are rejected. Deletion needs a tombstone or equivalent policy; absence from a partial batch does not imply deletion.

Use timezone-aware ISO timestamps. Store UTC for comparison and convert explicitly to Hong Kong time for business dates. Do not mix naive local timestamps with UTC or derive every report date from the computer clock.

## Independent challenge
Build a standard-library or SQLite consumer in a separate practice folder. Keep append-only events, current-state table and checkpoint. Test:
1. Same batch twice.
2. Failure after output commit but before checkpoint advancement.
3. Equal timestamps.
4. Out-of-order update.
5. Delete followed by replay.
6. Reconciliation against full recomputation.

Document version rules. Keep this fictional extension separate from production matching; the course does not prescribe production CDC semantics.

## Logs, metrics and alerts
A log describes an event. A metric summarizes a quantity over time. Lineage links outputs to inputs and transformations. A trace connects spans across services. None substitutes for the others.

Useful fields include run_id, stage, attempt, input hash, code version, duration, counts and error category. Metrics include freshness, processed/rejected rows, ambiguity rate and retry rate. Do not log raw contacts for convenience.

A service-level indicator is a precise measure, such as the fraction of daily batches validated by 09:00 Hong Kong time. A service-level objective sets its target over a defined period. Alerts should indicate actionable failure or risk, not every harmless retry.

## Governance and access
Hashing an HKID does not automatically anonymize it. Predictable identifiers can be guessed; linked records can remain identifiable. Only fictional data belongs in public repositories, screenshots and portfolios.

Keep secrets outside code, grant least privilege, define retention/deletion and record lineage without publishing payloads. Source contracts need an owner and escalation path. Governance is part of engineering.

## Failure investigation
A dashboard reports 100% success because it counts only completed runs; missing expected runs never enter the denominator. Redefine against the expected schedule or arrival contract. Explain why zero incoming data can mean outage rather than a successful empty day.

<details><summary>Reasoning guide</summary>
Incremental correctness needs identity, conflict handling, durable progress and replay safety. Operational correctness also requires detecting absence. A green task without the expected input may not fulfill the business obligation.
</details>

## Evidence to keep
Submit events, expected state, checkpoint protocol, replay/failure tests, reconciliation and a redacted report. Include an alert with a concrete action and a retention statement.
