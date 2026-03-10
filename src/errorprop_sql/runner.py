from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .executor import execute_sqlite
from .feedback import build_feedback_payload
from .oracle import compare_with_oracle, load_oracle_result
from .schema_utils import dump_sqlite_schema
from .sql_extract import extract_sql
from .states import classify_state
from .task_loader import get_task_by_id, resolve_sqlite_db_path
from .utils import append_jsonl, ensure_dir, safe_model_slug, sha1_text

def _load_template(prompt_dir: Path, name: str) -> str:
    return (prompt_dir / name).read_text(encoding="utf-8")

def _manual_collect_response() -> str:
    print("\nPaste the model response below.")
    print("Finish with a line that contains only: END")
    print("Or provide FILE:/absolute/or/relative/path/to/response.txt")
    lines: list[str] = []
    first = input("> ").rstrip("\n")
    if first.startswith("FILE:"):
        path = Path(first[5:].strip())
        return path.read_text(encoding="utf-8")
    if first == "END":
        return ""
    lines.append(first)
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)
    return "\n".join(lines)

def _make_run_id(instance_id: str, model_label: str, condition: str, replicate: int) -> str:
    return f"{instance_id.upper()}-{safe_model_slug(model_label).upper()}-{condition}-R{replicate}"

def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def run_manual_trajectory(
    *,
    spider2_root: Path,
    out_dir: Path,
    prompt_dir: Path,
    model_label: str,
    instance_id: str,
    condition: str,
    t_max: int,
    temperature: float,
    reasoning_mode: str,
    replicate: int,
    batch_id: str,
    operator: str,
    timeout_sec: float,
) -> dict[str, Any]:
    prompt_dir = prompt_dir
    out_dir = out_dir
    for sub in ["prompts", "responses", "sql", "feedback", "logs", "runs"]:
        ensure_dir(out_dir / sub)

    task = get_task_by_id(spider2_root, instance_id)
    db_path = resolve_sqlite_db_path(spider2_root, task.db)
    schema_dump = dump_sqlite_schema(db_path, sample_rows_per_table=0)
    oracle = load_oracle_result(spider2_root, task.instance_id, db_path)

    run_id = _make_run_id(instance_id, model_label, condition, replicate)
    run_dir = ensure_dir(out_dir / "runs" / run_id)

    now_iso = datetime.now().isoformat(timespec="seconds")

    run_plan_row = {
        "run_id": run_id,
        "batch_id": batch_id,
        "task_id": task.instance_id,
        "db_name": task.db,
        "model_id": model_label,
        "model_snapshot": model_label,
        "protocol_id": condition,
        "temperature": temperature,
        "reasoning_mode": reasoning_mode,
        "T_max": t_max,
        "replicate": replicate,
        "operator": operator,
        "planned_date": now_iso[:10],
        "record_file": "",
        "artifact_folder": str(run_dir.relative_to(out_dir)),
        "commit_hash": "",
        "status": "In progress",
        "notes": "",
    }
    append_jsonl(out_dir / "logs" / "run_plan.jsonl", run_plan_row)

    previous_sql = None
    final_state = None
    turns_logged = 0
    pass_turn = None

    for turn_no in range(1, t_max + 1):
        if turn_no == 1:
            template = _load_template(prompt_dir, "turn1_sql.txt")
            prompt_text = template.format(
                db_name=task.db,
                schema_dump=schema_dump,
                question=task.question,
            )
        else:
            template = _load_template(prompt_dir, f"revise_{condition}.txt")
            prompt_text = template.format(
                previous_sql=previous_sql,
                feedback_payload=feedback_payload,
            )

        prompt_file = out_dir / "prompts" / f"{run_id}_turn{turn_no:02d}.txt"
        _write_text(prompt_file, prompt_text)
        print("\n" + "=" * 80)
        print(f"Turn {turn_no} prompt saved to: {prompt_file}")
        print("Open the file, paste it into the model, then paste the model reply back here.")
        response_text = _manual_collect_response()

        response_file = out_dir / "responses" / f"{run_id}_turn{turn_no:02d}.txt"
        _write_text(response_file, response_text)

        extracted_sql, extraction_mode = extract_sql(response_text)
        format_error = extracted_sql is None
        sql_file = out_dir / "sql" / f"{run_id}_turn{turn_no:02d}.sql"
        _write_text(sql_file, extracted_sql or "")

        if format_error:
            exec_result = None
            comparison = None
            state = classify_state(format_error=True, execution_result=None, comparison=None)
            sqlite_error = "Model response did not contain extractable SQL."
            rows_pred = None
            rows_gold = len(oracle.rows)
            symdiff_rows = None
            feedback_payload = "The previous response did not contain a valid SQL query. Return one SQLite SQL query only."
        else:
            exec_result = execute_sqlite(db_path, extracted_sql, timeout_sec=timeout_sec)
            comparison = compare_with_oracle(extracted_sql, exec_result, oracle) if exec_result.ok else None
            state = classify_state(format_error=False, execution_result=exec_result, comparison=comparison)
            sqlite_error = exec_result.error_message
            rows_pred = comparison.rows_pred if comparison else None
            rows_gold = comparison.rows_gold if comparison else len(oracle.rows)
            symdiff_rows = comparison.symdiff_rows if comparison else None
            if state != "Pass":
                feedback_payload = build_feedback_payload(condition, state, exec_result, comparison)

        feedback_file = out_dir / "feedback" / f"{run_id}_turn{turn_no:02d}.txt"
        _write_text(feedback_file, feedback_payload if state != "Pass" else "PASS")

        turn_row = {
            "batch_id": batch_id,
            "run_id": run_id,
            "turn_no": turn_no,
            "task_id": task.instance_id,
            "db_name": task.db,
            "model_id": model_label,
            "protocol_id": condition,
            "prompt_file": str(prompt_file.relative_to(out_dir)),
            "response_file": str(response_file.relative_to(out_dir)),
            "extracted_sql_file": str(sql_file.relative_to(out_dir)),
            "prompt_hash": sha1_text(prompt_text),
            "exec_ms": getattr(exec_result, "runtime_ms", None),
            "rows_pred": rows_pred,
            "rows_gold": rows_gold,
            "symdiff_rows": symdiff_rows,
            "sqlite_error": sqlite_error,
            "exec_state": state,
            "feedback_file": str(feedback_file.relative_to(out_dir)),
            "screenshot_file": "",
            "recording_timestamp": datetime.now().strftime("%H:%M:%S"),
            "notes": f"extraction={extraction_mode}",
            "review_flag": "",
        }
        append_jsonl(out_dir / "logs" / "turn_log.jsonl", turn_row)

        turns_logged += 1
        previous_sql = extracted_sql or previous_sql
        final_state = state

        print(f"Turn {turn_no} state: {state}")
        if state == "Pass":
            pass_turn = turn_no
            break

    # Mark completion state in a second run_plan entry for traceability
    run_plan_done = dict(run_plan_row)
    run_plan_done["status"] = "Complete"
    run_plan_done["notes"] = f"final_state={final_state}; pass_turn={pass_turn}"
    append_jsonl(out_dir / "logs" / "run_plan.jsonl", run_plan_done)

    summary = {
        "run_id": run_id,
        "final_state": final_state,
        "logged_turns": turns_logged,
        "pass_turn": pass_turn,
        "run_dir": str(run_dir),
    }
    _write_text(run_dir / "summary.json", json.dumps(summary, indent=2))
    return summary

def run_reexecution_stability_checks(
    *,
    run_id: str,
    spider2_root: Path,
    out_dir: Path,
    repeats: int,
    timeout_sec: float,
) -> list[dict[str, Any]]:
    import pandas as pd
    from .task_loader import get_task_by_id

    logs_path = out_dir / "logs" / "turn_log.jsonl"
    if not logs_path.exists():
        raise FileNotFoundError("No turn log found.")

    df = pd.read_json(logs_path, lines=True)
    run_df = df[df["run_id"] == run_id].sort_values("turn_no")
    if run_df.empty:
        raise KeyError(f"Run not found: {run_id}")

    pass_rows = run_df[run_df["exec_state"] == "Pass"]
    if pass_rows.empty:
        raise ValueError(f"Run {run_id} never reached Pass.")

    final_pass = pass_rows.iloc[-1]
    sql_rel = final_pass["extracted_sql_file"]
    sql_path = out_dir / sql_rel
    sql = Path(sql_path).read_text(encoding="utf-8")
    task = get_task_by_id(spider2_root, str(final_pass["task_id"]))
    db_path = resolve_sqlite_db_path(spider2_root, str(task.db))
    oracle = load_oracle_result(spider2_root, task.instance_id, db_path)

    rows_out: list[dict[str, Any]] = []
    for repeat_no in range(1, repeats + 1):
        exec_result = execute_sqlite(db_path, sql, timeout_sec=timeout_sec)
        comparison = compare_with_oracle(sql, exec_result, oracle) if exec_result.ok else None
        state = classify_state(format_error=False, execution_result=exec_result, comparison=comparison)
        row = {
            "run_id": run_id,
            "pass_turn": int(final_pass["turn_no"]),
            "check_type": "Re-execution",
            "repeat_no": repeat_no,
            "outcome_state": state,
            "stable_pass?": "Yes" if state == "Pass" else "No",
            "evidence_file": str(Path(sql_rel)),
            "notes": "",
        }
        append_jsonl(out_dir / "logs" / "stability_checks.jsonl", row)
        rows_out.append(row)
    return rows_out
