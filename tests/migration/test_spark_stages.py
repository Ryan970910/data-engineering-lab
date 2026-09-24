"""Real Spark execution tests. Missing Spark means SKIPPED, never PASS."""

import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
HAS_SPARK = importlib.util.find_spec("pyspark") is not None


@unittest.skipUnless(HAS_SPARK, "PySpark is not installed; runtime not verified")
class SparkStages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pyspark.sql import SparkSession
        cls.spark = SparkSession.builder.master("local[2]").appName("private-migration-tests").config(
            "spark.sql.session.timeZone", "Asia/Hong_Kong").config("spark.ui.enabled", "false").config(
            "spark.local.dir", str(ROOT / ".learning-runtime/migration/spark-tests")).getOrCreate()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def frame(self, rows, schema):
        return self.spark.createDataFrame(rows, schema)

    def test_roi_questionnaire_global_fallback_across_partitions(self):
        from club_migration.roi import clean_questions
        df = self.frame([(0, "2.0", "b a"), (1, "3+1", "")],
            "_row_id long, Questionnaire_Answer2 string, questionnaire_answer1 string").repartition(2)
        rows = clean_questions(df).orderBy("_row_id").collect()
        self.assertEqual([r.questionAnswsers for r in rows], [["2.0", "a+b"], ["1+3", ""]])

    def test_roi_projection_property_count(self):
        from club_migration.roi import transform
        df = self.frame([(0, "TEST PERSON", "1 3.9", "2.0")],
            "_row_id long, ENGLISH_NAME string, PROPERTY_PREFERENCE string, Q2 string")
        row = transform(df).first()
        self.assertEqual((row.englishName, row.noOfPropertyPurchase, row.Questionnaire_Answer2), ("TEST PERSON", 3, "2"))

    def test_go_park_65_and_remark_order(self):
        from club_migration.go_park import transform
        df = self.frame([(0, "MR", "1961-01-01", True, "Y", None, "852-60000000"),
                         (1, "mr", "2010-01-01", False, "N", None, None)],
            "_row_id long, title string, dateOfBirth string, `name validation` boolean, Consent_to_join_SHKP_club string, `invalid mobile` string, mobile string")
        rows = transform(df, 2026).orderBy("_row_id").collect()
        self.assertEqual(rows[0].ageGroup, 62)
        self.assertIsNone(rows[1].title)
        self.assertEqual(rows[1].remark, "Invalid Date of Birth+Invalid English Name+Consent to Join SHKP CLUB is not given+Mobile number is missing")

    def test_townplace_and_signature_home_age_difference(self):
        from club_migration import townplace, signature_home
        df = self.frame([(0, "2010-01-01", True, None, None, "", "A", "1", "2")],
            "_row_id long, dateOfBirth string, `name validation` boolean, `invalid mobile` string, mobile string, emailAddress string, room string, floor string, block string")
        self.assertEqual(townplace.transform(df, 2026).first().ageGroup, 0)
        self.assertEqual(signature_home.transform(df, 2026).first().remark, "Invalid Date of Birth")

    def test_loving_home_real_field_positions(self):
        from club_migration.loving_home import transform
        text = "%".join([str(i) for i in range(29)])
        df = self.frame([(0, 1, text, "剩20% 100%\ntext")], "_row_id long, IMPORT_ID long, DETAILS string, note string")
        row = transform(df, special_import_ids=[]).first()
        self.assertEqual(row["Intermediate Attengind"], "1")
        self.assertEqual(row["file name"], "28")
        self.assertEqual(row.note, "剩百分之20 百分之百 text")

    def test_handover_unpivot_includes_empty_cell(self):
        from club_migration.handover import transform
        df = self.frame([(0, "B1", 0, 2, "Flat A"), (0, "B1", 1, 0, "5/F"), (0, "B1", 1, 2, None)],
            "sheet_order long, sheet string, row long, col long, value string")
        row = transform(df).first()
        self.assertEqual((row.flat, row.floor, row.date, row.block), ("A", "5", "", "B1"))

    def test_move_in_null_equal_anti_joins(self):
        from club_migration.move_in import compare_units
        left = self.frame([(0, " a ", None, "1"), (1, "B", "1", "2")], "_row_id long, Tower string, Floor string, Unit string")
        right = self.frame([(0, "A", None, "1")], "_row_id long, HANDOVER_BLOCK string, HANDOVER_FLOOR string, HANDOVER_FLAT string")
        missing_left, missing_right = compare_units(left, right)
        self.assertEqual([r.Tower for r in missing_left.collect()], ["B"])
        self.assertEqual(missing_right.count(), 0)

    def test_update_roi_space_explosion_keeps_empty_tokens(self):
        from club_migration.update_roi import transform
        df = self.frame([(0, "A  B", "nan")], "_row_id long, BISERIALNO string, ERR_MSG_RAW string")
        rows = transform(df).collect()
        self.assertCountEqual([r.biserialno for r in rows], ["A", "", "B"])
        self.assertTrue(all(r.error_msg_raw is None for r in rows))

    def test_the_point_duplicate_score(self):
        from club_migration.the_point_check import transform
        df = self.frame([(0, ["CHAN", "CHAN"], ["Chan"])], "_row_id long, applicant_segments array<string>, buyer_segments array<string>")
        self.assertEqual(transform(df).first().match_rate, 1.0)

    def test_the_point_list_inclusive_period_and_hash(self):
        from club_migration.the_point_list import transform, hash_mobile
        df = self.frame([(0, "1", "test", "100", "A", "1", "2", "", "852", "60000000", "Y", "N", "Y", "Y", "2026-09-15 23:59:59", None)],
            "_row_id long, import_id string, description string, property_code string, handover_block string, handover_flat string, handover_floor string, tp_member_no string, mobile_country_code string, mobile string, choose_the_point string, send_the_point_url string, check_the_point_tnc string, is_owner string, date_entered string, date_submitted string")
        row = transform(df, date(2026, 9, 16)).first()
        self.assertEqual(row.hashed_mobile, hash_mobile("85260000000"))
        self.assertEqual(row.tp_gold, "Y")

    def test_export_questions_last_duplicate_answer_and_three_applicants(self):
        from club_migration.export_roi import transform
        df = self.frame([(0, "R1", "B1", [(1, "1"), (3, "a,b"), (3, "c,d")], [("I", "F", "18")])],
            "_row_id long, registrationNumber string, ballotId string, anwerList array<struct<sequence:int,anwer:string>>, applicantList array<struct<type:string,sex:string,age:string>>")
        row = transform(df).first()
        self.assertEqual(row.form_b_layout_plan, "c|d")
        self.assertIsNone(row.registrant3_sex)

    def test_buyer_form_oldest_and_mobile_before_email(self):
        from club_migration.buyer_form import transform
        fields = "_row_id long, english_name string, membership_start_date string, mobilephone string, email string, serial_number string, title string, age_group string, district string, country string, province string, city string"
        members = self.frame([(0, "TEST", "2020-01-01", "m1", "e1", "10", "1", "18", "D", "H", "", ""),
                             (1, "TEST", "2021-01-01", "m2", "e2", "11", "2", "22", "D", "H", "", "")], fields)
        forms = self.frame([(0, "TEST", "m2", "e1", None, None, None, None, None, None, None)],
            "_row_id long, english_name string, hashed_form_mobile string, hashed_form_email string, serial_no string, title string, age_gp string, district_18 string, country string, province string, city string")
        self.assertEqual(transform(members, forms).first().serial_no, "11")

    def test_buyer_report_preserves_regex_and_date_rules(self):
        from club_migration.contracts import SOURCE_FIELDS
        from club_migration.buyer import transform
        def member(serial, distribution, start):
            row = dict.fromkeys(SOURCE_FIELDS, "")
            row.update(serial_number=serial, distribution=distribution, membership_start_date=start)
            return row
        records = [member("10", "Buyers Triple Rewards", "2021-01-01"), member("20", "OTHER", "2020-01-01")]
        source = self.frame([(i, *[r[k] for k in SOURCE_FIELDS]) for i, r in enumerate(records)],
            "_row_id long, " + ", ".join(f"{k} string" for k in SOURCE_FIELDS))
        errors = self.frame([(0, "10", "20", "T1"), (1, "10", "20", "T1")],
            "_row_id long, Retained_SN string, Terminated_SN string, Termination_ID string")
        report, template = transform(source.repartition(2), errors.repartition(2), ["Serial No", "membership start date"])
        row = report.first()
        self.assertEqual((row.transfer_mobile, row.distribution_retained, row._row_id), ("Y", "OTHER", 0))
        self.assertEqual(template.first()["membership start date"], "01-01-2020")


if __name__ == "__main__":
    unittest.main(verbosity=2)
