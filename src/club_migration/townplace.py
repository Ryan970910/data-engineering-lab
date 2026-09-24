"""Townplace final rules AFTER existing name/address/contact/date cleansing."""

from .registration import age_group, star_fields


def transform(df, as_of_year):
    from pyspark.sql import functions as F

    group = age_group(F.col("dateOfBirth").try_cast("date"), as_of_year)
    df = star_fields(df).withColumn("ageGroup", F.when(group == -1, 0).otherwise(group))
    reasons = [
        F.when(F.col("ageGroup") == -1, "Invalid Date of Birth"),
        F.when(F.col("name validation") == F.lit(False), "Invalid English Name"),
        F.when(F.col("invalid mobile").isNull() & F.col("mobile").isNull(), "Mobile number is missing"),
        F.when(F.col("emailAddress") == "", "Email is missing"),
    ]
    return df.withColumn("remark", F.concat_ws("+", *reasons)).drop("name validation", "Full Name  ↑")
