"""Buyer-form membership lookup on already normalized names and hashed contacts."""


def transform(members, forms):
    from pyspark.sql import Window, functions as F

    fields = {"serial_no": "serial_number", "title": "title", "age_gp": "age_group",
              "district_18": "district", "country": "country", "province": "province", "city": "city"}
    payload = F.struct(*[F.col(source).alias(target) for target, source in fields.items()])
    contacts = members.select("_row_id", "english_name", "membership_start_date", payload.alias("_member"),
        F.explode(F.array("mobilephone", "email")).alias("_contact"))
    order = Window.partitionBy("english_name", "_contact").orderBy("membership_start_date", "_row_id")
    lookup = contacts.withColumn("_rank", F.row_number().over(order)).filter("_rank = 1")
    result = forms
    for key, label in [("hashed_form_mobile", "mobile"), ("hashed_form_email", "email")]:
        right = lookup.select(F.col("english_name").alias("_name"), "_contact", F.col("_member").alias(f"_{label}"))
        condition = result["english_name"].eqNullSafe(right["_name"]) & result[key].eqNullSafe(right["_contact"])
        result = result.join(right, condition, "left").drop("_name", "_contact")
    match = F.coalesce(F.col("_mobile"), F.col("_email"))
    fill = F.col("serial_no").isNull() & match.isNotNull()
    result = result.withColumns({name: F.when(fill, match[name]).otherwise(F.col(name)) for name in fields})
    return result.drop("_mobile", "_email")
