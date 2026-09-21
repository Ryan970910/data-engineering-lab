# What data engineering actually is

## Start with a promise, not a tool

A data engineer builds systems that make data usable and dependable for someone else. The work includes collecting records, describing what they mean, changing their shape without changing their intended meaning, delivering them to a consumer, and operating the process when something fails.

The consumer might be an analyst, an application, an operations team or another pipeline. In your project, a consumer is the membership workflow that needs a trustworthy relationship between incoming ROI/Buyer records and existing members. The valuable outcome is not “a Python script ran.” It is “the right records were processed using the agreed rules, the result can be explained, and a rerun will not cause an uncontrolled duplicate action.”

A pipeline is a sequence of operations that moves data toward that outcome. A data platform is a collection of capabilities used by many pipelines: storage, compute, scheduling, security and monitoring. You can learn pipeline engineering on one laptop. You do not need a cloud platform to start, and a laptop exercise does not establish experience operating a production cluster.

## A concrete problem before any vocabulary

Imagine that the same Buyer spreadsheet is uploaded twice. One row has an empty email. Another row shares a phone number with a different person. A request to update a member times out, but the receiving system may already have saved it.

A script that reads a spreadsheet and sends requests has not automatically solved these problems. You must ask:

1. What identifies the input batch? A filename alone can be reused.
2. What does one row represent? A source application is not necessarily one unique person.
3. Which identity rules are authorized? A convenient phone match may be wrong.
4. What evidence shows that the result is correct? A row count is not a relationship check.
5. What happened before the timeout? Retrying an unknown write can repeat an effect.
6. Who is allowed to inspect the data? Hashing an identity field does not make the whole record anonymous.

These questions are data engineering. Airflow and Spark help implement parts of the answer; neither makes the decisions for you.

## The lifecycle

| Stage | Question | Project-shaped example |
|---|---|---|
| Requirements | Who needs which outcome, by when? | A reviewer needs exceptions before a membership import |
| Ingestion | What arrived, from where, and in what version? | Record the batch and preserve its input snapshot |
| Storage | How do we retain and retrieve it? | Keep raw, validated and delivery artifacts separate |
| Transformation | How does meaning become a useful representation? | Form permitted identity links |
| Quality | What must be true before use? | Reject duplicate source IDs; preserve ambiguous candidates |
| Delivery | Which consumer receives which effect? | Write only approved decisions to a mock receiver |
| Operation | Can we observe, repair and rerun it? | Reconcile an acknowledged or uncertain delivery |
| Governance | Who may access, retain or publish it? | Publish synthetic examples, never real member records |

Governance, testing and observability run across the lifecycle. They are not cleanup steps after a successful demo.

An **ETL** pipeline extracts data, transforms it, then loads a target. **ELT** loads data into a capable analytical system before doing many transformations there. The distinction concerns where transformations happen, not whether one method is universally modern. A pipeline may contain both patterns at different boundaries.

## What belongs to which role?

A data analyst interprets data to answer business questions. A data scientist may build statistical or predictive models. A software engineer develops application behavior. A data engineer makes data flows dependable. Real jobs overlap: all four may write SQL, and all four must care about correctness.

Do not define the role as “the person who uses Spark.” A well-tested Python/SQL pipeline can demonstrate stronger engineering than an unreliable cluster job. Conversely, being able to clean one CSV manually is not evidence of scheduling, recovery or incremental processing.

## Worked example: success is more than a green task

Suppose a teaching run reads 15 source records and produces 13 candidate membership edges. Nine source records have exactly one candidate, two have multiple candidates, and four have none.

A useful success statement is:

> For input snapshot H and rule version V, every source record received a decision. Nine unique matches were delivered to the local mock receiver. Two ambiguous records and four unmatched records remained visible. Replaying the same result inserted zero additional operations.

“Imported 15 records successfully” would conceal several different concepts. It confuses input records, relationship edges, unique decisions and external writes. Learning to distinguish these quantities is one of the first signs of engineering judgment.

## Guided lab: write the promise

No software installation is required.

Write a one-page service brief for an imaginary daily membership batch. Include the consumer, input sources, output grain, authorized matching rules, delivery deadline, failure behavior and privacy boundary. Treat the deadline as your proposed requirement, not a measured fact about the real project.

Then write three acceptance criteria with observable evidence:

- Every valid source ID appears exactly once in the decision output.
- No ambiguous record is silently converted into a unique match.
- Replaying one completed batch adds zero duplicate mock operations.

For each criterion, name the file, query or test that could prove it. “It works” is not an observable acceptance criterion.

## Independent challenge

A stakeholder asks for “real-time data” but only reviews the report each morning. Ask five questions that might justify a simpler daily batch. Cover decision latency, source availability, acceptable delay, failure recovery and operating cost. End with a conditional recommendation, not a tool shopping list.

## Failure investigation

A task is green, but a reviewer reports that the wrong person was updated. Separate orchestration success, transformation correctness and delivery correctness. State one piece of evidence you would inspect for each. Do not start by increasing the retry count.

<details><summary>Reasoning guide — open after attempting the work</summary>
A task can exit successfully while using the wrong join condition. Reconstruct the input snapshot, inspect the specific source-to-member edge and rule version, then compare the intended delivery with the receiver's recorded effect. A count alone cannot identify which relationship was wrong. A daily batch may be sufficient if the decision and source refresh are both daily; choose streaming only for a concrete latency or event-processing need.
</details>

## Evidence to keep

Save your service brief, three measurable criteria and the failure investigation as M00 evidence. You are demonstrating requirements analysis and precise terminology, not yet claiming pipeline implementation experience. A coach should be able to change the consumer or deadline and hear you revise your design coherently.
