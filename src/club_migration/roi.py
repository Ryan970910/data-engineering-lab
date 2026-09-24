"""ROI field projection and questionnaire stage, NOT the complete ROI importer."""

import re

from club_migration.contracts import BULK_IMPORT_DATA_TEMPLE_API, BULK_ROI_MAPPING_API


def question_value(value):
    """Keep Python's token ordering and whole-value float conversion semantics."""
    text = "+".join(sorted(set(str(value).replace("+", " ").split())))
    try:
        converted = str(int(float(text))) if text and text != "nan" else text
        return text, converted, False
    except (ValueError, OverflowError):
        return text, text, True


def property_count(value):
    """Deliberately raise for malformed tokens, as the legacy helper does."""
    return max(int(float(part)) for part in str(value).replace(" ", "+").split("+"))


def project_fields(df):
    """Input boundary: raw ROI columns AFTER swap_and_cleanse_cols(A_BLOCK)."""
    from pyspark.sql import functions as F

    names = list(dict.fromkeys([*BULK_IMPORT_DATA_TEMPLE_API,
        *[target for target, source in BULK_ROI_MAPPING_API.items() if source in df.columns]]))
    expressions = []
    for target in names:
        source = BULK_ROI_MAPPING_API.get(target)
        value = F.col(source) if source in df.columns else F.lit("")
        expressions.append(F.coalesce(value.cast("string"), F.lit("")).alias(target))
    return df.select("_row_id", *expressions)


def clean_questions(df):
    """Input boundary: string answers; column order is business-significant."""
    from pyspark.sql import functions as F

    columns = [c for c in df.columns if re.fullmatch(r"questionnaire_answer[0-9]", c, re.I)]
    parse = F.udf(question_value, "struct<text:string,converted:string,invalid:boolean>")
    for column in columns:
        df = df.withColumn("_question", parse(F.col(column)))
        if column == "Questionnaire_Answer2":
            bad = df.agg(F.max(F.col("_question.invalid").cast("int")).alias("_any_bad"))
            df = df.crossJoin(bad).withColumn(column, F.when(F.col("_any_bad") == 1,
                F.col("_question.text")).otherwise(F.col("_question.converted"))).drop("_any_bad")
        else:
            df = df.withColumn(column, F.col("_question.text"))
        df = df.drop("_question")
    return df.withColumn("questionAnswsers", F.array(*[F.col(c) for c in columns]).cast("array<string>"))


def transform(df):
    """Review artifact only: projection, property count, questionnaire answers."""
    from pyspark.sql import functions as F

    df = project_fields(df)
    count = F.udf(property_count, "long")
    df = df.withColumn("noOfPropertyPurchase", count(F.col("noOfPropertyPurchase")))
    return clean_questions(df)
