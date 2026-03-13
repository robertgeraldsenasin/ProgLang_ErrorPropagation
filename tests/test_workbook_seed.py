from __future__ import annotations

import shutil
from pathlib import Path

from openpyxl import load_workbook

from errorprop_sql.workbook_seed import seed_workbook_reference_data


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKBOOK_TEMPLATE = REPO_ROOT / "workbook" / "Experiment_ProgLang_Error_Propagation_repo.xlsx"
SAMPLE_ROOT = REPO_ROOT / "samples" / "mini_spider2"


def test_seed_workbook_reference_data_populates_lookups_tasks_and_run_plan(tmp_path: Path) -> None:
    workbook_path = tmp_path / "seed_test.xlsx"
    shutil.copy2(WORKBOOK_TEMPLATE, workbook_path)

    seed_workbook_reference_data(
        workbook_path,
        repo_root=REPO_ROOT,
        model_suite_path=REPO_ROOT / "configs" / "free_model_suite.yaml",
        task_pack_path=REPO_ROOT / "configs" / "task_pack_zero_budget.yaml",
        study_protocol_path=REPO_ROOT / "configs" / "study_protocol_zero_budget.yaml",
        spider2_root=SAMPLE_ROOT,
        include_holdout=False,
    )

    wb = load_workbook(workbook_path, data_only=False)
    lookups = wb["Lookups"]
    tasks = wb["Tasks"]
    run_plan = wb["Run Plan"]
    prompt_library = wb["Prompt Library"]

    assert lookups["G2"].value == "chatgpt-free-gpt-5.3"
    assert prompt_library["A5"].value == "T1_SQL"
    assert "{supporting_context}" in str(prompt_library["D5"].value)

    # Only local001 is available in the sample root, so unknown tasks fall back to blank db/question rows.
    assert tasks["A5"].value == "local002"
    assert tasks["K5"].value == "PILOT"

    seeded_run_ids = [run_plan[f"A{row}"].value for row in range(5, 30) if run_plan[f"A{row}"].value]
    assert any("CHATGPT-FREE-GPT-5-3" in run_id for run_id in seeded_run_ids)
    assert any(run_id.endswith("-F2-R1") for run_id in seeded_run_ids)
