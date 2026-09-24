"""Optional Spark comparisons for generic table operations, not business ports."""


def registration(df):
    from pyspark.sql import functions as F
    return df.withColumn("eligible", (F.col("age") >= 18) & F.col("consent"))


def retained(df):
    from pyspark.sql import Window, functions as F
    order = Window.partitionBy("name").orderBy("joined", "id")
    return df.withColumn("rank", F.row_number().over(order)).filter("rank = 1").drop("rank")


def candidates(forms, members):
    from pyspark.sql import functions as F
    left, right = forms.alias("f"), members.alias("m")
    phone = (F.col("f.phone") != "") & (F.col("f.phone") == F.col("m.phone"))
    email = (F.col("f.email") != "") & (F.col("f.email") == F.col("m.email"))
    condition = (F.col("f.name") == F.col("m.name")) & (phone | email)
    return left.join(right, condition).select(F.col("f.id").alias("form_id"), F.col("m.id").alias("member_id"))


def missing(expected, observed):
    return expected.join(observed, "unit", "left_anti").distinct()


def references(df):
    from pyspark.sql import functions as F
    result = df.withColumn("reference", F.explode(F.split("references", ",")))
    result = result.withColumn("reference", F.trim("reference"))
    return result.filter(F.col("reference") != "").select("id", "reference")
