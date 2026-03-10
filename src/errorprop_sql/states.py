from __future__ import annotations

import re

from .config import ERROR_SEVERITY
from .executor import ExecutionResult
from .oracle import ComparisonResult

SYNTAX_PATTERNS = [
    r"syntax error",
    r"incomplete input",
    r"unrecognized token",
    r"unterminated",
]

SCHEMA_PATTERNS = [
    r"no such table",
    r"no such column",
    r"ambiguous column name",
    r"has no column named",
    r"unknown column",
    r"cannot join using column",
]

def classify_state(
    *,
    format_error: bool,
    execution_result: ExecutionResult | None,
    comparison: ComparisonResult | None,
) -> str:
    if format_error:
        return "FormatError"
    if execution_result is None:
        return "FormatError"
    if execution_result.timed_out:
        return "Timeout"
    if execution_result.ok:
        return "Pass" if comparison and comparison.same else "WrongResult"

    msg = (execution_result.error_message or "").lower()
    for pattern in SYNTAX_PATTERNS:
        if re.search(pattern, msg):
            return "SyntaxError"
    for pattern in SCHEMA_PATTERNS:
        if re.search(pattern, msg):
            return "SchemaError"
    return "RuntimeError"

def severity_for_state(state: str) -> int:
    return ERROR_SEVERITY[state]
