from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import argparse

from errorprop_sql.workbook_seed import seed_workbook_reference_data
from errorprop_sql.workbook_sync import repair_workbook_layout


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed workbook reference data (models, prompts, tasks, and planned runs) for the free-model study."
    )
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--spider2-root")
    parser.add_argument("--model-suite", default=str(REPO_ROOT / "configs" / "free_model_suite.yaml"))
    parser.add_argument("--task-pack", default=str(REPO_ROOT / "configs" / "task_pack_zero_budget.yaml"))
    parser.add_argument("--study-protocol", default=str(REPO_ROOT / "configs" / "study_protocol_zero_budget.yaml"))
    parser.add_argument("--include-holdout", action="store_true")
    args = parser.parse_args()

    workbook_path = Path(args.workbook)
    spider2_root = Path(args.spider2_root) if args.spider2_root else None

    repair_workbook_layout(
        workbook_path,
        spider2_root=spider2_root,
        populate_tasks=False,
        drop_template_examples=True,
        clear_task_rows=True,
        clear_working_sheets=True,
    )
    seed_workbook_reference_data(
        workbook_path,
        repo_root=REPO_ROOT,
        model_suite_path=Path(args.model_suite),
        task_pack_path=Path(args.task_pack),
        study_protocol_path=Path(args.study_protocol),
        spider2_root=spider2_root,
        include_holdout=args.include_holdout,
    )
    print("Workbook reference data seeded successfully.")


if __name__ == "__main__":
    main()
