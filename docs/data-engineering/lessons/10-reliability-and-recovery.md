# Make retries safe

## A timeout is not proof of failure
A sender submits a request. The receiver commits the change. The response is lost. The sender sees a timeout. Retrying may be necessary, but it can duplicate a side effect unless the receiver recognizes the operation.

This is why “retry three times” is not a complete reliability design. At-least-once execution means an operation may execute again. Idempotency means repeating the same logical operation has the same intended effect as applying it once, under a defined contract.

Exactly-once claims need a precise boundary. A local database transaction cannot atomically cover an unrelated remote API without additional protocol support. Airflow task success does not prove that every external side effect happened exactly once.

## Understand the lab's boundary
deliver validates the result, selects only matched decisions, computes an operation key from each decision and inserts into a SQLite table whose key is unique. INSERT OR IGNORE prevents duplicate keys in that one receiver database. A transaction commits the writes before the simulated timeout is raised.

This illustrates receiver-side deduplication. It is not a generic CRM update protocol. The current key is derived from decision fields; changes to source attributes that do not change the decision are not represented. A different workspace has a different receiver database. Cross-workspace deduplication is not demonstrated.

## Guided lab: reproduce uncertain completion
Use a fresh folder. In PowerShell:

~~~powershell
$python = ".\.venv\Scripts\python.exe"
$work = "D:/projects/data-engineering-lab/.learning-runtime/recovery"
& $python docs/data-engineering/lab.py run --workspace $work --fail-after-commit
$LASTEXITCODE
& $python docs/data-engineering/lab.py deliver --workspace $work
$LASTEXITCODE
Get-Content "$work/delivery.json"
~~~

The first command must fail after committing. The retry should report inserted 0 and total 9. If you choose a new workspace for the retry, you are not testing the same receiver and cannot claim recovery deduplication.

Inspect the receiver's deliveries table using a small read-only Python query. Show that failure of the command did not imply rollback of the committed writes.

## Design an operation identity
A robust operation key describes a business operation, not a random attempt. “Update member X to version V” may require a different identity than “create membership request Y.” Generate the same key on a retry of the same operation, but a new key when a genuinely new operation is intended.

A receiver should reject reuse of a key with a conflicting payload, rather than silently accepting whichever arrived first. Deduplication also needs a retention policy: forgetting keys too soon can make old retries unsafe.

A transactional outbox can commit intended messages alongside database changes, then deliver them asynchronously. Consumers still need deduplication. Learn this pattern as a design extension; the lab does not implement a production outbox.

## Independent challenge
Build a separate mock_receiver.py in your practice folder. Store operation_key, payload_hash and payload. Implement three outcomes: new operation inserts once; same key and same payload returns the original result; same key with different payload fails explicitly.

Test all three and simulate a response loss after commit. Do not modify production APIs or use actual member information. Explain how a crash before commit differs from a crash after commit.

## Backoff and classification
A temporary network failure may justify retry with bounded exponential backoff and jitter. A schema violation generally will not improve by waiting. An authorization error requires configuration or access correction. Blind retries can overload a failing dependency and conceal permanent errors.

Define a retry budget, timeout, alert threshold and manual recovery path. Logs should identify an operation without printing its personal payload.

## Failure investigation
A program catches every exception, prints “failed,” and exits zero. The scheduler marks it successful and runs delivery. Reproduce this behavior in a harmless toy subprocess, then correct error propagation.

<details><summary>Reasoning guide</summary>
Schedulers usually observe process exit status, not the emotional meaning of printed text. A failed subprocess must return nonzero or raise through a checked invocation. Recovery evidence needs durable receiver state plus attempt outcomes, not only the final green UI state.
</details>

## Evidence to keep
Submit the two attempt logs with exit codes, the receiver count, your conflicting-payload test and a sequence diagram of the lost-response scenario. State the exact idempotency boundary and one limitation. This explanation is more valuable than writing “exactly once” in a portfolio.
