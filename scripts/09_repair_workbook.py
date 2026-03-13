from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import argparse

from errorprop_sql.workbook_sync import repair_workbook_layout


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair workbook formulas/layout and optionally repopulate the Tasks sheet from Spider2-Lite.")
    parser.add_argument("--workbook", required=True)
    parser.add_argument("--spider2-root")
    parser.add_argument("--populate-tasks", action="store_true")
    parser.add_argument("--keep-template-examples", action="store_true")
    parser.add_argument("--clear-task-rows", action="store_true")
    parser.add_argument("--clear-working-sheets", action="store_true")
    args = parser.parse_args()

    repair_workbook_layout(
        Path(args.workbook),
        drop_template_examples=not args.keep_template_examples,
        clear_task_rows=args.clear_task_rows,
        clear_working_sheets=args.clear_working_sheets,
        spider2_root=Path(args.spider2_root) if args.spider2_root else None,
        populate_tasks=args.populate_tasks,
    )
    print("Workbook repair complete.")


if __name__ == "__main__":
    main()
