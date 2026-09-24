"""Read-only port of the final BISERIALNO explosion, never the SQL updates."""


def transform(df):
    from pyspark.sql import functions as F

    df = df.withColumn("BISERIALNO", F.explode_outer(F.split(F.col("BISERIALNO"), " ", -1)))
    expressions = []
    for field in df.schema:
        target = "error_msg_raw" if field.name.lower() == "err_msg_raw" else field.name.lower()
        value = F.col(field.name)
        if field.dataType.simpleString() == "string":
            value = F.when(value != "nan", value)
        expressions.append(value.alias(target))
    return df.select(*expressions)
