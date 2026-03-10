from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .config import ERROR_SEVERITY

def _read_log(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_json(path, lines=True)

def generate_analysis_tables(out_dir: Path) -> list[str]:
    logs_dir = out_dir / "logs"
    analysis_dir = out_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    turn_df = _read_log(logs_dir / "turn_log.jsonl")
    run_df = _read_log(logs_dir / "run_plan.jsonl")
    stability_df = _read_log(logs_dir / "stability_checks.jsonl")

    generated: list[str] = []

    if not turn_df.empty:
        turn_df["severity"] = turn_df["exec_state"].map(ERROR_SEVERITY)
        if "regressed" not in turn_df.columns:
            turn_df["regressed"] = 0
        turn_csv = analysis_dir / "turn_log.csv"
        turn_df.to_csv(turn_csv, index=False)
        generated.append(str(turn_csv))

        turn_df["prev_state"] = turn_df.groupby("run_id")["exec_state"].shift(1)
        trans = (
            turn_df.dropna(subset=["prev_state"])
            .groupby(["prev_state", "exec_state"])
            .size()
            .reset_index(name="count")
        )
        trans_csv = analysis_dir / "transition_counts.csv"
        trans.to_csv(trans_csv, index=False)
        generated.append(str(trans_csv))

        by_turn = (
            turn_df.groupby(["turn_no", "exec_state"])
            .size()
            .reset_index(name="count")
            .sort_values(["turn_no", "exec_state"])
        )
        by_turn_csv = analysis_dir / "state_distribution_by_turn.csv"
        by_turn.to_csv(by_turn_csv, index=False)
        generated.append(str(by_turn_csv))

        # Simple plot
        pivot = by_turn.pivot(index="turn_no", columns="exec_state", values="count").fillna(0)
        ax = pivot.plot(kind="bar", stacked=True, figsize=(10, 5))
        ax.set_title("State distribution by turn")
        ax.set_xlabel("Turn number")
        ax.set_ylabel("Count")
        fig = ax.get_figure()
        plot_path = analysis_dir / "state_distribution_by_turn.png"
        fig.tight_layout()
        fig.savefig(plot_path, dpi=150)
        plt.close(fig)
        generated.append(str(plot_path))

        run_summary = (
            turn_df.sort_values(["run_id", "turn_no"])
            .groupby("run_id")
            .agg(
                task_id=("task_id", "first"),
                model_id=("model_id", "first"),
                protocol_id=("protocol_id", "first"),
                logged_turns=("turn_no", "count"),
                first_pass_turn=("turn_no", lambda s: s[turn_df.loc[s.index, "exec_state"].eq("Pass")].min() if (turn_df.loc[s.index, "exec_state"] == "Pass").any() else pd.NA),
                final_turn=("turn_no", "max"),
                final_state=("exec_state", "last"),
                regressions=("regressed", lambda s: int(pd.Series(s).fillna(0).sum()) if "regressed" in turn_df.columns else 0),
            )
            .reset_index()
        )
        if not stability_df.empty:
            stable = (
                stability_df.groupby("run_id")
                .size()
                .reset_index(name="stability_checks")
            )
            run_summary = run_summary.merge(stable, on="run_id", how="left")
        run_summary_csv = analysis_dir / "run_summary_from_logs.csv"
        run_summary.to_csv(run_summary_csv, index=False)
        generated.append(str(run_summary_csv))

    if not run_df.empty:
        run_csv = analysis_dir / "run_plan.csv"
        run_df.to_csv(run_csv, index=False)
        generated.append(str(run_csv))

    if not stability_df.empty:
        stability_csv = analysis_dir / "stability_checks.csv"
        stability_df.to_csv(stability_csv, index=False)
        generated.append(str(stability_csv))

    return generated
