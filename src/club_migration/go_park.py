"""Go Park registration rules on an explicitly prepared, offline snapshot."""

from club_migration.contracts import TITLE_MAPPING
from .registration import age_group


def transform(df, as_of_year):
    """Names/phones/districts must already have passed the existing cleansers."""
    from pyspark.sql import functions as F

    titles = F.create_map(*[F.lit(v) for pair in TITLE_MAPPING.items() for v in pair])
    df = df.withColumn("title", F.element_at(titles, F.col("title")))
    birth_date = F.col("dateOfBirth").try_cast("date")
    if df.filter(birth_date.isNull()).limit(1).count():
        raise ValueError("Go Park requires a valid ISO dateOfBirth in the prepared snapshot")
    df = df.withColumn("ageGroup", age_group(birth_date, as_of_year))
    df = df.withColumn("membershipType", F.lit("G"))
    df = df.withColumn("addressLanguage", F.lit("E"))
    df = df.withColumn("callVerifyFlag", F.lit("Y"))
    consent = F.coalesce(F.col("Consent_to_join_SHKP_club"), F.lit(""))
    df = df.withColumn("Consent_to_join_SHKP_club", consent)
    reasons = [
        F.when(F.col("ageGroup") == -1, "Invalid Date of Birth"),
        F.when(F.col("name validation") == F.lit(False), "Invalid English Name"),
        F.when(consent.isin("N", ""), "Consent to Join SHKP CLUB is not given"),
        F.when(F.col("invalid mobile").isNull() & F.col("mobile").isNull(), "Mobile number is missing"),
    ]
    return df.withColumn("remark", F.concat_ws("+", *reasons)).drop("name validation")
