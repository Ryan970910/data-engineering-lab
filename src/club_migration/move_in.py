"""First move-in comparison report; the later missing-member report is separate."""


def compare_units(collection, registered):
    from functools import reduce
    from operator import and_
    from pyspark.sql import functions as F

    keys = ["_KEY_BLOCK", "_KEY_FLOOR", "_KEY_FLAT"]

    def normalize(df, columns):
        for source, target in zip(columns, keys):
            value = F.upper(F.trim(F.coalesce(F.col(source).cast("string"), F.lit("nan"))))
            value = F.when(value != "NAN", value)
            df = df.withColumn(source, value).withColumn(target, value)
        return df

    left = normalize(collection, ["Tower", "Floor", "Unit"])
    right = normalize(registered, ["HANDOVER_BLOCK", "HANDOVER_FLOOR", "HANDOVER_FLAT"])
    condition = reduce(and_, [left[k].eqNullSafe(right[k]) for k in keys])
    return left.join(right, condition, "left_anti"), right.join(left, condition, "left_anti")
