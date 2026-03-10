from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import argparse
from pathlib import Path

from errorprop_sql.runner import run_manual_trajectory

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--condition", required=True, choices=["F0", "F1", "F2", "F3"])
    parser.add_argument("--t-max", type=int, default=5)
    parser.add_argument("--spider2-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--reasoning-mode", default="none")
    parser.add_argument("--replicate", type=int, default=1)
    parser.add_argument("--batch-id", default="MAIN")
    parser.add_argument("--operator", default="")
    parser.add_argument("--prompt-dir", default="prompts")
    parser.add_argument("--timeout-sec", type=float, default=5.0)
    args = parser.parse_args()

    result = run_manual_trajectory(
        spider2_root=Path(args.spider2_root),
        out_dir=Path(args.out_dir),
        prompt_dir=Path(args.prompt_dir),
        model_label=args.model_label,
        instance_id=args.instance_id,
        condition=args.condition,
        t_max=args.t_max,
        temperature=args.temperature,
        reasoning_mode=args.reasoning_mode,
        replicate=args.replicate,
        batch_id=args.batch_id,
        operator=args.operator,
        timeout_sec=args.timeout_sec,
    )

    print("\nRun finished.")
    print(f"run_id: {result['run_id']}")
    print(f"final_state: {result['final_state']}")
    print(f"logged_turns: {result['logged_turns']}")
    print(f"run_dir: {result['run_dir']}")

if __name__ == "__main__":
    main()
