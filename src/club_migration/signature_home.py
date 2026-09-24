"""Signature Home final rules AFTER existing address/contact/name processing."""

from .registration import age_group, star_fields


def transform(df, as_of_year):
    from pyspark.sql import functions as F

    df = star_fields(df).withColumn("ageGroup", age_group(F.col("dateOfBirth").try_cast("date"), as_of_year))
    reasons = [
        F.when(F.col("ageGroup") == -1, "Invalid Date of Birth"),
        F.when(F.col("name validation") == F.lit(False), "Invalid English Name"),
    ]
    return df.withColumn("remark", F.concat_ws("+", *reasons)).drop("name validation", "name_pre_check")
