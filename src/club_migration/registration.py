"""Expressions shared by the three registration sources, not their policies."""

from club_migration.contracts import AGE_GROUP_MAPPING


def age_group(date_column, as_of_year):
    from pyspark.sql import functions as F

    age = F.lit(as_of_year) - F.year(date_column)
    result = F.lit(0)
    for label, value in reversed(list(AGE_GROUP_MAPPING.items())):
        if "-" in label:
            low, high = map(int, label.split("-"))
            result = F.when(age.between(low, high), value).otherwise(result)
        elif label == "65 or above":
            result = F.when(age >= 65, value).otherwise(result)
    return result


def star_fields(df):
    from pyspark.sql import functions as F

    return df.withColumns({"membershipType": F.lit("S"), "starFlat": F.col("room"),
        "starFloor": F.col("floor"), "starBlock": F.col("block"),
        "addressLanguage": F.lit("E"), "country": F.lit("H"), "callVerifyFlag": F.lit("Y")})
