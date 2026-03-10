\
from __future__ import annotations

import re

SQL_BLOCK_RE = re.compile(r"```sql\s*(.*?)```", re.IGNORECASE | re.DOTALL)
ANY_BLOCK_RE = re.compile(r"```(?:\w+)?\s*(.*?)```", re.DOTALL)

def extract_sql(response_text: str) -> tuple[str | None, str]:
    text = (response_text or "").strip()
    if not text:
        return None, "empty_response"

    sql_match = SQL_BLOCK_RE.search(text)
    if sql_match:
        return sql_match.group(1).strip(), "sql_fenced_block"

    any_match = ANY_BLOCK_RE.search(text)
    if any_match:
        block = any_match.group(1).strip()
        return block if block else None, "generic_fenced_block"

    lowered = text.lower().lstrip()
    starters = ("select", "with", "insert", "update", "delete", "create", "drop")
    if lowered.startswith(starters):
        return text.strip(), "raw_sql"

    return None, "no_sql_detected"

def has_explicit_order_by(sql: str | None) -> bool:
    if not sql:
        return False
    return " order by " in f" {sql.lower()} "
