# Understand what Spark actually does

## Why another computation engine?
Python and SQLite can comfortably handle the baseline. Spark becomes relevant when distributed processing, large joins or a shared analytical ecosystem justify the overhead. It does not automatically make small data faster. The purpose here is to learn its execution model and preserve semantics across engines.

PySpark is a Python API to Spark. Most built-in DataFrame expressions describe work executed by Spark's engine rather than a Python loop for every row. The driver builds and coordinates the plan. Executors run tasks on partitions. Local mode runs on your machine and teaches the API; it is not evidence of operating a multi-node cluster.

A partition is a portion of a distributed dataset processed by tasks. A task is not the same thing as an Airflow task: one Airflow task may launch a Spark job containing many Spark tasks.

## Lazy transformations and actions
select, filter and join normally build a plan. They do not necessarily execute all computation immediately. Actions such as count, collect and writing output trigger work. Timing only a transformation can misleadingly report a fast “job” that did not run.

A DataFrame has named columns and a schema. Explicit schemas are especially important for empty fixtures and columns containing only nulls. Type inference on one convenient sample is not a durable data contract.

## Guided lab: a small executable probe
In Ubuntu, activate the Spark environment from M12. Save this as .learning-runtime/spark_probe.py and run it with that environment's python:

~~~python
from pyspark.sql import SparkSession, functions as F

spark = (
    SparkSession.builder.master("local[2]")
    .appName("course-probe")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)
try:
    records = spark.createDataFrame(
        [("R1", "ADA", "100"), ("R2", "BOB", None), ("R3", "CARA", "")],
        "id string, name string, phone string",
    )
    usable = records.filter(
        F.col("phone").isNotNull() & (F.col("phone") != "")
    ).select("id", "phone")
    records.printSchema()
    usable.explain("formatted")
    usable.show()
    print("usable_count", usable.count())
finally:
    spark.stop()
~~~

Predict one usable row, R1, before running. Record spark.version in your own copy. Successful output verifies more than importing pyspark: the JVM started and an action ran.

show is appropriate for this tiny synthetic probe. Do not print private records in production logs. collect transfers all selected rows to driver memory; an unbounded collect can exhaust it.

## Missing values and expressions
Spark SQL has null semantics. A comparison with null does not become true in an ordinary equality join. Empty string and null are different values. For our contract, exclude both from usable contact keys.

Use column expressions with &, | and parentheses. Python's and/or operators do not combine Spark Columns as intended. F.col("name") refers to a column; F.lit("roi") creates a literal value. Read each API's contract.

Prefer built-in functions over Python UDFs when they express the operation. UDFs may add serialization costs and hide optimization opportunities. They are not always wrong; choose based on capability and measurement.

## Independent challenge
Create an explicit-schema DataFrame with zero rows and prove that selecting and filtering it still work. Add a numeric-looking phone with a leading zero and show that a string schema preserves it.

Create two DataFrames with the same fields in different column orders. Compare union with unionByName using a tiny fixture. Explain why matching by position can silently corrupt data and why deduplication is separate.

Add a groupBy count by name. Compare its plan with the simple filter plan and identify where movement may appear. Save the plan, not only the final count.

## Failure investigation
A notebook times df.join(other, condition) and reports a huge speedup over Python. It never calls an action. Correct the experiment, including warm-up and equal output work. If Java fails to launch, inspect Java version, JAVA_HOME and the selected environment before changing matching code.

<details><summary>Reasoning guide</summary>
Building a plan and executing it are different measurements. Repeated actions can recompute an uncached plan. Local mode still exercises the JVM and scheduler but does not create independent networked executor machines.
</details>

## Evidence and sources
Submit the probe output, schema, empty-input test, union comparison and an annotated plan. State “Spark local mode” accurately.

Read the official [PySpark DataFrame quickstart](https://spark.apache.org/docs/4.0.1/api/python/getting_started/quickstart_df.html) and [Spark cluster overview](https://spark.apache.org/docs/4.0.1/cluster-overview.html).
