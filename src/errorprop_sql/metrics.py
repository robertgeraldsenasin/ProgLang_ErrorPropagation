from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .config import ERROR_SEVERITY


def _read_log(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_json(path, lines=True)


def _derive_turn_metrics(turn_df: pd.DataFrame) -> pd.DataFrame:
    if turn_df.empty:
        return turn_df

    turn_df = turn_df.copy().sort_values(["run_id", "turn_no"])
    turn_df["severity"] = turn_df["exec_state"].map(ERROR_SEVERITY)
    turn_df["helper_key"] = turn_df["run_id"].astype(str) + "|" + turn_df["turn_no"].astype(int).map(lambda v: f"{v:02d}")
    turn_df["prev_state"] = turn_df.groupby("run_id")["exec_state"].shift(1)
    turn_df["prev_severity"] = turn_df.groupby("run_id")["severity"].shift(1)
    turn_df["state_change"] = ((turn_df["prev_state"].notna()) & (turn_df["exec_state"] != turn_df["prev_state"])).astype(int)
    turn_df["improved"] = ((turn_df["prev_severity"].notna()) & (turn_df["severity"] < turn_df["prev_severity"])).astype(int)
    turn_df["regressed"] = ((turn_df["prev_severity"].notna()) & (turn_df["severity"] > turn_df["prev_severity"])).astype(int)
    turn_df["pass_flag"] = (turn_df["exec_state"] == "Pass").astype(int)
    return turn_df


def _build_run_summary(turn_df: pd.DataFrame, stability_df: pd.DataFrame) -> pd.DataFrame:
    if turn_df.empty:
        return pd.DataFrame()

    def _first_pass(series: pd.Series) -> float | pd.NA:
        states = turn_df.loc[series.index, "exec_state"]
        if (states == "Pass").any():
            return float(series[states == "Pass"].min())
        return pd.NA

    run_summary = (
        turn_df.groupby("run_id")
        .agg(
            task_id=("task_id", "first"),
            model_id=("model_id", "first"),
            protocol_id=("protocol_id", "first"),
            logged_turns=("turn_no", "count"),
            first_pass_turn=("turn_no", _first_pass),
            final_turn=("turn_no", "max"),
            final_state=("exec_state", "last"),
            improvements=("improved", "sum"),
            regressions=("regressed", "sum"),
            oscillations=("state_change", "sum"),
            max_severity=("severity", "max"),
        )
        .reset_index()
    )
    run_summary["pass_within_T"] = run_summary["first_pass_turn"].notna()
    if not stability_df.empty:
        stable_counts = (
            stability_df.groupby(["run_id", "check_type", "stable_pass?"])
            .size()
            .reset_index(name="count")
        )
        stable_pass = stable_counts[stable_counts["stable_pass?"] == "Yes"]
        reexec = stable_pass[stable_pass["check_type"] == "Re-execution"][["run_id", "count"]].rename(columns={"count": "stable_reexec_passes"})
        reprompt = stable_pass[stable_pass["check_type"] == "Re-prompt"][["run_id", "count"]].rename(columns={"count": "stable_reprompt_passes"})
        total = stability_df.groupby("run_id").size().reset_index(name="stability_checks")
        run_summary = run_summary.merge(reexec, on="run_id", how="left")
        run_summary = run_summary.merge(reprompt, on="run_id", how="left")
        run_summary = run_summary.merge(total, on="run_id", how="left")
    return run_summary


def _write_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, out_path: Path) -> None:
    if df.empty:
        return
    ax = df.plot(kind="bar", x=x_col, y=y_col, legend=False, figsize=(9, 4.5))
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(y_col.replace("_", " ").title())
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def generate_analysis_tables(out_dir: Path) -> list[str]:
    logs_dir = out_dir / "logs"
    analysis_dir = out_dir / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    turn_df = _derive_turn_metrics(_read_log(logs_dir / "turn_log.jsonl"))
    run_df = _read_log(logs_dir / "run_plan.jsonl")
    stability_df = _read_log(logs_dir / "stability_checks.jsonl")

    generated: list[str] = []

    if not turn_df.empty:
        turn_csv = analysis_dir / "turn_log.csv"
        turn_df.to_csv(turn_csv, index=False)
        generated.append(str(turn_csv))

        trans = (
            turn_df.dropna(subset=["prev_state"])
            .groupby(["prev_state", "exec_state"])
            .size()
            .reset_index(name="count")
        )
        trans_csv = analysis_dir / "transition_counts.csv"
        trans.to_csv(trans_csv, index=False)
        generated.append(str(trans_csv))

        trans_matrix = trans.pivot(index="prev_state", columns="exec_state", values="count").fillna(0)
        trans_matrix_csv = analysis_dir / "transition_matrix.csv"
        trans_matrix.to_csv(trans_matrix_csv)
        generated.append(str(trans_matrix_csv))

        by_turn = (
            turn_df.groupby(["turn_no", "exec_state"])
            .size()
            .reset_index(name="count")
            .sort_values(["turn_no", "exec_state"])
        )
        by_turn_csv = analysis_dir / "state_distribution_by_turn.csv"
        by_turn.to_csv(by_turn_csv, index=False)
        generated.append(str(by_turn_csv))

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

        run_summary = _build_run_summary(turn_df, stability_df)
        run_summary_csv = analysis_dir / "run_summary_from_logs.csv"
        run_summary.to_csv(run_summary_csv, index=False)
        generated.append(str(run_summary_csv))

        model_summary = (
            run_summary.groupby("model_id")
            .agg(
                runs=("run_id", "count"),
                pass_runs=("pass_within_T", "sum"),
                avg_logged_turns=("logged_turns", "mean"),
                avg_first_pass_turn=("first_pass_turn", "mean"),
                avg_regressions=("regressions", "mean"),
                avg_oscillations=("oscillations", "mean"),
            )
            .reset_index()
        )
        model_summary["pass_rate"] = model_summary["pass_runs"] / model_summary["runs"]
        model_summary_csv = analysis_dir / "model_summary.csv"
        model_summary.to_csv(model_summary_csv, index=False)
        generated.append(str(model_summary_csv))

        protocol_summary = (
            run_summary.groupby("protocol_id")
            .agg(
                runs=("run_id", "count"),
                pass_runs=("pass_within_T", "sum"),
                avg_logged_turns=("logged_turns", "mean"),
                avg_first_pass_turn=("first_pass_turn", "mean"),
                avg_regressions=("regressions", "mean"),
                avg_oscillations=("oscillations", "mean"),
            )
            .reset_index()
        )
        protocol_summary["pass_rate"] = protocol_summary["pass_runs"] / protocol_summary["runs"]
        protocol_summary_csv = analysis_dir / "protocol_summary.csv"
        protocol_summary.to_csv(protocol_summary_csv, index=False)
        generated.append(str(protocol_summary_csv))

        trajectory_summary_csv = analysis_dir / "trajectory_summary.csv"
        run_summary.to_csv(trajectory_summary_csv, index=False)
        generated.append(str(trajectory_summary_csv))

        pass_chart_path = analysis_dir / "pass_rate_by_model.png"
        _write_bar_chart(model_summary, "model_id", "pass_rate", "Pass rate by model", pass_chart_path)
        if pass_chart_path.exists():
            generated.append(str(pass_chart_path))

    if not run_df.empty:
        run_latest = run_df.drop_duplicates(subset=["run_id"], keep="last") if "run_id" in run_df.columns else run_df
        run_csv = analysis_dir / "run_plan.csv"
        run_latest.to_csv(run_csv, index=False)
        generated.append(str(run_csv))

        run_raw_csv = analysis_dir / "run_plan_raw.csv"
        run_df.to_csv(run_raw_csv, index=False)
        generated.append(str(run_raw_csv))

    if not stability_df.empty:
        stability_csv = analysis_dir / "stability_checks.csv"
        stability_df.to_csv(stability_csv, index=False)
        generated.append(str(stability_csv))

        stability_summary = (
            stability_df.groupby(["check_type", "outcome_state"])
            .size()
            .reset_index(name="count")
            .sort_values(["check_type", "outcome_state"])
        )
        stability_summary_csv = analysis_dir / "stability_summary.csv"
        stability_summary.to_csv(stability_summary_csv, index=False)
        generated.append(str(stability_summary_csv))

    return generated
