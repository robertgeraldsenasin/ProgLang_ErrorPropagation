from __future__ import annotations

from .executor import ExecutionResult
from .oracle import ComparisonResult

def render_sample_rows(rows: list[tuple[str, ...]]) -> str:
    if not rows:
        return "[]"
    return "[" + "; ".join(str(r) for r in rows) + "]"

def build_feedback_payload(
    condition: str,
    state: str,
    execution_result: ExecutionResult,
    comparison: ComparisonResult | None,
) -> str:
    if condition == "F0":
        return "Result: FAIL."

    if condition == "F1":
        if not execution_result.ok:
            return f"Execution failed.\nSQLite error:\n{execution_result.error_message}"
        return "Query executed but the output is incorrect. Result: FAIL."

    if condition in {"F2", "F3"}:
        if not execution_result.ok:
            return f"Execution failed.\nSQLite error:\n{execution_result.error_message}"
        assert comparison is not None
        return (
            "Query executed but output is incorrect.\n"
            f"Gold row_count = {comparison.rows_gold}\n"
            f"Pred row_count = {comparison.rows_pred}\n"
            f"Symmetric difference rows = {comparison.symdiff_rows}\n"
            f"Example gold rows: {render_sample_rows(comparison.gold_sample)}\n"
            f"Example predicted rows: {render_sample_rows(comparison.pred_sample)}"
        )

    raise ValueError(f"Unknown feedback condition: {condition}")
