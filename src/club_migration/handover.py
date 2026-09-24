"""Unpivot workbook cells using original sheet/row/column coordinates."""


def transform(cells):
    """Columns: sheet_order, sheet, row, col, value; null cells must be present."""
    from pyspark.sql import functions as F

    headers = cells.filter((F.col("row") == 0) & (F.col("col") >= 2)
        & F.col("value").startswith("Flat")).select("sheet_order", "sheet", "col",
        F.when(F.col("value").rlike("Flat (.*)"), F.regexp_extract("value", "Flat (.*)", 1)).alias("flat"))
    floors = cells.filter((F.col("row") > 0) & (F.col("col") == 0)).select("sheet_order", "sheet", "row",
        F.when(F.col("value").rlike("(.*)/F"), F.regexp_extract("value", "(.*)/F", 1)).alias("floor"))
    body = cells.filter(F.col("row") > 0)
    result = body.join(headers, ["sheet_order", "sheet", "col"]).join(floors, ["sheet_order", "sheet", "row"])
    return result.select("sheet_order", "row", "col", "flat", "floor",
        F.trim(F.coalesce(F.col("value"), F.lit(""))).alias("date"), F.col("sheet").alias("block"))
