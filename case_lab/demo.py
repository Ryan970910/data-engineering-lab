"""Run all fourteen fictional Python cases without Spark, Airflow or networking."""

import json
from datetime import date
from pathlib import Path
from uuid import uuid4

from . import stages


def run():
    members = [{"id": "M2", "name": "ADA", "joined": "2024-01-01", "phone": "fixture-1", "email": ""},
               {"id": "M1", "name": "ADA", "joined": "2020-01-01", "phone": "fixture-2", "email": "ada@example.invalid"}]
    outputs = {
        "interest": stages.interest_answers("B a b"),
        "retained": stages.retained_members(members),
        "event": stages.event_signup({"age": 17, "consent": True}),
        "residency": stages.residency_signup({"unit": " a1 ", "email": ""}),
        "lease": stages.lease_signup({"start": "2024-02-28", "end": "2024-03-01"}),
        "forms": stages.form_candidates([{"id": "F1", "name": "ADA", "phone": "fixture-1", "email": ""}], members),
        "move_in": stages.missing_units(["A1", "A2"], ["A1"]),
        "files": stages.file_plan(["question.csv", "interest.csv"]),
        "export": stages.flatten_answers([{"id": "Q1", "answers": {"layout": "two rooms"}}]),
        "name_score": stages.name_score(["Ada", "Ada"], ["ADA"]),
        "monthly": stages.monthly_list([{"id": "S1", "submitted": "2024-02-29"}], date(2024, 3, 1)),
        "handover": stages.handover_cells([{"floor": "2", "units": {"A": None, "B": "2024-03-01"}}]),
        "writing": stages.writing_entries("fiction|A walk|A fictional story"),
        "references": stages.expand_references([{"id": "R1", "references": "X1, ,X2"}]),
    }
    root = Path(__file__).resolve().parents[1] / ".learning-runtime" / "cases" / uuid4().hex
    root.mkdir(parents=True)
    evidence = {"synthetic_only": True, "production_parity": False, "engine": "python", "outputs": outputs}
    path = root / "evidence.json"
    path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    return str(path)


if __name__ == "__main__":
    print(run())
