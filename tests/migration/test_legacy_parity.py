"""Differential checks against selected actual legacy functions, not whole workflows."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from club_migration.contracts import SOURCE_FIELDS, TEMPLATE_COLUMN_MAPPING, TEMPLATE_DATE_COLUMNS

AVAILABLE = bool(os.environ.get('LEGACY_PROJECT_ROOT') and os.environ.get('LEGACY_PYTHON') and importlib.util.find_spec('pyspark'))


@unittest.skipUnless(AVAILABLE, 'Real legacy checkout/interpreter and Spark required; parity not verified')
class LegacyParity(unittest.TestCase):
    def test_all_buyer_report_template_and_roi_question_values(self):
        import pandas as pd
        from pyspark.sql import SparkSession
        from club_migration.buyer import transform
        from club_migration.roi import clean_questions

        runtime = ROOT / '.learning-runtime/migration/parity-tests'
        runtime.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime) as folder:
            folder = Path(folder)
            members = []
            for serial, distribution, joined in [('10', 'SYNTHETIC', '2021-01-01'), ('20', 'OTHER', '2020-01-01'), ('30', 'ROI', '2022-01-01')]:
                row = dict.fromkeys(SOURCE_FIELDS, '')
                row.update(serial_number=serial, distribution=distribution, membership_start_date=joined)
                members.append(row)
            errors = [{'Retained_SN': '10', 'Terminated_SN': '20', 'Termination_ID': 'T1'},
                      {'Retained_SN': '10', 'Terminated_SN': '20', 'Termination_ID': 'T1'},
                      {'Retained_SN': '30', 'Terminated_SN': '10', 'Termination_ID': 'T2'}]
            questions = [{'Questionnaire_Answer2': '2.0', 'questionnaire_answer1': 'b a b'},
                         {'Questionnaire_Answer2': '3+1', 'questionnaire_answer1': ''}]
            columns = list(dict.fromkeys([*TEMPLATE_COLUMN_MAPPING.values(), *TEMPLATE_DATE_COLUMNS, 'unmapped']))
            data = {'members': members, 'errors': errors, 'questions': questions, 'template_columns': columns}
            source, expected = folder / 'input.json', folder / 'legacy.json'
            source.write_text(json.dumps(data), encoding='utf-8')
            legacy_env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            for key in ('PYTHONPATH', 'SPARK_PYTHON_UNPACKED', 'PRIVATE_MIGRATION_ARCHIVE'):
                legacy_env.pop(key, None)
            subprocess.run([os.environ['LEGACY_PYTHON'], str(Path(__file__).with_name('legacy_reference.py')),
                            os.environ['LEGACY_PROJECT_ROOT'], str(source), str(expected)], check=True,
                           env=legacy_env)
            baseline = json.loads(expected.read_text(encoding='utf-8'))
            spark = SparkSession.builder.master('local[2]').appName('actual-legacy-parity').config(
                'spark.ui.enabled', 'false').config('spark.sql.session.timeZone', 'Asia/Hong_Kong').getOrCreate()
            try:
                member_frame = spark.createDataFrame([(i, *[r[k] for k in SOURCE_FIELDS]) for i, r in enumerate(members)],
                    '_row_id long, ' + ', '.join(k + ' string' for k in SOURCE_FIELDS))
                error_frame = spark.createDataFrame([(i, r['Retained_SN'], r['Terminated_SN'], r['Termination_ID']) for i, r in enumerate(errors)],
                    '_row_id long, Retained_SN string, Terminated_SN string, Termination_ID string')
                report, template = transform(member_frame.repartition(2), error_frame.repartition(2), columns)
                question_frame = spark.createDataFrame([(i, r['Questionnaire_Answer2'], r['questionnaire_answer1']) for i, r in enumerate(questions)],
                    '_row_id long, Questionnaire_Answer2 string, questionnaire_answer1 string')
                frames = {'report': report, 'template': template, 'questions': clean_questions(question_frame)}
                for name, frame in frames.items():
                    with self.subTest(output=name):
                        fields = [c for c in frame.columns if c not in {'_row_id', '_source_retained', '_source_terminated'}]
                        self.assertEqual(fields, baseline[name]['columns'])
                        actual = pd.DataFrame([list(r) for r in frame.orderBy('_row_id').select(*fields).collect()], columns=fields)
                        actual = json.loads(actual.to_json(orient='split', date_format='iso'))
                        self.assertEqual(actual['data'], baseline[name]['data'])
                print('REAL LEGACY PARITY: all fields/rows of Buyer report, template and ROI questions; legacy pandas=' + baseline['legacy_pandas'])
            finally:
                spark.stop()


if __name__ == '__main__':
    unittest.main()
