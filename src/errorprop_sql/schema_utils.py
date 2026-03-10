from __future__ import annotations

import sqlite3
from pathlib import Path

def dump_sqlite_schema(db_path: Path, sample_rows_per_table: int = 0) -> str:
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables = cur.fetchall()
        chunks: list[str] = []
        for table_name, create_sql in tables:
            chunks.append(create_sql.rstrip(";") + ";")
            fk_rows = conn.execute(f"PRAGMA foreign_key_list('{table_name}')").fetchall()
            if fk_rows:
                fk_desc = ", ".join(
                    f"{row[3]} -> {row[2]}.{row[4]}" for row in fk_rows
                )
                chunks.append(f"-- Foreign keys: {fk_desc}")
            if sample_rows_per_table > 0:
                sample = conn.execute(
                    f"SELECT * FROM '{table_name}' LIMIT {int(sample_rows_per_table)}"
                ).fetchall()
                if sample:
                    chunks.append(f"-- Sample rows from {table_name}:")
                    for row in sample:
                        chunks.append("-- " + repr(tuple(row)))
            chunks.append("")
        return "\n".join(chunks).strip()
    finally:
        conn.close()
