from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from errorprop_sql.runner import run_manual_trajectory, run_reexecution_stability_checks
from errorprop_sql.workbook_driver import current_git_commit, load_run_request, update_run_plan_row
from errorprop_sql.workbook_sync import sync_output_to_workbook


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run one planned trajectory directly from the workbook, then sync Run Plan, Turn Log, and Stability Checks."
    )
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--spider2-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--row", type=int, help="Run Plan row number to execute (data rows start at 5).")
    parser.add_argument("--run-id", help="Alternative to --row: execute the row matching this run_id.")
    parser.add_argument("--prompt-dir", default="prompts")
    parser.add_argument("--timeout-sec", type=float, default=5.0)
    parser.add_argument("--operator", default="")
    parser.add_argument("--record-file", default="")
    parser.add_argument("--commit-hash", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--run-stability-on-pass", action="store_true")
    parser.add_argument("--stability-repeats", type=int, default=3)
    args = parser.parse_args()

    workbook_path = Path(args.workbook)
    spider2_root = Path(args.spider2_root)
    out_dir = Path(args.out_dir)

    request = load_run_request(workbook_path, row=args.row, run_id=args.run_id)
    commit_hash = args.commit_hash or request.commit_hash or current_git_commit(REPO_ROOT)
    operator = args.operator or request.operator
    record_file = args.record_file or request.record_file
    notes = " | ".join(part for part in [request.notes, args.notes] if part)

    update_run_plan_row(
        workbook_path,
        request.row_index,
        {
            "run_id": request.run_id,
            "planned_date": request.planned_date,
            "artifact_folder": request.artifact_folder,
            "commit_hash": commit_hash,
            "operator": operator,
            "record_file": record_file,
            "status": "In progress",
            "notes": notes,
        },
    )

    result = run_manual_trajectory(
        spider2_root=spider2_root,
        out_dir=out_dir,
        prompt_dir=Path(args.prompt_dir),
        model_label=request.model_id,
        instance_id=request.task_id,
        condition=request.protocol_id,
        t_max=request.t_max,
        temperature=request.temperature,
        reasoning_mode=request.reasoning_mode,
        replicate=request.replicate,
        batch_id=request.batch_id,
        operator=operator,
        timeout_sec=args.timeout_sec,
        model_snapshot=request.model_snapshot,
        planned_date=request.planned_date,
        record_file=record_file,
        commit_hash=commit_hash,
        notes=notes,
    )
    sync_output_to_workbook(workbook_path, out_dir)

    update_run_plan_row(
        workbook_path,
        request.row_index,
        {
            "db_name": result["db_name"],
            "artifact_folder": request.artifact_folder,
            "commit_hash": commit_hash,
            "operator": operator,
            "record_file": record_file,
            "status": "Complete",
        },
    )

    if args.run_stability_on_pass and result["final_state"] == "Pass":
        run_reexecution_stability_checks(
            run_id=result["run_id"],
            spider2_root=spider2_root,
            out_dir=out_dir,
            repeats=args.stability_repeats,
            timeout_sec=args.timeout_sec,
        )
        sync_output_to_workbook(workbook_path, out_dir)

    print("\nWorkbook-driven run finished.")
    print(f"run_id: {result['run_id']}")
    print(f"final_state: {result['final_state']}")
    print(f"logged_turns: {result['logged_turns']}")
    print(f"run_dir: {result['run_dir']}")


if __name__ == "__main__":
    main()
