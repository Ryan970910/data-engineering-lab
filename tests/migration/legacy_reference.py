"""Run only selected legacy pure functions with the real legacy interpreter.

Never imports a production module or invokes a database/API/UI entry point.
"""
import ast
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    legacy, input_path, output_path = map(Path, sys.argv[1:])
    data = json.loads(input_path.read_text(encoding="utf-8"))
    namespace = {"pd": pd, "np": np, "re": re}
    contract = ast.parse((legacy / "src/shkpclub/common/buyer_report_contract.py").read_text(encoding="utf-8"))
    for node in contract.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            namespace[node.target.id] = ast.literal_eval(node.value)
    tree = ast.parse((legacy / "src/shkpclub/sources/buyer.py").read_text(encoding="utf-8"))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'BuyerBulkImportMixin')
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in {
        'map_source_to_output', 'build_retained_dataframe', 'fill_template_with_data'}]
    assert len(methods) == 3
    for node in methods:
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<selected-legacy-buyer>', 'exec'), namespace)
    source, errors = pd.DataFrame(data['members']), pd.DataFrame(data['errors'])
    pairs = namespace['map_source_to_output'](None, source, errors)
    report = namespace['build_retained_dataframe'](None, pairs).drop_duplicates(subset=['Termination_ID'])
    template_path = input_path.parent / 'template.xlsx'
    pd.DataFrame(columns=data['template_columns']).to_excel(template_path, index=False)
    template = namespace['fill_template_with_data'](None, str(template_path), report)
    tree = ast.parse((legacy / 'src/shkpclub/sources/roi_mapping.py').read_text(encoding='utf-8'))
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'clean_question_column')
    exec(compile(ast.Module(body=[fn], type_ignores=[]), '<selected-legacy-roi>', 'exec'), namespace)
    questions = namespace['clean_question_column'](pd.DataFrame(data['questions']))
    def serialize(frame):
        value = json.loads(frame.to_json(orient='split', date_format='iso'))
        return {'columns': value['columns'], 'data': value['data']}
    result = {'report': serialize(report), 'template': serialize(template), 'questions': serialize(questions),
              'legacy_pandas': pd.__version__, 'scope': 'selected_real_functions_only'}
    output_path.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
