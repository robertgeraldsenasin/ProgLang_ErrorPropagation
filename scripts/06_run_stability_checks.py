from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import argparse
from pathlib import Path

from errorprop_sql.runner import run_reexecution_stability_checks

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--spider2-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout-sec", type=float, default=5.0)
    args = parser.parse_args()

    results = run_reexecution_stability_checks(
        run_id=args.run_id,
        spider2_root=Path(args.spider2_root),
        out_dir=Path(args.out_dir),
        repeats=args.repeats,
        timeout_sec=args.timeout_sec,
    )

    print("Stability check results:")
    for row in results:
        print(row)

if __name__ == "__main__":
    main()
