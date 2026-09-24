"""Port of the production retained/terminated report, not ROI-Buyer matching."""

from club_migration.contracts import (
    BLOCKED_ACTIVATE_STATUS, DATE_COLUMNS_PAIRED, MIN_DATE_BASES,
    REPLACE_WHEN_TERMINATED_IS_NEWER, SOURCE_FIELDS,
    TEMPLATE_COLUMN_MAPPING, TEMPLATE_DATE_COLUMNS,
)


def map_source_to_output(source, errors):
    """Keep every left-join match and retain input ordering as explicit columns."""
    from pyspark.sql import functions as F

    result = errors.select("_row_id", "Retained_SN", "Terminated_SN", "Termination_ID")
    fields = [c for c in SOURCE_FIELDS if c != "serial_number"]
    for key, suffix in [("Retained_SN", "retained"), ("Terminated_SN", "terminated")]:
        right = source.select(F.col("serial_number").alias("_join_sn"),
            F.col("_row_id").alias(f"_source_{suffix}"),
            *[F.col(c).alias(f"{c}_{suffix}") for c in fields])
        result = result.join(right, result[key].eqNullSafe(right["_join_sn"]), "left").drop("_join_sn")
    return result


def build_retained_dataframe(df):
    from pyspark.sql import functions as F

    for column in DATE_COLUMNS_PAIRED:
        df = df.withColumn(column, F.col(column).try_cast("timestamp"))

    def clean(column):
        return F.trim(F.coalesce(F.col(column), F.lit("")))

    status = clean("activate_status_retained")
    verified = F.upper(clean("verify_email_retained")) == "Y"
    mobile = F.upper(clean("valid_mobile_retained")) == "Y"
    email = F.upper(clean("valid_email_retained")) == "Y"
    retained = F.upper(clean("distribution_retained"))
    terminated = F.upper(clean("distribution_terminated"))
    blocked = status.isin(BLOCKED_ACTIVATE_STATUS)
    rewards = retained.rlike(".*Buyers Triple Rewards.*")
    roi = terminated.rlike(".*ROI*")
    email_reward = email & ~blocked & terminated.rlike(".*Buyers Triple Rewards.*")
    deny_mobile = blocked | verified | mobile | rewards | roi
    df = df.withColumn("transfer_mobile", F.when(deny_mobile, "N").otherwise("Y"))
    df = df.withColumn("transfer_email", F.when(deny_mobile | email_reward, "N").otherwise("Y"))
    replace = F.col("membership_start_date_retained") > F.col("membership_start_date_terminated")
    replacements = {target: F.when(replace, F.col(source)).otherwise(F.col(target))
                    for target, source in REPLACE_WHEN_TERMINATED_IS_NEWER.items()}
    df = df.withColumns(replacements)
    for base in MIN_DATE_BASES:
        df = df.withColumn(f"{base}_retained", F.least(F.col(f"{base}_retained"), F.col(f"{base}_terminated")))
    columns = ["_row_id", "_source_retained", "_source_terminated", "Retained_SN", "Terminated_SN", "Termination_ID"]
    columns += [f"{c}_retained" for c in ["distribution", "activate_status", "verify_email", "valid_mobile",
        "valid_email", "opt_out", "opt_out_phone", "opt_out_sms", "opt_out_post", "membership_start_date",
        "date_of_birth", "education", "age_group", "marital", "star_approval_date", "received_date",
        "application_date", "approval_date"]]
    return df.select(*columns, "transfer_mobile", "transfer_email")


def keep_first(df, keys):
    from pyspark.sql import Window, functions as F

    order = [F.col(c).asc_nulls_first() for c in ["_row_id", "_source_retained", "_source_terminated"]]
    rank = F.row_number().over(Window.partitionBy(*keys).orderBy(*order))
    return df.withColumn("_rank", rank).filter(F.col("_rank") == 1).drop("_rank")


def fill_template(df, template_columns):
    from pyspark.sql import functions as F

    df = keep_first(df, ["Retained_SN"])
    reverse = {target: source for source, target in TEMPLATE_COLUMN_MAPPING.items()}
    expressions = []
    for target in template_columns:
        source = reverse.get(target, target)
        value = F.col(source) if source in df.columns else F.lit(None).cast("string")
        if target in TEMPLATE_DATE_COLUMNS:
            value = F.date_format(value.try_cast("timestamp"), "dd-MM-yyyy")
        expressions.append(value.alias(target))
    return df.select("_row_id", *expressions)


def transform(source, errors, template_columns):
    from pyspark.sql import functions as F

    errors = errors.filter(F.col("Termination_ID").isNotNull() & (F.col("Termination_ID") != ""))
    pairs = map_source_to_output(source, errors)
    retained = keep_first(build_retained_dataframe(pairs), ["Termination_ID"])
    return retained, fill_template(retained, template_columns)
