"""Learner exercise: implement build_pairs, then run the public test cases."""
import argparse
import json
from pathlib import Path
from lab import SAMPLES, FIELDS, reference

def build_pairs(spark, batch):
    """Return two Spark DataFrames, not lists.

    roi_buyer columns: roi_id, buyer_id (strings).
    member_candidates columns: source, record_id, member_id (strings).

    Use explicit schema, non-empty-key guards, joins, select, unionByName and
    dropDuplicates on identity columns. Do not call collect/toPandas/reference
    inside your implementation. The fixtures are already normalized.
    """
    raise NotImplementedError("Complete build_pairs before requesting the Spark checkpoint")

def exercise_cases():
    base = {name: [dict(zip(FIELDS, row)) for row in rows] for name, rows in SAMPLES.items()}
    yield "baseline", base
    changed = json.loads(json.dumps(base))
    changed["members"].append(dict(zip(FIELDS, ["M009", "GIA", "", "700", "gia@example.invalid"])))
    yield "second_member_same_contacts", changed
    changed = json.loads(json.dumps(base))
    changed["members"][0]["name"] = "OTHER"
    yield "same_contact_different_name", changed
    changed = json.loads(json.dumps(base))
    changed["roi"][0]["phone"] = None
    changed["roi"][0]["email"] = None
    changed["buyer"][0]["hkid_hash"] = None
    yield "null_keys", changed
    yield "empty_buyer", {**base, "buyer": []}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    from pyspark.sql import SparkSession
    spark = (SparkSession.builder.master("local[2]").appName("club-training-assessment")
             .config("spark.sql.shuffle.partitions", "4").getOrCreate())
    spark.sparkContext.setLogLevel("WARN")
    results = []
    try:
        for name, batch in exercise_cases():
            rb, members = build_pairs(spark, batch)
            # collect is bounded here: only tiny assessment fixtures reach this code.
            actual_rb = sorted([list(row) for row in rb.select("roi_id", "buyer_id").collect()])
            actual_members = sorted([list(row) for row in members.select("source", "record_id", "member_id").collect()])
            expected = reference(batch)
            if actual_rb != expected["roi_buyer"] or actual_members != expected["member_candidates"]:
                raise AssertionError("PAIR_MISMATCH: " + name)
            print("PASS", name)
            results.append(name)
        rb.explain("formatted")
        evidence = {"spark_version": spark.version, "passed_cases": results,
                    "status": "PUBLIC_CASES_PASSED_NOT_MASTERY_CERTIFICATION"}
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
