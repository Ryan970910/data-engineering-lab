"""Actual duplicate-aware syllable score on prepared name-segment arrays."""

from collections import Counter


def match_rate(left, right):
    if not isinstance(left, list) or not isinstance(right, list) or not left or not right:
        return 0.0
    matches = Counter(map(str.upper, left)) & Counter(map(str.upper, right))
    return sum(matches.values()) / len(right)


def transform(df):
    from pyspark.sql import functions as F

    score = F.udf(match_rate, "double")
    return df.withColumn("match_rate", score(F.col("applicant_segments"), F.col("buyer_segments")))
