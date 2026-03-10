from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import argparse
from pathlib import Path

from errorprop_sql.metrics import generate_analysis_tables

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    paths = generate_analysis_tables(Path(args.out_dir))
    print("Analysis artifacts:")
    for p in paths:
        print(f"- {p}")

if __name__ == "__main__":
    main()
