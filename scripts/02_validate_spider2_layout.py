from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import argparse
from pathlib import Path

from errorprop_sql.task_loader import validate_spider2_layout, load_tasks_from_root

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spider2-root", required=True, help="Path to the cloned Spider2 repo root.")
    parser.add_argument("--show-local", action="store_true", help="List the first 20 local/SQLite task ids.")
    args = parser.parse_args()

    report = validate_spider2_layout(Path(args.spider2_root))
    print("Validation report:")
    for key, value in report.items():
        print(f"- {key}: {value}")

    if args.show_local:
        tasks = load_tasks_from_root(Path(args.spider2_root))
        local_ids = [t.instance_id for t in tasks if str(t.instance_id).startswith("local")]
        print("\nFirst local task ids:")
        for task_id in local_ids[:20]:
            print(task_id)

if __name__ == "__main__":
    main()
