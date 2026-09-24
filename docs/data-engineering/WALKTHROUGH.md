# Statement-by-statement: the fictional case lab

Read [the tool decisions](CASES.md) first. The functions below have invented public
contracts. Their simplicity makes it possible to predict every output and compare
engines without access to a private application. They are not anonymized customer
records and not a claim of business-rule equivalence.

## Python reference: case_lab/stages.py

### Interest answers — Python first

Spark is optional only after batch measurements; Airflow is useful only for a
recurring parent workflow. `interest_answers(text)` consists of one return:

```python
return sorted(set((text or "").lower().split()))
```

`text or ""` provides empty input for None/empty text. `lower` makes this teaching
contract case-insensitive. `split` divides on whitespace. `set` removes duplicates.
`sorted` turns the unordered set into stable lexical order. The returned object
is a list, not a serialized API answer. Predict `"B a b"` before running it.

### Retained members — SQL/Python first, Spark conditional

A large reconciliation may justify a window; a filtered twenty-row report does
not. The empty `selected` dictionary records each key's first winner. `sorted`
orders by canonical ISO `joined` date and then ID. `setdefault` inserts only when
the name is absent. `list(selected.values())` exposes the winners. Name is the
invented grouping key for this lesson, **not a safe universal identity key**.

The function does not mutate the caller's list or row dictionaries. It keeps row
objects, so callers should not mutate a winner accidentally afterwards. Exercise:
replace name grouping with an explicit fictional household ID and update tests.

### Event signup — a column-expression comparison, not a Spark requirement

The function returns `{**row, "eligible": ...}`. `**row` copies the input fields.
`row["age"] >= 18` and `row["consent"] is True` implement the invented contract.
`is True` deliberately requires a boolean, not the string `"Y"`. Input schema is
part of correctness; do not loosen it silently while comparing Python and Spark.

### Residency signup — keep simple normalization in Python

The returned dictionary copies the input. `strip().upper()` standardizes the
fictional unit text. `not bool(row["email"])` identifies an empty email for review.
This does not validate email syntax or deliver a membership. A scheduler does not
make this transformation more correct. Add validation only as an explicit new rule.

### Lease signup — ordinary date arithmetic

`date.fromisoformat` parses each ISO date and raises on malformed input. The `if`
checks whether end precedes start; `raise` rejects it instead of computing negative
duration. The returned dictionary adds `(end - start).days`. Equal dates produce
zero. Leap days are handled by date arithmetic, not a hardcoded month-length table.
An Airflow task may coordinate this in a recurring feed; Spark is not necessary.

### Form candidates — measure the join before choosing Spark

The list comprehension visits every form/member pair. The first condition requires
equal names. The grouped second condition allows either equal nonblank phones or
equal nonblank emails. The result contains form ID/member ID tuples, retaining all
candidate identities; it does not silently choose one member. Boolean guards stop
blank-to-blank matches. The O(forms × members) reference is intentionally tiny;
use it for correctness fixtures, not a half-million-row benchmark baseline.

### Missing units — a set or SQL anti join is often enough

`set(expected) - set(observed)` gives expected keys absent from observations.
`sorted` stabilizes output. Set semantics remove duplicates by definition. A
multiset report would be a different contract; explain which your business needs
before replacing this with Spark `left_anti` plus `distinct`.

### File plan — no Spark

Start an empty result list. Sort the names to make selection order explicit.
`PurePosixPath` manipulates path text without touching the filesystem. The guard
requires a simple basename ending in `.csv`, rejecting directory traversal.
Append only a source/destination dictionary and return all proposed operations.
Nothing copies a file. An Airflow retry can safely reconstruct the same plan;
executing those copies would require a separate policy and verification step.

### Flatten answers — Python for modest nested responses

The comprehension visits each record and each key/value in its `answers` mapping.
Each output retains its record ID along with the question and answer. An empty
answer mapping contributes no rows. This is a one-to-many operation, so row-count
growth is expected. Do not make HTTP requests inside this transform; extraction
and transformation have different failure/retry concerns.

### Name score — ordinary Python, with an explicit denominator

An empty right list returns zero, avoiding division by zero. Each `Counter` counts
casefolded words. Counter intersection takes the smaller count of each shared
word, so one right-hand occurrence cannot match unlimited left occurrences.
Sum the overlap counts and divide by the **right** length. This score is asymmetric
and is not identity proof. A set intersection loses repeated-word information.

### Monthly list — a good scheduling example, not necessarily a Spark job

`run_date.replace(day=1)` gives the exclusive end of the previous month. Subtract
one day to enter that month, then replace its day with 1 to get the inclusive
start. Parse each submission date and retain `start <= submitted < end`. Keeping
the business date explicit enables reproducible reruns. A task run on a later day
must not silently change the reporting period by reading a new wall clock.

### Handover cells — Python/pandas reshape first

For each floor row, iterate the `units` dictionary. Create a long row containing
floor, unit and date value. A value of None remains None; it does not cause the
row to disappear. The adapter deciding which grid cells exist is therefore part
of the contract. Spark cannot recover blank cells discarded before ingestion.

### Writing entry — three-field parsing does not need a cluster

`split("|")` retains positional text. The length check requires exactly three
parts; fewer or extra delimiters raise instead of shifting fields silently.
`zip` pairs the three literal headings with the parts. `dict` returns the named
record. A delimiter inside a story is currently invalid; designing escaping is a
separate schema change, not something to conceal in a migration.

### Reference expansion — Python baseline, optional Spark explode

For each row, split its references on commas. Strip surrounding whitespace from
each token. The filter skips empty tokens. Create one output per nonempty token,
retaining the parent ID. Duplicate references remain duplicates. This is an
artifact transform; it does not update a database row for every expanded value.

## Spark comparisons: case_lab/spark_stages.py

### Why these five operations?

Registration compares column predicates; retained compares ordered windows;
candidates compares relational joins; missing compares anti joins; references
compares explode. These illustrate actual distributed-table mechanisms. The
other tiny functions stay in Python: a technical portfolio should show judgment,
not a requirement to rewrite every line using Spark.

### registration

The local import leaves this module importable without Spark until a Spark
function is called. `F.col` constructs a column expression, not one row's value.
`&` combines predicates for each row. `withColumn` returns a new plan with eligible.
The fixture contract uses non-null integer ages and boolean consent; define null
behavior explicitly before adding nullable inputs. No action has executed yet.

### retained

`Window.partitionBy("name")` defines winner groups. `orderBy("joined", "id")`
pins a total order for fixture rows. `row_number().over(order)` numbers each group.
Keep rank 1 and drop the temporary rank. Spark duplicate removal alone does not
promise which record wins. Sorting the output when comparing engines is separate
from choosing the correct survivor within a group.

### candidates

Alias forms as `f` and members as `m` to distinguish identically named fields.
Build the guarded phone and email conditions separately, then combine them with
equal names. Join all matches and project only the two renamed identity fields.
This preserves ambiguity for inspection instead of choosing a convenient winner.
Null equality is not true in SQL; combined with nonblank guards, null contact keys
do not produce candidates in this teaching contract.

### missing

`left_anti` returns expected rows with no observed unit key. `distinct` aligns the
Spark output with the Python reference's set contract. Removing it would preserve
duplicate missing rows and no longer be the same exercise. This is an opportunity
to discuss semantics, not merely optimize an execution plan.

### references

`split` creates an array, `explode` emits one row for each array element, and
`withColumn` carries original columns along. The next expression trims each token.
Filter out empty text, then project the parent ID and reference. A write/collect
action is needed to run this plan. Merely importing the module proves no runtime.

## Orchestration: case_lab/dag.py

**Why Airflow here?** To learn explicit task dependencies and failure propagation.
For one manual Python run it is unnecessary; it becomes useful for recurring,
unattended flows. This demonstration intentionally does not require Spark.

The imports select a timezone-aware date and Airflow's public decorators. `@dag`
declares no schedule, disables historical catch-up and allows one active run.
`fictional_cases` builds the task graph. The first `@task(retries=0)` defines
`transform`; its runtime import calls the Python demo and returns one evidence path.

The second task reads that JSON. It checks synthetic-only and false production
parity markers, raises on violation, then returns only case count and engine.
`inspect(transform())` connects the tasks through the first task's output.
The final `fictional_cases()` registers the DAG; it does not trigger it.

There is no database/API/file-copy delivery task. Both tasks must see the same
local filesystem. A scheduler running successfully does not certify distributed
storage, production delivery or business equivalence.

## Execution evidence: case_lab/demo.py and tests

`demo.run` constructs fictional dictionaries and invokes all fourteen Python
references. Its output dictionary names each case. A UUID chooses a new private
scratch directory, preventing accidental overwrite. JSON records `engine: python`,
`synthetic_only: true`, and `production_parity: false`, then the CLI prints its path.

The tests use hand-authored expectations, malformed input and an actual demo run.
The Spark test creates a real session and calls real actions only when installed.
The Airflow test imports a real DagBag only when installed. Missing dependencies
are reported as skipped; installed-but-broken runtimes fail rather than pretending
to pass. Neither author checks nor reading this walkthrough proves learner mastery.

## Your independent assessment

Choose one case where Spark is not justified and defend that decision. Then choose
one join case, draw its input/output grain, add duplicate and missing-key fixtures,
predict full output tuples and run your tests. Finally introduce a bug deliberately
and show the test catching it. Submit code, outputs and reasoning, not just a green
check mark. Runtime exercises remain deferred until you choose to enable them.
