from __future__ import annotations

from copy import copy
from pathlib import Path

import openpyxl

from .utils import read_jsonl

TURN_LOG_HEADERS = [
    "batch_id",
    "run_id",
    "turn_no",
    "task_id",
    "db_name",
    "model_id",
    "protocol_id",
    "prompt_file",
    "response_file",
    "extracted_sql_file",
    "prompt_hash",
    "exec_ms",
    "rows_pred",
    "rows_gold",
    "symdiff_rows",
    "sqlite_error",
    "exec_state",
    "severity",
    "helper_key",
    "helper_prev_key",
    "prev_state",
    "prev_severity",
    "state_change",
    "improved",
    "regressed",
    "pass_flag",
    "feedback_file",
    "screenshot_file",
    "recording_timestamp",
    "notes",
    "review_flag",
]

RUN_PLAN_HEADERS = [
    "run_id",
    "batch_id",
    "task_id",
    "db_name",
    "model_id",
    "model_snapshot",
    "protocol_id",
    "temperature",
    "reasoning_mode",
    "T_max",
    "replicate",
    "operator",
    "planned_date",
    "record_file",
    "artifact_folder",
    "commit_hash",
    "status",
    "notes",
]

STABILITY_HEADERS = [
    "run_id",
    "pass_turn",
    "check_type",
    "repeat_no",
    "outcome_state",
    "stable_pass?",
    "evidence_file",
    "notes",
]


def _first_blank_row(ws, key_col: int) -> int:
    row = 5
    while ws.cell(row, key_col).value not in (None, ""):
        row += 1
    return row


def _copy_row_style(ws, source_row: int, target_row: int, max_col: int) -> None:
    for c in range(1, max_col + 1):
        src = ws.cell(source_row, c)
        dst = ws.cell(target_row, c)
        if src.has_style:
            dst._style = copy(src._style)
        dst.number_format = src.number_format
        dst.font = copy(src.font)
        dst.fill = copy(src.fill)
        dst.border = copy(src.border)
        dst.alignment = copy(src.alignment)
        dst.protection = copy(src.protection)
    ws.row_dimensions[target_row].height = ws.row_dimensions[source_row].height


def _formulaify_turn_log_row(ws, row: int) -> None:
    ws[f"R{row}"] = f'=IF(Q{row}="","",IFERROR(VLOOKUP(Q{row},Lookups!$A$2:$B$8,2,FALSE),""))'
    ws[f"S{row}"] = f'=IF(B{row}="","",B{row}&"|"&TEXT(C{row},"00"))'
    ws[f"T{row}"] = f'=IF(B{row}="","",B{row}&"|"&TEXT(C{row}-1,"00"))'
    ws[f"U{row}"] = f'=IFERROR(INDEX($Q$5:$Q$5000,MATCH(T{row},$S$5:$S$5000,0)),"")'
    ws[f"V{row}"] = f'=IFERROR(INDEX($R$5:$R$5000,MATCH(T{row},$S$5:$S$5000,0)),"")'
    ws[f"W{row}"] = f'=IF(U{row}="","",IF(Q{row}<>U{row},1,0))'
    ws[f"X{row}"] = f'=IF(V{row}="","",IF(R{row}<V{row},1,0))'
    ws[f"Y{row}"] = f'=IF(V{row}="","",IF(R{row}>V{row},1,0))'
    ws[f"Z{row}"] = f'=IF(Q{row}="","",IF(Q{row}="Pass",1,0))'


def _upsert_rows(
    ws,
    rows: list[dict],
    headers: list[str],
    dedupe_keys: list[str],
    key_col: int,
    style_source_row: int,
) -> None:
    row_index: dict[tuple, int] = {}
    header_to_col = {header: idx + 1 for idx, header in enumerate(headers)}

    for r in range(5, ws.max_row + 1):
        first = ws.cell(r, key_col).value
        if first in (None, ""):
            continue
        dedupe = tuple(ws.cell(r, header_to_col[k]).value for k in dedupe_keys)
        row_index[dedupe] = r

    for row in rows:
        dedupe = tuple(row.get(k) for k in dedupe_keys)
        target = row_index.get(dedupe)
        if target is None:
            target = _first_blank_row(ws, key_col)
            _copy_row_style(ws, style_source_row, target, len(headers))
            row_index[dedupe] = target

        for i, header in enumerate(headers, start=1):
            value = row.get(header)
            if value is not None:
                ws.cell(target, i).value = value


def _ensure_run_summary_rows(ws, run_plan_ws) -> None:
    target_last_row = max(run_plan_ws.max_row, 305)
    template_row = 5

    formulas_by_col = {
        "A": "=IF('Run Plan'!A{r}=\"\",\"\",'Run Plan'!A{r})",
        "B": "=IF(A{r}=\"\",\"\",'Run Plan'!C{r})",
        "C": "=IF(A{r}=\"\",\"\",'Run Plan'!E{r})",
        "D": "=IF(A{r}=\"\",\"\",'Run Plan'!G{r})",
        "E": "=IF(A{r}=\"\",\"\",'Run Plan'!K{r})",
        "F": "=IF(A{r}=\"\",\"\",'Run Plan'!J{r})",
        "G": "=IF(A{r}=\"\",\"\",COUNTIF('Turn Log'!$B$5:$B$5000,A{r}))",
        "H": "=IF(A{r}=\"\",\"\",IFERROR(MINIFS('Turn Log'!$C$5:$C$5000,'Turn Log'!$B$5:$B$5000,A{r},'Turn Log'!$Q$5:$Q$5000,\"Pass\"),\"\"))",
        "I": "=IF(A{r}=\"\",\"\",IFERROR(MAXIFS('Turn Log'!$C$5:$C$5000,'Turn Log'!$B$5:$B$5000,A{r}),\"\"))",
        "J": "=IF(A{r}=\"\",\"\",IFERROR(INDEX('Turn Log'!$Q$5:$Q$5000,MATCH(1,('Turn Log'!$B$5:$B$5000=A{r})*('Turn Log'!$C$5:$C$5000=I{r}),0)),\"\"))",
        "K": "=IF(A{r}=\"\",\"\",IFERROR(INDEX('Turn Log'!$R$5:$R$5000,MATCH(1,('Turn Log'!$B$5:$B$5000=A{r})*('Turn Log'!$C$5:$C$5000=I{r}),0)),\"\"))",
        "L": "=IF(A{r}=\"\",\"\",COUNTIFS('Turn Log'!$B$5:$B$5000,A{r},'Turn Log'!$X$5:$X$5000,1))",
        "M": "=IF(A{r}=\"\",\"\",COUNTIFS('Turn Log'!$B$5:$B$5000,A{r},'Turn Log'!$Y$5:$Y$5000,1))",
        "N": "=IF(A{r}=\"\",\"\",COUNTIFS('Turn Log'!$B$5:$B$5000,A{r},'Turn Log'!$W$5:$W$5000,1))",
        "O": "=IF(H{r}=\"\",\"No\",\"Yes\")",
        "P": "=IF(A{r}=\"\",\"\",COUNTIFS('Stability Checks'!$A$5:$A$2000,A{r},'Stability Checks'!$C$5:$C$2000,\"Re-execution\",'Stability Checks'!$E$5:$E$2000,\"Pass\"))",
        "Q": "=IF(A{r}=\"\",\"\",COUNTIFS('Stability Checks'!$A$5:$A$2000,A{r},'Stability Checks'!$C$5:$C$2000,\"Re-prompt\",'Stability Checks'!$E$5:$E$2000,\"Pass\"))",
        "R": "=IF(A{r}=\"\",\"\",'Run Plan'!Q{r})",
    }

    for row in range(5, target_last_row + 1):
        if row > ws.max_row or ws.cell(row, 1).value in (None, ""):
            _copy_row_style(ws, template_row, row, ws.max_column)

        for col_letter, template in formulas_by_col.items():
            ws[f"{col_letter}{row}"] = template.format(r=row)


def sync_output_to_workbook(workbook_path: Path, out_dir: Path) -> None:
    wb = openpyxl.load_workbook(workbook_path)
    run_plan_ws = wb["Run Plan"]
    turn_log_ws = wb["Turn Log"]
    stability_ws = wb["Stability Checks"]
    run_summary_ws = wb["Run Summary"]

    logs_dir = out_dir / "logs"
    run_plan_rows = read_jsonl(logs_dir / "run_plan.jsonl")
    turn_log_rows = read_jsonl(logs_dir / "turn_log.jsonl")
    stability_rows = read_jsonl(logs_dir / "stability_checks.jsonl")

    _upsert_rows(run_plan_ws, run_plan_rows, RUN_PLAN_HEADERS, ["run_id"], 1, 5)
    _upsert_rows(turn_log_ws, turn_log_rows, TURN_LOG_HEADERS, ["run_id", "turn_no"], 2, 7)
    _upsert_rows(stability_ws, stability_rows, STABILITY_HEADERS, ["run_id", "check_type", "repeat_no"], 1, 5)

    for r in range(5, turn_log_ws.max_row + 1):
        if turn_log_ws[f"B{r}"].value not in (None, ""):
            _formulaify_turn_log_row(turn_log_ws, r)

    _ensure_run_summary_rows(run_summary_ws, run_plan_ws)

    wb.calculation.fullCalcOnLoad = True
    wb.calculation.forceFullCalc = True
    wb.save(workbook_path)
