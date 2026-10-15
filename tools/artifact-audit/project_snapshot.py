"""Read-only snapshot of a CLOSED synthetic .agrolines project for future acceptance tests.

Never opens the application, enables SQLite extensions, migrates, or modifies a project.
Output contains hashes/counts, not row contents. Keep even these diagnostics private.
"""

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

TABLES = {"project", "feature", "revision", "source", "event"}


def snapshot(path):
    path = Path(path).resolve(strict=True)
    if path.suffix != ".agrolines":
        raise ValueError("Expected a synthetic .agrolines file")
    if any(Path(str(path) + suffix).exists() for suffix in ("-wal", "-shm", "-journal")):
        raise ValueError("Close application and settle SQLite sidecars before snapshot")
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        db.execute("PRAGMA query_only=ON")
        db.execute("PRAGMA trusted_schema=OFF")
        if db.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("SQLite integrity check failed")
        if db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite foreign-key integrity check failed")
        schema = db.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name"
        ).fetchall()
        version = db.execute("PRAGMA user_version").fetchone()[0]
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if tables != TABLES or version != 1:
            raise ValueError("Unknown schema: explicit migration review required")
        results = {}
        for table in sorted(TABLES):
            # Only literal names from the allowlist; no arbitrary SQL identifiers.
            rows = db.execute(f'SELECT * FROM "{table}"').fetchall()
            digests = sorted(
                hashlib.sha256(
                    json.dumps(
                        row,
                        ensure_ascii=True,
                        separators=(",", ":"),
                        default=lambda blob: {"blob_hex": blob.hex()},
                    ).encode()
                ).hexdigest()
                for row in rows
            )
            results[table] = {
                "rows": len(rows),
                "rows_sha256": hashlib.sha256(
                    json.dumps(digests, separators=(",", ":")).encode()
                ).hexdigest(),
            }
    after = hashlib.sha256(path.read_bytes()).hexdigest()
    if before != after:
        raise ValueError("Project changed during inspection")
    return {
        "schema_sha256": hashlib.sha256(
            json.dumps(schema, separators=(",", ":")).encode()
        ).hexdigest(),
        "schema_version": version,
        "file_sha256": after,
        "tables": results,
        "read_only": True,
        "closed_synthetic_project_required": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    args = parser.parse_args()
    print(json.dumps(snapshot(args.project), indent=2))


if __name__ == "__main__":
    main()
