# Assessment: prove that you can do the work

## Four different learning states
Read means you visited and marked a chapter. Concept-checked means you answered visible questions. Practiced means you executed or implemented the exercise and kept evidence. Assessed means a coach reviewed that evidence, questioned your reasoning and tested transfer with a new variant.

The website records only reading, self-checks and your notes. It never silently promotes those into an assessed pass. Exported evidence is a learner-authored draft, not a certificate.

## Submission format
For each checkpoint, include:
1. Module, objective and exact code revision or file.
2. Environment and versions, including interpreter path.
3. Prediction before running.
4. Commands, exit codes and compact actual output.
5. Input fixture or snapshot hash and expected identities.
6. Tests, one controlled failure and recovery.
7. Explanation of why the result follows from the contract.
8. Help used, uncertainty and limitations.

Use only synthetic data. Do not paste credentials, actual names, phone numbers, HKIDs or company configurations. A screenshot is supporting context, not a replacement for a reproducible command and test.

Copy this request into your coaching conversation:

> Assess M05 (replace with my module). Review the attached code and outputs. Ask me to explain the important choices, then give me an unseen variant. Grade correctness, explanation, independence and diagnosis separately. Do not mark me passed merely because the visible tests pass.

## Scoring rubric
Each dimension is scored 0–5:
- 0: no relevant evidence or fundamentally unsafe/incorrect result.
- 1: can repeat terminology or copy steps but cannot explain them.
- 2: partial success with substantial guidance; important gaps remain.
- 3: correct routine work with a sound explanation and limited assistance.
- 4: independent correct work, useful tests and diagnosis of a new variation.
- 5: strong transfer, explicit trade-offs, robust failure handling and reproducible evidence.

| Dimension | What the coach examines |
| --- | --- |
| Correctness | Exact output, grain, contracts, failure behavior and tests |
| Explanation | Why the design works; alternatives, assumptions and limits |
| Independence | Ability to adapt without copying an answer; transparent help log |
| Diagnosis | Reproducing, localizing and recovering from a controlled new failure |

Pass requires at least 16/20, no dimension below 3, and no critical error. Critical errors include using private data publicly, bypassing a failed quality gate, changing authorized matching semantics silently, losing ambiguous identities or claiming unexecuted work as completed.

Documentation lookup is allowed. The coach should distinguish using a reference from copying the full solution without understanding.

## Checkpoints and required evidence
| Checkpoint | Modules | Required demonstration |
| --- | --- | --- |
| C1: Foundations | M00–M03 | Explain lifecycle and grain; map a new record through the project |
| C2: Relational correctness | M04–M08 | SQL and independent matcher; exact edges; NULL/duplicate/ambiguity cases |
| C3: Reliability | M09–M11 | Historical model, uncertain-commit retry and tool-selection decision |
| C4: Orchestration | M12–M13 | Real Linux versions, successful DAG, retry and blocked downstream task |
| C5: Spark | M14–M16 | JVM action, independent joins, new fixture and measured plans |
| C6: Integration | M17–M19 | End-to-end capstone, failure matrix, reproducibility and honest portfolio |

Do not make the Linux installation a prerequisite for understanding M00. Conversely, do not grant C4 for a screenshot of a DAG definition without a real task run.

## Unseen variants
Public exercises are deliberately visible. For assessment, the coach should generate a new small fixture or failure condition after reviewing the submission, keeping the published business contract unchanged. Ask the learner to predict the output, implement/test the change and explain discrepancies.

Useful variant categories include one-to-many identity edges, duplicate reasons versus duplicate members, equal timestamps, changed schema, delayed source arrival and failure after durable commit. Do not give the full answer before the learner attempts it. Hints can be progressive: clarify the contract, identify the boundary, then suggest a technique.

The coach must not pretend to execute submitted code if it has only read it. Report “reviewed,” “executed,” and “not verified” explicitly.

## Feedback and remediation
Return a score per dimension, concrete evidence supporting it, failed/missing criteria and a narrow next exercise. If the learner loses unmatched records, practice a three-row left join before assigning a larger Spark job.

After a corrected submission, reassess the failed concept with a different input. Do not award the original score automatically after the learner pastes a suggested fix.

## Retention and portfolio review
After a week, ask the learner to rebuild one transformation from its contract and diagnose a new failure. At capstone review, require a clean-checkout reproduction and a ten-minute explanation.

Portfolio claims must link to actual code, tests and artifacts. “Local mode on synthetic data” is a valid scope. “Production distributed platform” is not supported by this course alone. Passing the course does not guarantee employment or mastery of every data-engineering domain.

## Learner record
Current status: NOT ASSESSED. No checkpoint has been passed by the author on the learner's behalf.

Keep future assessment results in a private learning journal with date, checkpoint, evidence references, scores, feedback and reassessment outcome. Do not publish personal grading records automatically with the public course.
