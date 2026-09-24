"""Small reference transformations with invented, public teaching contracts."""

from collections import Counter
from datetime import date, timedelta
from pathlib import PurePosixPath


def interest_answers(text):
    return sorted(set((text or "").lower().split()))


def retained_members(members):
    selected = {}
    for row in sorted(members, key=lambda item: (item["joined"], item["id"])):
        selected.setdefault(row["name"], row)
    return list(selected.values())


def event_signup(row):
    return {**row, "eligible": row["age"] >= 18 and row["consent"] is True}


def residency_signup(row):
    return {**row, "unit": row["unit"].strip().upper(), "review": not bool(row["email"])}


def lease_signup(row):
    start, end = date.fromisoformat(row["start"]), date.fromisoformat(row["end"])
    if end < start:
        raise ValueError("Lease end precedes start")
    return {**row, "days": (end - start).days}


def form_candidates(forms, members):
    # ponytail: tiny reference fixtures only; use a measured SQL join for larger batches.
    return [(form["id"], member["id"]) for form in forms for member in members
            if form["name"] == member["name"] and
            ((bool(form["phone"]) and form["phone"] == member["phone"]) or
             (bool(form["email"]) and form["email"] == member["email"]))]


def missing_units(expected, observed):
    return sorted(set(expected) - set(observed))


def file_plan(names):
    result = []
    for name in sorted(names):
        path = PurePosixPath(name)
        if path.name != name or path.suffix != ".csv" or "\\" in name or ":" in name:
            raise ValueError("Use a simple fictional CSV filename")
        result.append({"source": name, "destination": "review/" + name})
    return result


def flatten_answers(records):
    return [{"id": row["id"], "question": key, "answer": value}
            for row in records for key, value in row["answers"].items()]


def name_score(left, right):
    if not right:
        return 0.0
    overlap = Counter(word.casefold() for word in left) & Counter(word.casefold() for word in right)
    return sum(overlap.values()) / len(right)


def monthly_list(rows, run_date):
    end = run_date.replace(day=1)
    start = (end - timedelta(days=1)).replace(day=1)
    return [row for row in rows if start <= date.fromisoformat(row["submitted"]) < end]


def handover_cells(rows):
    return [{"floor": row["floor"], "unit": unit, "date": value}
            for row in rows for unit, value in row["units"].items()]


def writing_entries(text):
    parts = text.split("|")
    if len(parts) != 3:
        raise ValueError("Expected category|title|body")
    return dict(zip(("category", "title", "body"), parts))


def expand_references(rows):
    return [{"id": row["id"], "reference": token.strip()}
            for row in rows for token in row["references"].split(",") if token.strip()]
