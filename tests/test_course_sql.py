"""Offline tests for the course SQL helper; never imports production code."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

COURSE = Path(__file__).resolve().parents[1] / "docs" / "data-engineering"
sys.path.insert(0, str(COURSE))
from lab import SAMPLES, FIELDS, extract
from sql_lab import query, check, DEFAULT_QUERY

RB = "SELECT r.record_id AS roi_id, b.record_id AS buyer_id FROM source_records r JOIN source_records b ON r.name=b.name AND r.hkid_hash=b.hkid_hash WHERE r.source='roi' AND b.source='buyer' AND r.hkid_hash IS NOT NULL"
MEMBERS = "SELECT s.source, s.record_id, m.member_id FROM source_records s JOIN members m ON s.name=m.name AND (s.phone=m.phone OR s.email=m.email)"


class CourseSQLTests(unittest.TestCase):
    def setUp(self):
        self.batch = {name: [dict(zip(FIELDS, row)) for row in rows] for name, rows in SAMPLES.items()}

    def test_default_counts(self):
        self.assertEqual(query(self.batch, DEFAULT_QUERY), (["source", "record_count"], [["buyer", 7], ["roi", 8]]))

    def test_exact_both_relations(self):
        for sql, expected in [(RB, "roi-buyer"), (MEMBERS, "member-candidates")]:
            columns, rows = query(self.batch, sql)
            check(self.batch, columns, rows, expected)

    def test_changed_hash_not_hardcoded(self):
        self.batch["buyer"][0]["hkid_hash"] = "changed"
        columns, rows = query(self.batch, RB)
        self.assertEqual(len(rows), 4)
        check(self.batch, columns, rows, "roi-buyer")

    def test_empty_buyer(self):
        self.batch["buyer"] = []
        columns, rows = query(self.batch, RB)
        self.assertEqual(rows, [])
        check(self.batch, columns, rows, "roi-buyer")

    def test_null_and_multiple_members(self):
        self.batch["members"].append({**self.batch["members"][6], "id": "M009"})
        self.batch["roi"][0]["phone"] = None
        self.batch["roi"][0]["email"] = None
        columns, rows = query(self.batch, MEMBERS)
        check(self.batch, columns, rows, "member-candidates")
        self.assertEqual(sum(row[:2] == ["roi", "R007"] for row in rows), 2)

    def test_bad_count_duplicate_and_columns_rejected(self):
        columns, rows = query(self.batch, RB)
        for bad in [rows[:-1], rows + [rows[0]], [["wrong", "wrong"]] + rows[1:]]:
            with self.assertRaisesRegex(ValueError, "ROW_MISMATCH"):
                check(self.batch, columns, bad, "roi-buyer")
        with self.assertRaisesRegex(ValueError, "COLUMN_MISMATCH"):
            check(self.batch, ["x", "y"], rows, "roi-buyer")

    def test_writes_attach_and_pragma_rejected(self):
        for sql in ["DELETE FROM members", "CREATE TABLE x (id)", "UPDATE members SET name='X'", "ATTACH DATABASE ':memory:' AS other", "PRAGMA user_version=1", "SELECT load_extension('missing')"]:
            with self.subTest(sql=sql), self.assertRaises(sqlite3.DatabaseError):
                query(self.batch, sql)

    def test_cte_supported(self):
        self.assertEqual(query(self.batch, "WITH counts AS (" + DEFAULT_QUERY + ") SELECT * FROM counts ORDER BY source")[1], [["buyer", 7], ["roi", 8]])

    def test_cli_snapshot_pin_and_nonzero_failure(self):
        runtime = COURSE.parents[1] / ".learning-runtime" / "sql-tests"
        runtime.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime) as directory:
            root = Path(directory)
            command = [sys.executable, str(COURSE / "sql_lab.py"), "--workspace", str(root)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(first.stdout)["rows"], [["buyer", 7], ["roi", 8]])
            sql_file = root / "query.sql"
            sql_file.write_text(RB, encoding="utf-8-sig")
            check_command = command + ["--query-file", str(sql_file), "--expect", "roi-buyer"]
            raw = root / "raw" / "buyer.csv"
            raw.write_text(raw.read_text().replace("hash-a", "new-hash"), encoding="utf-8")
            pinned = subprocess.run(check_command, capture_output=True, text=True)
            self.assertEqual(pinned.returncode, 0, pinned.stderr)
            self.assertEqual(json.loads(pinned.stdout)["row_count"], 5)
            extract(root)
            changed = subprocess.run(check_command, capture_output=True, text=True)
            self.assertEqual(changed.returncode, 0, changed.stderr)
            self.assertEqual(json.loads(changed.stdout)["row_count"], 4)
            failed = subprocess.run(command + ["--sql", "DELETE FROM members"], capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("not authorized", failed.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
