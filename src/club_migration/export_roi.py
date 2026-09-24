"""Questionnaire response flattening; no HTTP fetch, SQL write or Excel export."""


def transform(df):
    from pyspark.sql import functions as F

    answers = F.col("anwerList")

    def answer(sequence):
        matching = F.filter(answers, lambda item: item["sequence"] == sequence)
        return F.try_element_at(matching, F.lit(-1))["anwer"]

    layout = answer(3)
    if df.filter((F.size("applicantList") == 0) | layout.isNull()).limit(1).count():
        raise ValueError("Legacy process_entry requires an applicant and a layout answer")
    applicants = F.col("applicantList")
    fields = [F.col("_row_id"), F.col("registrationNumber").alias("RegNums"), F.col("ballotId"),
        F.get(applicants, 0)["type"].alias("Type"), answer(1).alias("form_b_prev_prop_count"),
        answer(2).alias("form_b_purchase_plan"), F.regexp_replace(layout, ",", "|").alias("form_b_layout_plan")]
    for index in range(3):
        fields += [F.get(applicants, index)["sex"].alias(f"registrant{index + 1}_sex"),
                   F.get(applicants, index)["age"].alias(f"registrant{index + 1}_age_group")]
    return df.select(*fields)
