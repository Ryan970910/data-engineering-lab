"""Real DETAILS expansion; record-specific exception IDs must stay in private job input."""

FIELDS = (
    "Category", "Intermediate Attengind", "Intermediate Grade", "Intermediate Teacher",
    "Primary Attending", "Primary Grade", "Primary Teacher", "Entry Type", "Story Title",
    "Text Entry", "Title", "Below 18 (please specify)", "Above 65 (please specify)",
    "SHKP Club promotional email", "SHKP Club website", "School", "SHKP Club Facebook Page",
    "SHKP Club Instagram Page", "SHKP Club WeChat Page", "Social media ads", "Mall promotions",
    "Estate publicity", "From Other", "learnOther", '"""2025LovingHome"""', "Form Type", "Create Date", "blank",
)


def transform(df, special_import_ids):
    from pyspark.sql import functions as F

    if not isinstance(special_import_ids, list) or not all(type(v) is int for v in special_import_ids):
        raise ValueError("Supply the approved integer exception IDs in the private job manifest")
    special = F.col("IMPORT_ID").isin(special_import_ids)
    expressions = []
    for field in df.schema:
        value = F.col(field.name)
        if field.dataType.simpleString() == "string":
            value = F.regexp_replace(value, r"\n|\r", " ")
            value = F.when(special, F.regexp_replace(value, " ", "")).otherwise(value)
            value = F.regexp_replace(value, r"剩(\d+)%", "剩百分之$1")
            value = F.regexp_replace(value, "100%", "百分之百")
        expressions.append(value.alias(field.name))
    df = df.select(*expressions)
    parts = F.split(F.col("DETAILS"), "%", -1)
    if df.filter(F.col("DETAILS").isNotNull() & (F.size(parts) < 28)).limit(1).count():
        raise ValueError("DETAILS has fewer than 28 fields; the legacy parser would fail too")
    df = df.withColumns({name: F.get(parts, i) for i, name in enumerate(FIELDS)})
    if df.filter(F.size(parts) == 29).limit(1).count():
        df = df.withColumn("file name", F.when(F.size(parts) == 29, F.get(parts, 28)))
    return df
