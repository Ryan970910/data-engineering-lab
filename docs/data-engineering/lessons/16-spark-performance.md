# Read execution plans and measure performance

## Performance begins after correctness
Programs producing different rows are not comparable optimizations. Freeze the output contract and exact-result tests before changing partitioning, join strategy or caching.

For tiny data, startup and scheduling can dominate. A slower Spark result than Python is not a failed lesson. It shows tool choice depends on workload. Your portfolio should explain when you would not use Spark.

## Plans, stages and shuffles
A logical plan describes operations. Spark optimizes it and selects a physical plan. explain("formatted") shows physical operators. An Exchange often indicates movement between partitions. Joins, aggregations and deduplication may require shuffles, depending on partitioning and strategy.

A shuffle redistributes rows so related keys can be processed together. It can involve network transfer, disk spill and synchronization. Local mode has no real multi-machine network, but shuffle costs still exist.

Broadcast joins send a small side to participating executors to avoid shuffling the larger side. “Small” is relative to memory and configuration, not a universal row count. A forced broadcast that works on the fixture can cause memory failure on real data.

## Partitions, skew and files
Too few partitions can limit parallelism and create large tasks. Too many create scheduling overhead and tiny files. A heavily repeated key can cause skew: one partition does much more work.

repartition typically reshuffles to a target partitioning. coalesce can reduce partitions with less movement but may leave uneven work. Neither should be applied mechanically.

Caching may help when an expensive DataFrame is reused. It consumes memory and must be materialized; call an action before measuring cached reuse and unpersist afterward. Caching a once-used DataFrame can add overhead.

## Guided lab: annotate a real plan
Take your M15 solution and save plans for the ROI–Buyer join and member union/deduplication. Identify source, filter, projection, join and Exchange operators. Do not assume a tutorial screenshot matches: adaptive execution and size can change plans.

Run a warm-up, then at least five comparable measured actions with time.perf_counter. Use the same input, selected columns and output action. Report all timings or median and range, not only the fastest trial.

## Independent challenge: a bounded experiment
Generate larger synthetic inputs using Spark range and expressions, not a giant Python list on the driver. Start modestly and set an explicit row-count limit.

Define roughly uniform keys and a second distribution with one hot key. Preserve a small correctness fixture separately. Compare:
- Default strategy versus explicitly broadcasting a genuinely small member side.
- Several shuffle partition counts appropriate to local[2].
- Repeated action with and without materialized cache.

Measure the action, capture plans, record input/output counts and monitor memory/disk. Stop rather than risking a full disk. Never use real contact data.

Write predictions first. “No meaningful improvement at this scale” is a valid conclusion. Record machine resources and configuration.

## Interpreting results
A local[2] speedup is not cluster scalability evidence. One trial is sensitive to JVM warm-up, OS caching and background load. A count action and a full write may execute different work. Equal row counts do not prove equal identities.

If a join multiplies rows, inspect cardinality before tuning. A contract bug can look like a performance problem. A hot key is not necessarily fixed by more total partitions.

## Failure investigation
A benchmark calls count repeatedly on an uncached join and labels later runs “cached Spark performance.” Distinguish explicitly persisted DataFrames, OS cache and runtime effects. Rebuild the experiment with clear cache state.

<details><summary>Reasoning guide</summary>
Claims require defined inputs, output work, configuration, correctness and repeated measurements. An unexplained number cannot establish why a change helped. Plans show strategy; timings show behavior under particular conditions.
</details>

## Evidence and sources
Submit hypothesis, method, raw timings, plans, checks, conclusion and limitations. Do not advertise “10x faster” without its baseline and conditions.

Read the official [Spark SQL performance tuning guide](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html).
