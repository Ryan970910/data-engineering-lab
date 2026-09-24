"""The Point half-month selection on canonical ISO timestamp/string inputs."""

import hashlib
from datetime import datetime, timedelta


def period_bounds(run_date):
    today = datetime.combine(run_date, datetime.min.time())
    if today.day == 16:
        return today.replace(day=1), today - timedelta(seconds=1)
    if today.day == 1:
        last = today - timedelta(seconds=1)
        return last.replace(day=16, hour=0, minute=0, second=0), last
    raise ValueError("The legacy report defines a period only on the 1st or 16th")


def hash_mobile(value):
    try:
        value = int(value)
        number = int((value * 8 + 45678) / 2)
        return hashlib.sha256(str(number).encode("utf-8")).hexdigest().lower()
    except (ValueError, TypeError, OverflowError):
        return value


def transform(df, run_date):
    from pyspark.sql import functions as F

    start, end = period_bounds(run_date)
    latest = F.greatest(F.col("date_entered").try_cast("timestamp"), F.col("date_submitted").try_cast("timestamp"))
    df = df.filter(latest.between(start, end))
    mobile = F.concat(F.coalesce(F.col("mobile_country_code"), F.lit("nan")), F.coalesce(F.col("mobile"), F.lit("nan")))
    member = F.col("tp_member_no")
    requested = (member.isNull() | (member == "")) & (F.col("choose_the_point") == "Y") & (F.col("send_the_point_url") == "N")
    mobile = F.when(requested | member.isNotNull(), mobile).otherwise(F.lit(""))
    gold = F.when((F.col("check_the_point_tnc") == "Y") & (F.col("is_owner") == "Y"), "Y").otherwise("N")
    df = df.select("_row_id", "import_id", "description", "property_code", "handover_block", "handover_flat", "handover_floor",
        F.coalesce(member, F.lit("")).alias("tp_member_no"), mobile.alias("mobile"), gold.alias("tp_gold"))
    df = df.withColumn("hashed_mobile", F.udf(hash_mobile, "string")(F.col("mobile")))
    df = df.replace("", None)
    return df.dropna(subset=["tp_member_no", "mobile"], how="all")
