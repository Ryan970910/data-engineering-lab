# Prove your skills with an independent capstone

## What counts as hands-on experience?
Reading demonstrates exposure. Running supplied code demonstrates environment operation. Implementing and testing a transformation demonstrates practice. Diagnosing a new failure, explaining trade-offs and reproducing results demonstrates deeper capability.

A synthetic project is valuable when described honestly. It is not production deployment merely because it uses Airflow and Spark. Aim for a defensible portfolio, not a webpage badge.

## The capstone brief
Build a fictional membership pipeline with the project's two distinct matching relations. Keep ROI–Buyer name/hash matching separate from source–member name/contact matching. Preserve identity, multiple candidates and unmatched records.

Ingest a versioned batch, freeze a snapshot, calculate edges with your PySpark code, validate contracts, quarantine ambiguity and deliver eligible decisions to a replay-safe mock receiver. Use Airflow for coordination. Add an incremental extension with an explicit version contract, or justify deferring it in favor of full refresh.

Do not connect to production databases, APIs, email or UI. Do not publish company source, customer records or configuration. Use original learning code and synthetic fixtures.

## Deliverables another person can use
Your README explains the business problem, scope and non-goals before tools. Include architecture, contracts, exact setup, versions, a baseline command and test commands.

Provide deterministic fixtures with expected identities. Store code and compact redacted evidence, not generated datasets, credentials, dependencies or whole service logs. Explain output locations and reproduction.

Include a decision record explaining why Airflow/Spark are useful for learning, when Python/SQL would suffice and what distributed production would require.

## A reproducible demonstration
Ask another person to start from a clean checkout. They should identify the interpreter, run checks, launch the DAG and inspect outputs without asking where files are hidden.

Demonstrate success, repeated logical delivery, malformed input rejection, ambiguity quarantine, transformation failure blocking delivery and corrected rerun. Record commands, exits, run/input identities and outputs. Screenshots supplement, not replace, executable evidence.

## Independent assessment
The coach grades correctness, explanation, independence and diagnosis from 0–5. Passing requires 16/20, every dimension at least 3 and no critical defect. Read Assessment for the complete rubric.

After visible tests, the coach supplies an unseen variation: a new duplicate pattern, equal timestamps, missing keys or failure at another boundary. Do not select an assessment input merely because your code already handles it.

Record hints. Documentation use is normal engineering; claiming independence after copying a solution is not. A failed checkpoint identifies the next practice target.

## Guided lab: write an evidence index
Map each claim to code, test, artifact and limitation:

| Claim | Evidence | Limitation |
| --- | --- | --- |
| Preserved matching in Spark | Exact edge tests and unseen fixture | Synthetic normalized input |
| Orchestrated dependencies | DAG and failed-quality run | Single host/local storage |
| Recovered uncertain delivery | Attempts and receiver count | Mock protocol only |
| Evaluated performance | Plans and repeated timings | Local mode, not cluster scale |

Remove unsupported claims. Keep planned, implemented and validated separate.

## Independent challenge
Prepare a ten-minute walkthrough without reading a script. Explain one record end to end, one failure, one rejected design and one unresolved risk. Solve a new fixture while explaining your reasoning.

A week later, rebuild a key transformation from its contract without reopening your implementation. Repeat an unseen-variant assessment. Retention matters more than finishing pages quickly.

## Portfolio wording
A defensible statement is: “Built a synthetic membership-data pipeline using PySpark local mode and Airflow on WSL; implemented exact-identity tests, ambiguity handling and mock-receiver retry recovery.”

Do not claim production distributed deployment unless it actually happened with authorization and evidence. Quantify only measured results with conditions stated.

## Failure investigation
You reproduce the tutorial but cannot explain a left join for decisions. Return to M05/M07, draw the lost unmatched record and implement a tiny example. Do not memorize a screenshot of the expected DAG.

<details><summary>Reasoning guide</summary>
Mastery transfers a concept to a new situation and diagnoses failures. Code, tests, decisions and honest limits make that visible. A course progress bar measures reading, not engineering competence.
</details>

## Submit for review
Export your evidence draft, attach synthetic code and outputs, and say: “Assess M19. Check my evidence, ask me to explain the design, then give me an unseen variation before deciding whether I pass.”

No checkpoint is passed merely because this website or its author tests work.
