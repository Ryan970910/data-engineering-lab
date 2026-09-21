# Turn your project into an engineering case study

## Understand the existing boundary

Your project already contains data engineering problems. It receives several kinds of records, interprets source-specific fields, cleans values, matches entities and interacts with external systems. The learning opportunity is to make these responsibilities explicit and demonstrate them in a safe, reproducible setting.

The current bulk-import entry point initializes logging, reads environment-specific configuration, creates database connectors and selects the production or development workflow. Source-specific parsing and processing are owned elsewhere. A scheduler should eventually call an explicit job interface; it should not duplicate all the ROI or Buyer processing in a DAG.

These are observations about the current code structure, not a claim that an Airflow integration already exists. Do not run the real bulk-import entry point as a course exercise: its normal path loads configuration and can interact with business systems.

## Map responsibilities, not just filenames

| Existing area | Responsibility observed | Transferable engineering concept |
|---|---|---|
| application/bulk_import.py | Environment selection and workflow entry | A parameterized job boundary |
| application/options.py | Inputs used by the central UI | Separate presentation from execution |
| sources/roi.py and buyer.py | Source parsing and owned import workflows | Source adapters and transformation contracts |
| sources/go_park.py, townplace.py, signature_home.py, buyer_form.py | Other source-specific workflows | Multiple producers with different schemas |
| infrastructure/member_api.py and member_api_dev.py | Workflow coordination and external integration | Side effects, failure propagation and environment separation |
| operations/update_member.py, merge_members.py, update_distribution.py | Specific update operations | Business commands with explicit effects |
| infrastructure/database.py and reporting/ | Data access and outputs | Storage adapters and downstream consumers |

The paths above are inside the private source package. They are reading references for the project owner. The public course deliberately does not ship those files.

A good architecture diagram shows an input boundary, a transformation boundary and a side-effect boundary. A diagram containing only boxes named after libraries tells you little about responsibility.

## Preserve the two identity contracts

The course keeps the user-specified matching boundaries:

- **ROI to Buyer:** same name and same non-empty hashed HKID.
- **ROI/Buyer to member:** same name and same non-empty phone, or same name and same non-empty email.

The teaching fixtures already contain normalized values. The lessons use blank-key exclusion and ambiguity quarantine to study quality controls. Those teaching conventions are not authorization to alter existing production behavior, address normalization, phone placeholders, email handling or any previously preserved business rule.

A hashed identity field is still sensitive in a real system. A record containing a name and contact details does not become safe to publish merely because one column is hashed. Our values such as hash-a and ada@example.invalid are fabricated.

## Worked example: ADA versus DAN

ADA's ROI and Buyer records have the same name and hash but different contact details. They can form an ROI–Buyer pair. That does not imply that both independently match the same member: each source record still uses the name-plus-contact member rule.

DAN has two member candidates. One candidate is supported by phone and another by email. Taking the first row returned by a join would turn an unresolved identity question into an arbitrary decision. In the teaching pipeline, both candidates remain visible and the source record is marked ambiguous.

The key insight is that “same person,” “same source record” and “same delivery operation” are three different claims. Each needs its own key and evidence.

## Define the safe laboratory

The supplied lab uses only synthetic CSV, JSON and a local SQLite receiver. It does not import the production package, open its configuration, call CRM or load a customer workbook. That is why you can deliberately break input schemas and simulate uncertain delivery without harming live records.

There are also limits. The demonstration uses tiny inputs, a quadratic reference matcher and one host. It simplifies authentication, API semantics, concurrency and retention. You must disclose those limits in a portfolio. A learning implementation inspired by a real workflow is useful experience; presenting it as an operated production platform would be inaccurate.

## Guided lab: a source-to-consumer map

Draw six boxes: source arrival, input snapshot, transformation, quality gate, mock delivery and report. Connect them with arrows labelled with the artifact being passed: not simply “data,” but “snapshot path and hash” or “candidate identity edges.”

For each box, write who owns it, its input contract, what proves completion, its failure behavior and whether it has a side effect. For delivery, say explicitly that the course receiver is SQLite, not the real membership API.

## Independent challenge

Add a hypothetical new source called Events. Do not write a new copy of the whole pipeline. Describe the adapter output you would require so the existing quality and delivery stages can consume it. Include source identity, record identity, contact fields and provenance. Explain which business decisions still need approval.

## Failure investigation

An exception is caught, printed and not re-raised in a hypothetical source adapter. A scheduler sees exit code zero and starts delivery. Write the causal chain from swallowed exception to misleading success. Propose a boundary test that would detect it without contacting a real API.

<details><summary>Reasoning guide</summary>
The adapter needs an explicit success/failure contract. A failed transformation must not publish an apparently complete artifact. A subprocess wrapper should detect a nonzero exit status, and downstream tasks should depend on successful quality validation. Testing a fake adapter that intentionally raises is safer and more diagnostic than running a production job.
</details>

## Evidence to keep

Keep a responsibility map, a glossary distinguishing the three identities, and an architecture decision record: “Why the course uses an isolated receiver.” State the original project relationship without publishing private code or data. Your evidence demonstrates architectural reasoning and boundary design.
