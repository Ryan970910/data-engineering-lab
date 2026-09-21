# A working data-engineering glossary

## Data and meaning
**Record:** one represented observation/entity/event at a declared grain. A row is not automatically a person.

**Grain:** what exactly one row means. Candidate edge and source-record decision are different grains.

**Schema:** field names, types and structural constraints. A schema alone does not express every business rule.

**Contract:** the agreed meaning, structure, identity, freshness and failure policy for data.

**Natural key:** business-derived identifying fields, such as an approved matching combination. It may be nonunique or change.

**Surrogate key:** an assigned identifier independent of business attributes. It does not automatically solve entity resolution.

**Composite key:** several fields used together. In the lab, source + record_id distinguishes ROI from Buyer identities.

**Cardinality:** how many rows on one side relate to another. One-to-many joins can legitimately increase row count.

**NULL:** SQL's missing/unknown value, not an empty string or zero. Use IS NULL rather than = NULL.

**Candidate:** a possible relationship allowed by a matching rule. A candidate is not automatically an approved final identity.

**Deduplication:** collapsing repeated representations under an explicit key. The chosen key determines what information is lost.

## Pipeline design
**Ingestion:** acquiring source data with provenance and an arrival contract.

**ETL / ELT:** extract-transform-load versus extract-load-transform. The distinction concerns where/when transformation happens, not quality.

**Batch:** processing a bounded collection. Frequent micro-batches are still bounded work units.

**Streaming:** processing an ongoing sequence, requiring explicit event-time, state and late-data policies.

**Snapshot:** a frozen representation of input at a point/boundary. It supports replay and lineage.

**Manifest:** metadata describing selected artifacts, identities and checksums. It is not the dataset itself.

**Lineage:** the relationship between outputs, input versions and transformations.

**Quarantine:** retaining records excluded from an approved path with reasons and a resolution process.

**Schema evolution:** controlled change to data structure with compatibility rules.

## Storage and analytics
**OLTP:** transactional operational workloads with small consistent reads/writes.

**OLAP:** analytical workloads scanning and aggregating larger historical datasets.

**Warehouse:** an analytical data platform emphasizing structured models and managed querying.

**Lake:** file/object-oriented storage requiring deliberate organization, governance and metadata.

**Lakehouse:** capabilities for managed analytical tables on file/object storage; not just a Parquet folder.

**Parquet:** a typed columnar file format. It does not alone provide cross-file transactions.

**Partition pruning:** skipping partitions that cannot satisfy a query's filters.

**Fact table:** measurements at a declared grain. **Dimension:** descriptive context used to analyze facts.

**SCD:** slowly changing dimension strategies; Type 1 overwrites, Type 2 retains versions.

## Reliability and orchestration
**Transaction:** a defined set of database operations committed or rolled back together.

**Idempotency:** repeated application of the same logical operation has the same intended effect within a stated boundary.

**At-least-once:** an execution/delivery guarantee that permits repetition.

**Operation key:** stable identity for a logical operation, distinct from its attempt ID.

**Retry:** another attempt; it does not itself provide safe effects.

**Outbox:** durable messages committed alongside local data changes, then delivered separately.

**DAG:** directed acyclic graph describing dependencies.

**Task instance:** one task in one orchestration run. A retry is another attempt of it.

**Data interval:** the data time window for a scheduled run, distinct from when it actually executes.

**Backfill:** processing historical intervals. It requires the same correctness and replay protections as current work.

**XCom:** Airflow's small inter-task coordination data mechanism; pass references, not large datasets.

## Spark execution
**Driver:** coordinates a Spark application and builds plans.

**Executor:** executes tasks and stores partitions for an application.

**Transformation:** an operation defining a new dataset/plan. **Action:** triggers computation or output.

**Partition:** a portion of distributed data processed by tasks.

**Shuffle:** redistribution of data across partitions, often needed for joins and aggregates.

**Broadcast join:** distributes a small relation to avoid shuffling the larger one.

**Skew:** uneven data/work distribution causing disproportionately heavy tasks.

**Cache/persist:** retain computed data for reuse, consuming resources; materialization still requires execution.

**UDF:** user-defined function. Built-in expressions are often more optimizable when they express the same logic.

## Change and operations
**Event time:** when the business event occurred. **Ingestion time:** when it entered your system.

**Watermark/checkpoint:** a bound or state representing processing progress; its precise semantics depend on the system.

**CDC:** capturing source changes, often from a database change log. Timestamp polling has different guarantees.

**Tombstone:** an explicit deletion representation.

**Reconciliation:** compare incremental/current outputs with an independent/full source of truth.

**SLI:** a defined reliability measure. **SLO:** a target for that measure over a stated period.

**Pseudonymization:** replacing direct identifiers while retaining possible linkability; hashing is not automatic anonymity.

Return to the relevant module to see each term in an experiment. Knowing a definition is not equivalent to being able to design or debug its use.
