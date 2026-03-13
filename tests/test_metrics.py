from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from errorprop_sql.metrics import generate_analysis_tables


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_generate_analysis_tables_dedupes_run_plan_and_derives_regressions(tmp_path: Path) -> None:
    out_dir = tmp_path / "output"
    logs_dir = out_dir / "logs"

    _write_jsonl(
        logs_dir / "run_plan.jsonl",
        [
            {"run_id": "R1", "status": "In progress"},
            {"run_id": "R1", "status": "Complete"},
        ],
    )
    _write_jsonl(
        logs_dir / "turn_log.jsonl",
        [
            {"run_id": "R1", "turn_no": 1, "task_id": "local001", "model_id": "gpt-5.1", "protocol_id": "F1", "exec_state": "WrongResult"},
            {"run_id": "R1", "turn_no": 2, "task_id": "local001", "model_id": "gpt-5.1", "protocol_id": "F1", "exec_state": "SyntaxError"},
            {"run_id": "R1", "turn_no": 3, "task_id": "local001", "model_id": "gpt-5.1", "protocol_id": "F1", "exec_state": "Pass"},
        ],
    )

    paths = generate_analysis_tables(out_dir)
    assert any(path.endswith("run_plan.csv") for path in paths)
    assert any(path.endswith("run_plan_raw.csv") for path in paths)

    run_plan_df = pd.read_csv(out_dir / "analysis" / "run_plan.csv")
    assert len(run_plan_df) == 1
    assert run_plan_df.loc[0, "status"] == "Complete"

    run_summary_df = pd.read_csv(out_dir / "analysis" / "run_summary_from_logs.csv")
    assert int(run_summary_df.loc[0, "regressions"]) == 1
    assert int(run_summary_df.loc[0, "improvements"]) == 1
    assert int(run_summary_df.loc[0, "oscillations"]) == 2
