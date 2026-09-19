"""Synthetic offline course pipeline: stdlib only, no production/network access."""
import argparse
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

FIELDS = ["id", "name", "hkid_hash", "phone", "email"]
SAMPLES = {
    "roi": [
        ["R001", "ADA", "hash-a", "100", "ada@example.invalid"],
        ["R002", "BOB", "hash-b", "200", ""],
        ["R003", "CARA", "hash-c", "", "cara@example.invalid"],
        ["R004", "DAN", "hash-d", "400", "dan@example.invalid"],
        ["R005", "ERIN", "", "500", ""],
        ["R006", "FINN", "hash-f", "", ""],
        ["R007", "GIA", "hash-g", "700", "gia@example.invalid"],
        ["R008", "HAN", "hash-h", "800", "han@example.invalid"],
    ],
    "buyer": [
        ["B001", "ADA", "hash-a", "999", "different@example.invalid"],
        ["B002", "BOB", "hash-b", "200", ""],
        ["B003", "CARA", "hash-different", "", "cara@example.invalid"],
        ["B004", "DAN", "hash-d", "400", "dan@example.invalid"],
        ["B005", "ERIN", "", "500", ""],
        ["B006", "FINN", "hash-f", "", ""],
        ["B007", "GIA", "hash-g", "700", "gia@example.invalid"],
    ],
    "members": [
        ["M001", "ADA", "", "100", "ada@example.invalid"],
        ["M002", "BOB", "", "200", ""],
        ["M003", "CARA", "", "", "cara@example.invalid"],
        ["M004", "DAN", "", "400", "other@example.invalid"],
        ["M005", "DAN", "", "999", "dan@example.invalid"],
        ["M006", "ERIN", "", "500", ""],
        ["M007", "GIA", "", "700", "gia@example.invalid"],
        ["M008", "FINN", "", "", ""],
    ],
}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def seed(root):
    raw = root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for source, rows in SAMPLES.items():
        path = raw / (source + ".csv")
        if not path.exists():
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(FIELDS)
                writer.writerows(rows)

def load_rows(root, source):
    with (root / "raw" / (source + ".csv")).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError("SCHEMA_ERROR: " + source)
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("MALFORMED_ROW: " + source)
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)) or any(not value for value in ids):
        raise ValueError("ID_ERROR: " + source)
    if any(not row["name"].strip() for row in rows):
        raise ValueError("NAME_ERROR: " + source)
    return rows

def extract(root):
    batch = {source: load_rows(root, source) for source in SAMPLES}
    fingerprint = digest(batch)
    path = root / "snapshots" / (fingerprint + ".json")
    if path.exists():
        if read(path) != batch:
            raise ValueError("SNAPSHOT_CHANGED")
    else:
        save(path, batch)
    save(root / "manifest.json", {"snapshot": str(path), "sha256": fingerprint})
    return batch

def reference(batch):
    """Small-data correctness oracle; O(n*m), not production ETL."""
    rb = sorted([
        [r["id"], b["id"]] for r in batch["roi"] for b in batch["buyer"]
        if r["name"] and r["hkid_hash"] and r["name"] == b["name"]
        and r["hkid_hash"] == b["hkid_hash"]
    ])
    candidates = set()
    for source in ("roi", "buyer"):
        for row in batch[source]:
            for member in batch["members"]:
                name = bool(row["name"]) and row["name"] == member["name"]
                phone = bool(row["phone"]) and row["phone"] == member["phone"]
                email = bool(row["email"]) and row["email"] == member["email"]
                if name and (phone or email):
                    candidates.add((source, row["id"], member["id"]))
    decisions = []
    for source in ("roi", "buyer"):
        for row in batch[source]:
            members = sorted(c[2] for c in candidates if c[:2] == (source, row["id"]))
            status = "unmatched" if not members else "matched" if len(members) == 1 else "ambiguous"
            decisions.append({"source": source, "id": row["id"], "status": status, "members": members})
    return {"roi_buyer": rb, "member_candidates": sorted(map(list, candidates)), "decisions": decisions}

def snapshot(root):
    manifest = read(root / "manifest.json")
    batch = read(Path(manifest["snapshot"]))
    if digest(batch) != manifest["sha256"]:
        raise ValueError("SNAPSHOT_HASH_MISMATCH")
    return batch

def match(root):
    result = reference(snapshot(root))
    save(root / "result.json", result)
    return result

def validate(root):
    result = read(root / "result.json")
    if result != reference(snapshot(root)):
        raise ValueError("RESULT_MISMATCH")
    summary = {s: sum(row["status"] == s for row in result["decisions"])
               for s in ("matched", "ambiguous", "unmatched")}
    summary.update(roi_buyer_pairs=len(result["roi_buyer"]), member_candidate_pairs=len(result["member_candidates"]))
    save(root / "quality.json", summary)
    return summary

def deliver(root, fail_after_commit=False):
    """Receiver-side deduplication in one local DB transaction, not a real API."""
    validate(root)
    rows = [row for row in read(root / "result.json")["decisions"] if row["status"] == "matched"]
    with sqlite3.connect(root / "mock_crm.sqlite") as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS deliveries (operation_key TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        before = connection.total_changes
        for row in rows:
            connection.execute("INSERT OR IGNORE INTO deliveries VALUES (?, ?)",
                               (digest(row), json.dumps(row, sort_keys=True)))
        inserted = connection.total_changes - before
        total = connection.execute("SELECT COUNT(*) FROM deliveries").fetchone()[0]
    if fail_after_commit:
        raise RuntimeError("SIMULATED_TIMEOUT_AFTER_COMMIT: retry with the same input")
    summary = {"inserted": inserted, "total": total}
    save(root / "delivery.json", summary)
    return summary

def self_check(root):
    if any(root.iterdir()):
        raise ValueError("Self-check needs a new empty workspace")
    seed(root)
    extract(root)
    result = match(root)
    assert validate(root) == {"matched": 9, "ambiguous": 2, "unmatched": 4,
                              "roi_buyer_pairs": 5, "member_candidate_pairs": 13}
    try:
        deliver(root, True)
    except RuntimeError as error:
        assert "SIMULATED_TIMEOUT" in str(error)
    else:
        raise AssertionError("Failure injection did not fail")
    assert deliver(root) == {"inserted": 0, "total": 9}
    assert deliver(root) == {"inserted": 0, "total": 9}
    invalid = read(root / "result.json")
    invalid["roi_buyer"].append(["R005", "B005"])
    save(root / "result.json", invalid)
    try:
        validate(root)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid result accepted")
    match(root)
    assert ["R001", "B001"] in result["roi_buyer"]
    assert ["R003", "B003"] not in result["roi_buyer"]
    assert ["roi", "R006", "M008"] not in result["member_candidates"]
    assert sum(c[:2] == ["roi", "R007"] for c in result["member_candidates"]) == 1
    print("SELF_CHECK_PASS: matching, quarantine, replay, committed-failure recovery, bad-result rejection")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["seed", "extract", "match", "validate", "deliver", "run", "self-check"])
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--fail-after-commit", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    root.mkdir(parents=True, exist_ok=True)
    if args.command == "self-check":
        self_check(root)
    elif args.command == "run":
        seed(root)
        extract(root)
        match(root)
        validate(root)
        print(json.dumps(deliver(root, args.fail_after_commit)))
    elif args.command == "deliver":
        print(json.dumps(deliver(root, args.fail_after_commit)))
    else:
        result = globals()[args.command](root)
        print(json.dumps(result if args.command == "validate" else {"stage": args.command, "workspace": str(root)}))

if __name__ == "__main__":
    main()
