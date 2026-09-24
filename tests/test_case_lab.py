import ast
import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from case_lab import stages as s


class Cases(unittest.TestCase):
    def test_interest(self):
        self.assertEqual(s.interest_answers("b A b"), ["a", "b"])

    def test_retained(self):
        rows = [{"name": "A", "joined": "2020-01-01", "id": "2"}, {"name": "A", "joined": "2020-01-01", "id": "1"}]
        self.assertEqual(s.retained_members(rows)[0]["id"], "1")

    def test_event(self):
        self.assertFalse(s.event_signup({"age": 17, "consent": True})["eligible"])

    def test_residency(self):
        self.assertEqual(s.residency_signup({"unit": " a ", "email": ""}), {"unit": "A", "email": "", "review": True})

    def test_lease(self):
        self.assertEqual(s.lease_signup({"start": "2024-02-28", "end": "2024-03-01"})["days"], 2)
        with self.assertRaises(ValueError):
            s.lease_signup({"start": "2024-03-01", "end": "2024-02-28"})

    def test_forms(self):
        forms = [{"id": "F", "name": "A", "phone": "", "email": ""}]
        members = [{"id": "M", "name": "A", "phone": "", "email": ""}]
        self.assertEqual(s.form_candidates(forms, members), [])

    def test_move_in(self):
        self.assertEqual(s.missing_units(["A", "B", "B"], ["A"]), ["B"])

    def test_files(self):
        self.assertEqual(s.file_plan(["a.csv"])[0]["destination"], "review/a.csv")
        with self.assertRaises(ValueError):
            s.file_plan(["../a.csv"])
        with self.assertRaises(ValueError):
            s.file_plan(["..\\a.csv"])

    def test_export(self):
        self.assertEqual(s.flatten_answers([{"id": "A", "answers": {"q": "yes"}}]), [{"id": "A", "question": "q", "answer": "yes"}])

    def test_score(self):
        self.assertEqual(s.name_score(["A", "A"], ["a"]), 1)
        self.assertEqual(s.name_score(["A"], ["a", "a"]), .5)

    def test_month(self):
        self.assertEqual(s.monthly_list([{"submitted": "2024-02-29"}, {"submitted": "2024-03-01"}], date(2024, 3, 4)), [{"submitted": "2024-02-29"}])

    def test_handover(self):
        self.assertEqual(len(s.handover_cells([{"floor": "1", "units": {"A": None}}])), 1)

    def test_writing(self):
        self.assertEqual(s.writing_entries("a|b|c")["body"], "c")
        with self.assertRaises(ValueError):
            s.writing_entries("bad")

    def test_references(self):
        self.assertEqual(s.expand_references([{"id": "A", "references": "X, ,Y"}]), [{"id": "A", "reference": "X"}, {"id": "A", "reference": "Y"}])

    def test_real_demo(self):
        from case_lab.demo import run
        evidence = json.loads(Path(run()).read_text(encoding="utf-8"))
        self.assertEqual(len(evidence["outputs"]), 14)
        self.assertTrue(evidence["synthetic_only"])
        self.assertFalse(evidence["production_parity"])

    def test_no_production_imports(self):
        allowed = {"case_lab", "collections", "datetime", "pathlib", "uuid", "json", "pyspark", "airflow"}
        for path in (ROOT / "case_lab").glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    self.assertTrue(all(alias.name.split(".")[0] in allowed for alias in node.names))
                if isinstance(node, ast.ImportFrom) and node.module:
                    self.assertIn(node.module.split(".")[0], allowed)


@unittest.skipUnless(importlib.util.find_spec("pyspark"), "PySpark absent; runtime not verified")
class SparkCases(unittest.TestCase):
    def test_real_spark(self):
        from pyspark.sql import SparkSession
        from case_lab import spark_stages as p
        spark = SparkSession.builder.master("local[2]").appName("fictional-cases").config("spark.local.dir", str(ROOT / ".learning-runtime/spark")).getOrCreate()
        try:
            row = p.registration(spark.createDataFrame([(18, True)], "age int, consent boolean")).first()
            self.assertTrue(row.eligible)
            frame = spark.createDataFrame([("A", "X, ,Y")], "id string, references string")
            self.assertEqual(sorted(r.reference for r in p.references(frame).collect()), ["X", "Y"])
            members = spark.createDataFrame([("1", "A", "2020-01-01", "p", ""), ("2", "A", "2021-01-01", "q", "")], "id string, name string, joined string, phone string, email string")
            self.assertEqual(p.retained(members).first().id, "1")
            forms = spark.createDataFrame([("F", "A", "p", "")], "id string, name string, phone string, email string")
            self.assertEqual(p.candidates(forms, members).first().member_id, "1")
            self.assertEqual(p.missing(spark.createDataFrame([("A",), ("B",)], "unit string"), spark.createDataFrame([("A",)], "unit string")).first().unit, "B")
        finally:
            spark.stop()


@unittest.skipUnless(importlib.util.find_spec("airflow"), "Airflow absent; DAG runtime not verified")
class AirflowCases(unittest.TestCase):
    def test_dag_import(self):
        from airflow.models import DagBag
        bag = DagBag(dag_folder=str(ROOT / "case_lab/dag.py"), include_examples=False)
        self.assertEqual(bag.import_errors, {})
        self.assertEqual(set(bag.get_dag("fictional_cases").task_ids), {"transform", "inspect"})


if __name__ == "__main__":
    unittest.main()
