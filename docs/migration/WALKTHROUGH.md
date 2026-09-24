# Read the actual migration code, statement by statement

Each bullet explains the next executable statement, continued expression or declaration in the named real module. Open the source beside this guide. Numeric line references have been removed so later comments do not point at the wrong line; blank lines and closing brackets are not separate operations.

Read README.md for incomplete workflow boundaries. These are real partial ports, not fictional replacement rules or production-ready workflows. Every module starts with tool fit.

## 1. ROI: preserve the surprisingly important details

**Tool choice first:** keep Python/pandas today; no bottleneck is measured. Airflow
helps recurring extraction/validation/delivery coordination. Spark becomes a
candidate for large historical reprocessing or joins, not merely questionnaire
strings. At the reported 500,000-record scale, measure helper cost and actual batch
scope. This port is an optional comparison exercise; see README.md.

File: `src/club_migration/roi.py`.
Legacy references: `ROIBulkImportMixin.main_roi_data_parser`,
`roi_mapping.clean_question_column`, `clean_properties_preference_column`.

Input example: Q1=`3+1+3`, Q2=`2.0`, property preference=`1 3.9`.
The new stage maps columns and returns Q1=`1+3`, property count=3. Q2 depends on
**every row in the batch**, not just that row. It is not yet an uploadable ROI record.

- Import Python regular expressions for identifying questionnaire column names. This checks schema names on the driver, not every data row.
- Use the approved template and mapping from the independent contracts module. Keep these declarations aligned with the pinned legacy baseline.
- Define a pure value parser that can run in a normal Python test or as a Spark UDF.
- Convert the value to text, turn `+` into whitespace, split using Python whitespace rules, remove repeated tokens, sort lexically, then join with `+`. Thus `10+2` stays `10+2`, not numeric order.
- Start the optional numeric conversion attempt. Failure must be recorded rather than abort this entire value parser.
- Match the old `int(float(text))` conversion. `2.9` becomes `2`; empty text and the literal `nan` bypass conversion.
- Return original normalized text, numeric candidate and a false failure flag. A tuple becomes a typed Spark struct later.
- Conversion failures return the original text and a true flag. The caller can preserve the old whole-column fallback.
- Parse every property-count token through float then int and select the maximum. This deliberately raises for empty/bad tokens; inventing a default would alter business behavior.
- Define field projection and import Spark only when needed. Ordinary Python tests do not require Spark to import this module. The input must already have passed the A_BLOCK swap.
- Start with template order, then append mapped fields actually present in the source. `dict.fromkeys` removes duplicate names without sorting them. Column order later determines questionnaire array order.
- Prepare a list of Spark expressions, not a list of output records.
- Visit each output column once on the driver. This loop is over a small schema, not over potentially millions of rows.
- Find that output column's real source name. The mapping preserves misspellings such as `APPLICANTION_DATE`.
- Refer to an existing source column or create an empty literal when the field is absent.
- Establish the stage's string contract, replace null with empty text, and assign the output name. This is a review-stage representation, not proof of full legacy payload type parity.
- Return the projected table while retaining the original row-order ID for comparison.
- Define questionnaire processing independently from field projection so it can be tested with a small prepared table.
- Match a single digit, case-insensitively, just like the old regex. `Questionnaire_Answer10` is deliberately excluded. Keep the incoming column order.
- Wrap the Python parser as a Spark UDF with an explicit result schema. Spark must know that `invalid` is boolean and the other two members are strings.
- For each answer column, attach a temporary struct containing the parser's three results for every row.
- Apply numeric conversion only to the exact mixed-case name `Questionnaire_Answer2`. The legacy branch itself is case-sensitive even though column selection is not.
- Aggregate failure flags across the entire DataFrame. Maximum 1 means at least one row failed conversion. This is a global dependency.
- Join the one-row aggregate back to every row. If any conversion failed, use original normalized text for the whole column; otherwise use converted values. Remove the aggregate flag afterward.
- Other questionnaire columns use normalized text, not numeric conversion.
- Remove the temporary parsing struct before processing the next column.
- Build the ordered answer array. Preserve the existing output spelling `questionAnswsers`; changing it here would break a downstream contract.
- Expose one stage function. Its description explicitly says this is a review artifact, not a full importer.
- Apply actual production field names.
- Declare the property-count UDF's integer result type. Spark `long` is bounded; unusually large Python integers need a future contract decision.
- Replace the property-count column with computed values. This is a transformation, not immediate execution.
- Return the questionnaire-processed plan. Writing or collecting it will execute the plan.

Why not normalize Answer2 row by row? With `['2.0', '3+1']`, the old pandas
assignment fails on the second item and leaves **both** normalized values unchanged.
A naive Spark per-row `try_cast` would produce a different first value. That is
why there is an aggregate and a one-row cross join instead of a simpler expression.

The UDF preserves Python token and float semantics. It is not claimed to be the
fastest possible implementation. First establish equivalence; measure before
replacing it with native expressions that may treat Unicode whitespace or infinities
differently.

## 2. Buyer: actual retained/terminated report processing

**Tool choice first:** this is a meaningful Spark candidate because its work is
joins, ordered selection and date rules. But the old database query already filters
to requested serials; SQL plus pandas may remain simpler even with 500,000 total
members. Measure the selected rows, duplicate multiplication and memory before
adoption. Airflow helps recurring snapshot/report dependencies, not one-off UI use.

File: `src/club_migration/buyer.py`.
Legacy references: production `BuyerBulkImportMixin.map_source_to_output`,
`build_retained_dataframe`, `fill_template_with_data` and `run_buyer_import`.
This is **not** the separate `main_buyer_data_parser` ROI-matching path.

- Import one shared literal contract. The independent contracts module preserves the actual values without importing a production service module.
- Define the two-join transformation. The function receives DataFrames, not database connectors.
- Take the three report identifiers plus source order. Do not carry arbitrary error-report columns into the join.
- Separate the serial-number join key from fields that need retained/terminated suffixes.
- Describe two passes: look up the retained member, then the terminated member.
- Give the right serial key a temporary name to avoid accidental column collisions. Canonical string serials are an input requirement.
- Preserve member-source order separately for each join. One error row can match multiple source rows.
- Suffix each member attribute so that the two members' data remain distinguishable.
- Perform a left join: preserve the error record even if no member matches. Null-safe equality is explicit; snapshots must preserve legacy stringification before this point. Drop the temporary key.
- Return the joined table without deduplicating it prematurely.
- Start the retained-record rules; do not perform extraction or delivery.
- Convert each paired date to timestamp, with invalid canonical values becoming null. This corresponds to coercion, but raw ambiguous date strings still require an adapter.
- Define a reusable column expression: null becomes empty text, surrounding ASCII spaces are trimmed. This is used only for rule evaluation; it does not blanket-rewrite all outputs.
- Read the retained activation status without uppercasing it. The blocked values have exact case.
- Convert the verify-email flag to uppercase and test for `Y`.
- Do the same for valid-mobile.
- Do the same for valid-email. These are separate flags with separate downstream uses.
- Uppercase both distribution strings as the old code does.
- Test activation status against the existing blocked list.
- Keep the old mixed-case rewards regex even though the input was uppercased. This apparently odd behavior is a preserved rule, not silently repaired during migration.
- Keep the literal `.*ROI*` regex. `I*` means zero or more I characters; it is not equivalent to “contains the substring ROI.”
- Build the additional email-transfer condition separately from mobile transfer.
- Combine the mobile-denial conditions with Spark's bitwise predicate operators. Python `or` would try to evaluate a Column as one boolean and fail.
- Write `N` for denied mobile transfer and `Y` otherwise.
- Write email transfer using the mobile-denial conditions plus the email-specific condition.
- Preserve the old date comparison exactly: replace when retained membership starts later than terminated membership. Do not trust the misleading constant name instead of the expression.
- Replace all configured retained attributes from the terminated member under that mask. A single `withColumns` expresses simultaneous replacements.
- For each date base, take the earlier non-null timestamp. Spark `least` skips null operands; if both are null the result is null.
- Keep comparison/order metadata and the report identifiers.
- Declare report attribute order exactly, independently from member-source column order. A report schema is part of its contract.
- Drop terminated attributes that are no longer part of the final report, keeping transfer flags.
- Define explicit “keep first” semantics with a window, rather than relying on Spark's arbitrary duplicate survivor.
- Sort ties by original error row, retained source row and terminated source row. Null-first ordering is explicit.
- Number rows separately for each duplicate key group.
- Keep rank 1 and remove the helper rank. This does not promise physical output-file ordering.
- Define template projection. Ordered template column names are passed in; the function does not open a hardcoded workbook.
- Keep the first row for each retained serial, matching template deduplication.
- Reverse source-to-template mapping so each requested template column can find its source.
- Build expressions in template order.
- Use the mapped source name, or the same name when no rename is configured.
- Provide a typed null for an absent template column instead of omitting that column.
- Format only configured date columns as `dd-MM-yyyy`. This is presentation formatting, after timestamp comparisons.
- Assign each template heading, including headings containing spaces.
- Return the ordered template plus `_row_id` for offline traceability. The extra ID is not a production upload field.
- Expose the stage pipeline.
- Retain only errors with a non-null, nonempty termination ID, as the production branch does.
- Join member snapshots twice.
- Apply retained-record rules, then keep the first termination ID. Deduplication happens after rule evaluation.
- Return both the retained report and template view. No database, email or API write follows.

The extra order columns are migration evidence, not business fields. For comparison,
sort explicitly, compare selected business columns and row multiplicities, then
remove metadata only at a separately validated output boundary.

The old Buyer source refers to constants defined in the service module rather
than locally importing them. The isolated old-function tests inject those literal
constants to characterize rule behavior; that is **not** evidence that the entire
old Buyer menu entry runs successfully. This migration does not claim to repair it.

## 3. Shared registration expressions

**Tool choice first:** a shared helper needs neither its own DAG nor a separate
Spark job. It returns expressions to a caller that has independently justified its
engine. Reuse common rules without forcing every registration source onto Spark.

File: `src/club_migration/registration.py`.

- Reuse the real ordered age mapping instead of maintaining three copies.
- Accept a Spark date expression and an explicit year. A rerun should not silently use a different wall-clock year.
- Compute year difference, not birthday-aware age, because that is the existing rule.
- Start with unknown age group 0.
- Visit mapping entries backwards while nesting `when` expressions. The earliest original entry becomes the outermost branch and therefore wins first.
- Parse an inclusive range such as `62-65`. This is driver-side processing of configuration.
- Wrap the previous expression with a range test.
- Handle the open-ended 65-or-above entry. The prior `62-65` branch still wins at age 65.
- Return an expression, not a DataFrame or a computed scalar.
- Define only the STAR fields actually shared by Townplace and Signature Home.
- Set STAR membership and map room to starFlat.
- Map floor and block to STAR-specific field names.
- Set the three shared literals: English address language, Hong Kong, verification Y. Source-specific validation remains outside this helper.

### Go Park

**Tool choice first:** prefer Python/pandas for a registration workbook. Airflow is
conditional on recurring input/validation/delivery. Spark needs measured bulk
history or join pressure; title, age and consent checks alone do not justify it.

File: `src/club_migration/go_park.py`.

- Reuse title constants and the shared age expression, not another source's complete processing function.
- Require prepared names, phones and districts. This is a deliberately explicit partial-migration boundary.
- Construct a Spark map literal by flattening key/value pairs into alternating literal expressions.
- Look up the raw title. Unknown values become null. Unlike Townplace, this rule does not call uppercase first.
- Define conversion of the canonical DOB string to a date.
- Execute a small existence check for invalid dates and fail clearly. This is a snapshot contract check, not a newly invented age rule.
- Apply the ordered year-based age mapping.
- Assign General membership `G`, not STAR `S`.
- Assign English address language.
- Assign call verification flag Y.
- Replace missing consent with empty text and retain that normalized field.
- Begin an ordered list of optional error expressions.
- Add the date-of-birth error only for age group -1.
- Add a name error for explicitly false name validation. Null is not automatically false.
- Add the consent error only for N or empty, with the original capitalization and wording.
- Add the missing-mobile error only when both invalid-mobile and mobile are null. Empty text is different from null.
- Join non-null reasons with `+` in that order and remove the helper validation field. It does not send the old rejection email or exit the process.

### Townplace

**Tool choice first:** keep Python/pandas unless large repeated batches justify
distribution. Airflow can coordinate recurring imports. Measure family-field and
name/address processing before assuming a Spark UDF improves throughput.

File: `src/club_migration/townplace.py`.

- Import only genuinely shared expressions.
- Accept already-prepared fields and an explicit year.
- Compute the common age classification from a canonical date.
- Add STAR fields, then change under-18 group -1 to 0. This source-specific exception must not leak into Go Park.
- Start ordered remarks and retain the old age check, even though the preceding rule generally prevents -1.
- Add the explicit false-name error.
- Add the error only when both mobile fields are null.
- Add missing-email only for empty text, not every possible missing representation.
- Join reasons and remove the two legacy temporary columns. Spark drop tolerates a missing helper column in this prepared-stage contract.

### Signature Home

**Tool choice first:** retain Python/pandas for current workbook processing until
measured otherwise. Airflow can coordinate recurring stages; Spark requires evidence
that address/name resource loading and serialization do not outweigh its benefit.

File: `src/club_migration/signature_home.py`.

- Reuse age and STAR-field expressions.
- Define the prepared-data stage.
- Add STAR fields and retain the common age group without Townplace's under-18 rewrite.
- Start reasons and append the under-18 date error.
- Append invalid English name. There is no Go Park consent rule here.
- Join reasons and remove `name validation` and `name_pre_check`.

## 4. Loving Home: a real wide-row parser

**Tool choice first:** pandas is the current recommendation. Splitting one workbook's
DETAILS strings is not a distributed-computing requirement. Airflow is useful only
for recurring pipeline dependencies. The Spark version is an optional learning
comparison, not a mandatory architectural upgrade.

File: `src/club_migration/loving_home.py`.
Legacy reference: the entire transformation section of `tools/loving_home.py`,
including its positional `split_details` function. Excel I/O is not yet migrated.

- Declare the 28 positional output names in the exact old order, including `Intermediate Attengind` and the quoted 2025 label. Each tuple index corresponds to the same `%`-separated position in DETAILS.
- Receive a typed table rather than opening the UI or workbook.
- Require an explicit private list of integer exception IDs and validate its type. Real record IDs are not embedded in public code. Membership in the supplied list controls the same exception rule.
- Build a new projection across all original fields.
- Apply text replacements only to string fields; numeric fields stay numeric.
- Replace each newline or carriage return with a space. CRLF therefore contains two replacement positions, as in the old regex.
- Remove literal spaces only on rows selected by the supplied private exception IDs. Other rows keep their spaces.
- Replace the specific Chinese percentage pattern before splitting on `%`. Java replacement syntax uses `$1` for the captured digits.
- Replace `100%` with its original Chinese text. Otherwise its percent sign could be mistaken for a field delimiter.
- Keep each original name and apply the replacements together.
- Split DETAILS on `%`, retaining trailing empty fields using a negative limit. A final empty slot is meaningful.
- Reject non-null strings with fewer than 28 fields. The old positional parser also fails; silently padding would hide malformed input.
- Extract each position into its named column with zero-based `get`. Null DETAILS produces null extracted values under this stage's string/null contract.
- Add `file name` only if at least one row has exactly 29 parts. A row with 30 parts does not qualify, preserving the old branch.
- Return the expanded table; leave workbook formatting and filename timestamps to a future adapter.

For example, `remaining 100%` cannot be naively split before replacement. Think of
delimiters as a data contract, not merely a convenient string method. The numeric
ID exception and misspelled headings remain because this is a migration, not a
business cleanup.

## 5. Handover: replace nested cell loops with relational joins

**Tool choice first:** prefer Python/pandas for one Excel grid; Spark still needs an
Excel adapter and adds runtime overhead. Airflow is optional when file arrival and
downstream processing must be automated. This Spark version teaches relational
unpivoting, not a proven production performance improvement.

File: `src/club_migration/handover.py`.
The future Excel adapter must include blank cells, not just populated cells. Each
cell has sheet order, sheet name, row, column and a canonical string/null value.

- Define a transformation over cells, independent of Excel's Python library.
- Search only header row zero and columns from index two onward, as the original loop does.
- Select header cells beginning with `Flat` and keep their coordinates.
- Extract text after `Flat `. If the label begins with Flat but does not match the spaced pattern, output null rather than an invented flat.
- Find floor labels in column zero, excluding the header.
- Extract the floor before `/F`, retaining null for unmatched labels.
- Select data rows.
- Join each body cell to its flat header and its row's floor. Sheet order and sheet name stop identically numbered cells from different sheets matching.
- Retain coordinates for deterministic comparison plus the extracted flat and floor.
- Convert null date cells to empty text, trim surrounding spaces, and rename sheet to block. No date parsing is invented.

The output can be sorted by `sheet_order`, `row`, `col` to reproduce the original
nested-loop order. Dropping blank input cells would incorrectly delete output rows.

## 6. Move-in: unmatched units, with deliberate null behavior

**Tool choice first:** compare a database anti join and pandas first. Spark is a
candidate for large portfolio reconciliations, not automatically for one building.
Airflow can coordinate recurring consistent snapshots and exception reports.

File: `src/club_migration/move_in.py`.
This ports the first comparison report, **not** the later missing-membership report.

- Receive the two snapshots; import `reduce`, logical conjunction and Spark expressions.
- Define the common block/floor/flat key names in positional order.
- Build the same normalization for each source's differently named key columns.
- Under the documented NaN-normalized snapshot contract, convert values to uppercase, trimmed strings; a null first becomes the literal `nan`.
- Convert normalized `NAN` back to a SQL null. Other literal strings remain strings.
- Store both normalized source fields and common keys; return the new table.
- Map collection Tower/Floor/Unit to common keys.
- Map registered HANDOVER_BLOCK/FLOOR/FLAT to the same keys.
- AND together three null-safe equalities. Ordinary SQL equality would not match two null keys the way the legacy pandas merge can.
- Return left-only and right-only rows using anti joins. Matching rows are unnecessary for these two reports, so a full outer table would be wasted intermediate work.

An anti join answers “which left rows have no matching right row?” It does not
deduplicate left rows. Two unmatched collection rows remain two rows.

## 7. Buyer form: oldest member and contact precedence

**Tool choice first:** large member/form joins make this a Spark candidate, but
source-side filtering or SQL windows may be simpler. About 500,000 total members
does not mean every form job needs a full export. Airflow helps recurring snapshot
and reconciliation dependencies; it is unnecessary for a small interactive lookup.

File: `src/club_migration/buyer_form.py`.
Legacy reference: `tools/buyer_form_check.record_matching`.
Names and contact hashes are already prepared; this code never handles raw HKID.

- Define a transformation taking member and form tables. Windows specify deterministic winner selection.
- Declare the exact fields copied from a matched member into a form.
- Put those fields into one struct. This keeps one matched member's values together, even if individual fields are null.
- Turn each member's mobile and email into two contact rows while preserving name, membership date, source order and payload. The legacy dictionary uses one common contact-key namespace, so this does too.
- Group by name plus contact; sort oldest membership first and original row order second. The date snapshot must be valid, canonical and comparable.
- Keep the first member for each contact key. This represents the old dictionary's first insertion, not arbitrary deduplication.
- Start from every form, including forms without a match.
- Look up mobile first, then email, using separately named candidate structs.
- Rename lookup keys to avoid collisions with form columns.
- Require both name and contact to match, with explicit null semantics. No name-only matching is introduced.
- Left-join candidates and remove temporary lookup keys.
- Prefer the complete mobile candidate over the complete email candidate. Do not mix attributes from two members by coalescing individual fields.
- Fill only when the existing serial is null and a candidate exists. An empty-string serial is not automatically null.
- Copy all matched fields under the same condition, preserving existing form values otherwise.
- Drop the two internal candidate structs.

If mobile points to a member who joined in 2021 and email points to one who joined
in 2020, **mobile still wins**. “Oldest first” chooses within each lookup key;
it does not override the outer mobile-before-email rule.

## 8. The Point name score

**Tool choice first:** keep Python for a small set of name pairs. A large candidate
join may justify Spark after filtering, but the score UDF alone does not. Airflow
is conditional on repeated batch reconciliation, not on this function's existence.

File: `src/club_migration/the_point_check.py`.
Legacy reference: `tools/the_point_check.calculate_match_rate`.

- Import the standard-library Counter; no extra matching library is required.
- Return zero for missing, non-list or empty segment sequences, matching the old guard.
- Count uppercase syllables and take the multiset intersection. A buyer's one CHAN cannot match two CHAN occurrences.
- Divide by the buyer segment count, not the applicant count. The metric is asymmetric.
- Define a stage on already-segmented pairs, not on raw workbooks.
- Wrap the real score as a double-valued UDF.
- Attach the score without discarding the input pair. The stage does not yet reproduce the full legacy report's long column names and join logic.

This is not fuzzy string matching or identity proof. It is the project's specific
syllable-overlap metric. Separate matching and interpretation from score calculation.

## 9. The Point half-month list

**Tool choice first:** Airflow is a promising fit for the existing twice-monthly
business window, after readiness and delivery rules are confirmed. Spark is not
automatically needed for workbook filtering and hashing; compare SQL/pandas first.

File: `src/club_migration/the_point_list.py`.

- Use standard hashing and calendar arithmetic; no scheduler state is hidden here.
- Anchor the requested run date at local midnight. This makes replay explicit.
- On the 16th, select from this month's first midnight through the 15th at 23:59:59.
- On the 1st, find the preceding month's last second, then start at its 16th midnight. Leap years and year changes follow calendar arithmetic.
- Reject every other day. The legacy code never defined start/end values there; the migration does not invent another period.
- Convert mobile text to an integer inside the compatibility hash function.
- Preserve the exact multiply/add/divide/`int` sequence, including Python floating-point division. Algebraically simplifying it could change very large-number behavior.
- UTF-8 encode the resulting decimal string, hash it with SHA-256, and return lowercase hexadecimal. This is compatibility processing, not encryption.
- Return the original/final intermediate value for the same ordinary conversion failures instead of fabricating a hash.
- Begin the table transform and obtain explicit period boundaries.
- Convert the two ISO timestamps and choose the latest non-null one.
- Include both boundary timestamps, matching the old inclusive selection. Fractional seconds after 23:59:59 are outside that legacy interval.
- Concatenate country code and mobile strings. Snapshot null becomes literal `nan` to match the specified pandas stringification boundary. This intentionally does not validate the mobile.
- Keep the member-number expression for several decisions.
- Select a requested mobile invitation only when membership is null/empty, choice is Y and URL-send flag is N.
- Preserve the old alternative that a non-null member number permits the concatenated mobile. An empty string is still non-null at this step.
- Set gold eligibility only when both terms consent and owner are Y.
- Project the report columns; normalize null member number to empty text for the following cleanup.
- Compute the compatibility mobile hash using a Spark UDF.
- Replace empty strings with null after the prior conditions, not before them. Reordering changes behavior.
- Drop a row only when both member number and mobile are absent.

The migration assumes dates have already been normalized from the old day-first
workbook representation. Spark timestamp casting alone is not a substitute for
the full pandas day-first parser.

## 10. Export ROI questionnaire responses

**Tool choice first:** Python is the default for API extraction and modest response
flattening. Airflow can manage recurring extraction dependencies. Spark is optional
for large landed historical datasets; do not move HTTP calls into executor UDFs.

File: `src/club_migration/export_roi.py`.
Legacy reference: `tools/export_roi.process_entry`.

- Transform an offline nested-response table. No HTTP request is made.
- Use the real API spelling `anwerList`, not a corrected field name.
- Select answer structs whose sequence matches the requested question. This is a Spark higher-order array expression, not a Python loop over records.
- Take the last matching answer and its `anwer` field. The old dictionary comprehension also lets the last repeated sequence win.
- Obtain layout answer 3 for validation and later formatting.
- Fail on an empty applicant list or missing layout answer rather than silently accepting a case where the old function fails. Null/missing nested-container distinctions still need adapter characterization.
- Keep an expression for the applicant array.
- Project row identity, registration number and ballot.
- Use the first applicant's type and answer 1 for previous-property count.
- Project purchase-plan answer 2 and replace commas with pipes in layout answer 3.
- Iterate positions zero through two. Despite the legacy comment mentioning four, its real loop exports only three applicants.
- Add each applicant's sex and age using safe zero-based access; missing later applicants produce nulls.
- Return the flat table. No incremental import, database write or Excel export is claimed here.

## 11. Update ROI: only the final explosion stage

**Tool choice first:** keep transactional repairs in SQL/Python. Airflow is only
appropriate after approval, transaction and retry rules are explicit. Spark may
help large read-only snapshot expansion, not per-row database updates.

File: `src/club_migration/update_roi.py`.

- Accept a prepared processed-ROI snapshot; do not query or update Oracle.
- Split BISERIALNO on a literal space and explode it. Repeated spaces preserve empty tokens. `explode_outer` keeps a null-input row instead of silently deleting it.
- Build an output projection over the resulting schema.
- Lowercase column names and preserve the special `err_msg_raw` to `error_msg_raw` rename.
- Start with the current column expression.
- Turn the exact string `nan` into null for string fields. Floating NaN handling is still an input-adapter requirement.
- Apply the names and return the projected table. None of the preceding legacy SQL updates are executed.

## 12. Move ROI files: orchestration does not require Spark

**Tool choice first:** ordinary Python is sufficient for selection and copying.
Airflow can eventually coordinate unattended import steps, with Windows/batch and
retry constraints addressed. Spark is not appropriate for these file operations.

File: `src/club_migration/move_roi_files.py`.

- Use PureWindowsPath to manipulate Windows path text without accessing those files, even when the future worker is Linux.
- Accept an ordered metadata snapshot and begin a selection dictionary.
- Take the first record of each kind modified on the requested date. The old code uses `next`, not `max(mtime)`; “latest” in its variable name is not its actual behavior.
- Reject a missing ROI input explicitly. This is a safe planning failure, not an attempt to continue after an incomplete copy.
- Build operations in question-then-ROI order, only for kinds that exist.
- Parse the selected path as Windows path text.
- Remove the last underscore suffix from the filename stem and append `.xlsx`, matching the original filename transformation.
- Record source and proposed destination. Merely constructing this dictionary cannot copy a file.
- Return the plan for review. No batch execution, insert, commit or email exists in this function.

The plan is useful hands-on work: it teaches separation of decision and side effect.
It is not proof that the Windows import batch can run on an Airflow Linux worker.

## 13. Runner: where expressions actually execute

**Tool choice first:** ordinary Python is sufficient for validation and dispatch. Spark is invoked only for its implemented table stages; a file plan remains ordinary Python.

Open `src/club_migration/runner.py`.

- Standard-library imports provide argument parsing, dynamic module selection, JSON, pinned dates, paths and unique run IDs.
- ROOT resolves the learning checkout; WORK locates ignored runtime files. This runner is checkout-oriented, not an arbitrary installed-wheel service.
- STAGES is an explicit allowlist. It enumerates implemented slices, not complete business workflows.
- read_job resolves the manifest path before enforcing the private runtime boundary; parses JSON; rejects an unknown stage; validates the date; resolves each input; requires existing files and explicit DDL schemas.
- execute imports the selected independent module. It creates a fresh run directory and initializes evidence with delivery and parity false.
- The try/finally preserves failed-run evidence and stops an opened Spark session.
- The file-plan branch writes JSON only. It does not open, copy or rename source files.
- Other branches open a local Spark session, pin the timezone, disable its UI and locate scratch files on the approved drive.
- The reader uses supplied schemas and FAILFAST mode. Null or duplicate _row_id values are rejected to preserve traceability.
- Buyer receives members, errors and template columns; Buyer-form receives members and forms; Move-in receives two unit tables. Registration receives the pinned year and The Point the pinned date.
- Loving Home additionally requires private special_import_ids. Omission fails instead of silently changing the exception rule.
- Other implemented slices receive the data frame. The returned objects are Spark plans until an action runs.
- Parquet writes materialize those plans and reject an existing destination. Reading the output back and counting rows establishes artifact existence, not equivalent business content.
- Evidence changes to artifact-written only after all outputs finish. parity_verified remains false because this runner does not execute a full legacy comparison.
- CLI --check performs manifest validation only. Its explicit message must never be reported as a successful transformation.

## 14. Airflow: coordinate, do not replace the processing code

**Tool choice first:** the manual DAG teaches dependencies and failure propagation. Use it for repeatable unattended work, not merely because an interactive script exists. Linux execution is still pending; no successful DAG run is claimed.

Open `dags/club_migration.py`.

- datetime/timezone create an explicit aware start date; Airflow's public SDK supplies decorators and parameter types.
- @dag disables automatic schedules and catchup, allows one active run, and declares a private job-path parameter rather than embedding records.
- club_migration defines task relationships. Calling the function creates a DAG object; it does not execute a business run.
- @task(retries=0) disables automatic repetition until side effects and retry guarantees have been established.
- run_stage imports its runtime utilities inside the task so DAG parsing does not read a manifest.
- CLUB_MIGRATION_ROOT selects the independent checkout. CLUB_SPARK_PYTHON must identify an existing absolute interpreter, not a shell command.
- A private scratch directory and environment keep temporary files local and make src importable to the child.
- get_current_context reads the manually supplied manifest parameter.
- subprocess.run receives a list of arguments, checks the exit code and captures output. No shell interpolation executes manifest text.
- The task returns the final output line, a small evidence path, rather than sending a DataFrame through task metadata.
- verify_artifact reads that evidence, rejects unsuccessful artifacts or claimed production delivery, and returns both status and the explicit parity flag.
- verify_artifact(run_stage()) creates the dependency. Both workers must see the same filesystem; this is not a remote-cluster submission design.
- The final club_migration() call makes the DAG discoverable. Discovery, execution and business equivalence are three separate tests.

## 15. Validation and the real legacy reference

**Tool choice first:** ordinary Python is sufficient to compare test artifacts and launch a reference process. A second scheduler or distributed comparison framework would add no value here.

Open `validation.py`, `tests/migration/legacy_reference.py` and `test_legacy_parity.py`.

- _cell records a value's type alongside its content. Null, an empty string and a number-looking string are different; nested containers are processed recursively.
- _snapshot reads the supported artifact type. XLSX retains worksheet order, merged ranges, formulas, number formats and cells. CSV retains textual rows. Parquet retains schema and ordered records. No cross-format normalization is silently invented.
- compare rejects using the same path as both expected and actual, reads both artifacts, checks structure and every row, and reports differences without dumping customer cell values.
- The report contains content digests and explicitly sets full_workflow_verified to false. Equal supplied outputs do not prove that an incomplete input adapter or missing workflow branch exists.
- The CLI restricts reports to ignored runtime storage and exits nonzero on a mismatch.
- legacy_reference parses the real source AST and selects only the named pure Buyer methods and ROI helper. It never executes production module imports, database queries or UI initialization.
- The reference receives synthetic inputs, creates the same template structure and returns the complete selected functions' outputs and actual pandas version.
- The differential test removes Spark bootstrap overrides from the reference subprocess, preserving the original interpreter's dependencies.
- The Spark side runs actual joins/UDFs, sorts explicit comparison IDs and excludes only documented internal order metadata. It compares every remaining column and value with the reference, not just a few handpicked cells.
- The strict PowerShell runner fails on errors, failures OR skips and records the limitations in evidence.json.
