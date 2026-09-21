# Ingestion, snapshots and batch boundaries

## Receiving a file is not the same as owning an input

Ingestion brings data across a boundary into a system you control. That boundary might be a CSV export, an API, a database query or an event stream. The engineering task is to record what arrived and make later processing refer to a definite version.

Consider a file called buyer.xlsx. If someone overwrites it at noon, a retry at 13:00 may read different content than the morning attempt. Reusing the same filename does not make the job reproducible. You need an immutable snapshot, an object version or an equivalent source-version contract.

**Immutable** means that a published input version is not modified in place. A correction becomes a new version, with a recorded relationship to the previous version. It does not mean you must retain personal data forever; retention and lawful deletion still require a policy.

## The teaching pipeline's boundary

The lab's seed stage creates fictional CSV files only when they are absent. Extract validates them, serializes the parsed batch to a content-addressed JSON snapshot and writes a manifest containing its path and SHA-256 hash.

Subsequent matching reads the manifest's snapshot. It does not repeatedly reopen the latest raw CSV. Editing raw/roi.csv after extraction therefore should not change a match until you extract again.

The hash is a content fingerprint in a controlled local protocol. It is not encryption, proof that a publisher is trustworthy, or a substitute for access control. The teaching serializer sorts dictionary keys, but preserves row order; reordering otherwise identical rows can produce a different snapshot hash. Explain this limitation rather than conceal it.

## ETL and ELT in this example

Reading source CSV is extraction. Creating candidate relationships is transformation. Saving a mock receiver operation is loading/delivery. An analytical warehouse might first ingest raw records and then transform them with SQL: an ELT boundary.

A pipeline can use ETL for an operational API and ELT for analytical reporting. Neither word determines whether a business rule is correct. You still need source versions, identities, tests and ownership.

**Batch** processes a bounded collection such as a daily file or a fixed snapshot. **Streaming** continuously processes arriving events. A stream may include duplicates, out-of-order events and late corrections; it is not merely a very fast for loop. Start with a batch when the consumer's actual deadline permits it. Add streaming after defining why lower latency is valuable and how event-time behavior will work.

## Worked example: half-written input

A producer writes directly into the path the consumer watches. The consumer may see only the first half of the file and interpret it as a complete batch. A safer contract is to write a temporary object, verify completion, then publish a manifest or move it into the agreed completed location.

On a local filesystem, renaming can provide a useful publication boundary when the relevant filesystem operation is atomic. Do not generalize that into “rename is atomic everywhere,” especially across filesystems or on object storage. For remote storage, use its actual object-version and completion semantics.

A completed batch manifest might contain producer, batch_id, schema_version, input_uri, checksum, record_count and arrival_time. Those fields serve different purposes. Record count is an inexpensive check, not a complete integrity proof.

## Guided lab: specify a batch

Design a manifest for a fictional Buyer batch of seven rows. Use invented locations and timestamps. Define which field identifies the producer, which identifies the business batch and which pins content.

List three checks at arrival: schema compatibility, expected completeness and duplicate batch handling. For each failure, say whether to reject, quarantine or wait. Explain what the downstream consumer may read before completion.

You will implement the supplied snapshot experiment in M06. Predict now: after extract, will changing the raw phone field affect match? What event is required to adopt the correction?

## Independent challenge

An API returns records in pages of 100. Page 2 fails, and the source changes between retries. Design a pagination exercise plan that checks stable ordering/cursor behavior, checkpoint scope, overlapping records and the definition of complete extraction. Do not assume offset pagination is a stable snapshot.

Document what guarantee the source API would need to make. If it offers no snapshot guarantee, describe a reconciliation strategy and the limitation you would report to the consumer.

## Failure investigation

A new output file exists, so a downstream job treats extraction as successful. Later you discover that only three of seven rows were written. Explain why existence is not a completion contract. Propose a minimum manifest-based check and one failure-injection test.

<details><summary>Reasoning guide</summary>
The consumer should follow a published completed manifest, not infer completion from a filename appearing. The extractor should fail rather than publish a success marker when a page or file is incomplete. Retrying should either use the same pinned input or explicitly create a new input version. Mixing old and new pages can silently create a dataset that never existed at the source.
</details>

## Evidence to keep

Save your manifest specification, a producer/consumer publication sequence and a pagination risk analysis. Distinguish assumptions from tested behavior. In a portfolio, describe this as an ingestion contract until you have implemented and exercised it.
