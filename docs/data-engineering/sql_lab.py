"""Read-only SQL practice over a pinned, fictional course snapshot (stdlib only)."""
import argparse
import json
import sqlite3
from pathlib import Path

from lab import seed, extract, snapshot, reference

DEFAULT_QUERY = "SELECT source, COUNT(*) AS record_count FROM source_records GROUP BY source ORDER BY source"
CONTRACTS = {
    "roi-buyer": (["roi_id", "buyer_id"], "roi_buyer"),
    "member-candidates": (["source", "record_id", "member_id"], "member_candidates"),
}


def query(batch, sql):
    """Only SELECT/read operations are allowed; the database never persists."""
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE source_records (source TEXT, record_id TEXT, name TEXT, hkid_hash TEXT, phone TEXT, email TEXT)")
        connection.execute("CREATE TABLE members (member_id TEXT, name TEXT, hkid_hash TEXT, phone TEXT, email TEXT)")
        fields = ("id", "name", "hkid_hash", "phone", "email")
        for source in ("roi", "buyer"):
            connection.executemany("INSERT INTO source_records VALUES (?, ?, ?, ?, ?, ?)",
                                   [(source, *(row[key] or None for key in fields)) for row in batch[source]])
        connection.executemany("INSERT INTO members VALUES (?, ?, ?, ?, ?)",
                               [tuple(row[key] or None for key in fields) for row in batch["members"]])
        connection.commit()
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
        def authorize(action, first, second, database, trigger):
            if action == sqlite3.SQLITE_FUNCTION and str(second).lower() == "load_extension":
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY
        connection.set_authorizer(authorize)
        # Bound accidental recursive queries; this is a local learning aid, not a hostile-code sandbox.
        remaining = [10000]
        def budget():
            remaining[0] -= 1
            return int(remaining[0] <= 0)
        connection.set_progress_handler(budget, 1000)
        cursor = connection.execute(sql)
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchmany(10001)
        if len(rows) > 10000:
            raise ValueError("RESULT_TOO_LARGE: limit this learning query to 10000 rows")
        return columns, [list(row) for row in rows]
    finally:
        connection.close()


def check(batch, columns, rows, expectation):
    expected_columns, key = CONTRACTS[expectation]
    expected = reference(batch)[key]
    if columns != expected_columns:
        raise ValueError("COLUMN_MISMATCH: expected " + repr(expected_columns))
    if any(any(not isinstance(value, str) for value in row) for row in rows):
        raise ValueError("VALUE_MISMATCH: identity columns must contain non-null strings")
    if sorted(rows) != expected:
        raise ValueError("ROW_MISMATCH: compare exact identities, duplicates and missing edges")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    queries = parser.add_mutually_exclusive_group()
    queries.add_argument("--sql")
    queries.add_argument("--query-file", type=Path)
    parser.add_argument("--expect", choices=CONTRACTS)
    args = parser.parse_args()
    root = args.workspace.resolve()
    if not (root / "manifest.json").exists():
        seed(root)
        extract(root)
    batch = snapshot(root)
    sql = args.query_file.read_text(encoding="utf-8-sig") if args.query_file else args.sql or DEFAULT_QUERY
    columns, rows = query(batch, sql)
    if args.expect:
        check(batch, columns, rows, args.expect)
    print(json.dumps({"columns": columns, "rows": rows, "row_count": len(rows),
                      "check": "EXACT_ROWS_PASS_NOT_MASTERY" if args.expect else "NOT_REQUESTED"}, indent=2))


if __name__ == "__main__":
    main()
