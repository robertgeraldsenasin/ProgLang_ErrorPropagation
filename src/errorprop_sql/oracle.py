from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .executor import execute_sqlite, ExecutionResult
from .sql_extract import has_explicit_order_by
from .utils import normalize_rows

@dataclass
class OracleResult:
    source_type: str
    source_path: Path | None
    sql: str | None
    columns: list[str]
    rows: list[tuple[Any, ...]]

@dataclass
class ComparisonResult:
    same: bool
    order_sensitive: bool
    rows_pred: int
    rows_gold: int
    symdiff_rows: int
    gold_sample: list[tuple[str, ...]]
    pred_sample: list[tuple[str, ...]]

def _load_exec_result_file(path: Path) -> tuple[list[str], list[tuple[Any, ...]]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix == ".tsv":
        df = pd.read_csv(path, sep="\t")
    elif suffix == ".json":
        df = pd.read_json(path)
    elif suffix == ".jsonl":
        df = pd.read_json(path, lines=True)
    else:
        raise ValueError(f"Unsupported exec result format: {path}")
    return list(df.columns), [tuple(row) for row in df.itertuples(index=False, name=None)]

def load_oracle_result(spider2_root: Path, instance_id: str, db_path: Path, timeout_sec: float = 15.0) -> OracleResult:
    gold_exec_dir = spider2_root / "spider2-lite" / "evaluation_suite" / "gold" / "exec_result"
    gold_sql_dir = spider2_root / "spider2-lite" / "evaluation_suite" / "gold" / "sql"

    if gold_exec_dir.exists():
        matches = sorted(gold_exec_dir.glob(f"{instance_id}.*"))
        if matches:
            columns, rows = _load_exec_result_file(matches[0])
            return OracleResult(
                source_type="exec_result",
                source_path=matches[0],
                sql=None,
                columns=columns,
                rows=rows,
            )

    sql_path = gold_sql_dir / f"{instance_id}.sql"
    if sql_path.exists():
        sql = sql_path.read_text(encoding="utf-8").strip()
        exec_result = execute_sqlite(db_path, sql, timeout_sec=timeout_sec)
        if not exec_result.ok:
            raise RuntimeError(f"Gold SQL for {instance_id} failed to execute: {exec_result.error_message}")
        return OracleResult(
            source_type="gold_sql",
            source_path=sql_path,
            sql=sql,
            columns=exec_result.columns,
            rows=exec_result.rows,
        )

    raise FileNotFoundError(f"No oracle exec result or gold SQL found for {instance_id}")

def compare_with_oracle(pred_sql: str, exec_result: ExecutionResult, oracle: OracleResult) -> ComparisonResult:
    order_sensitive = has_explicit_order_by(pred_sql) or has_explicit_order_by(oracle.sql or "")

    pred_norm = normalize_rows(exec_result.rows)
    gold_norm = normalize_rows(oracle.rows)

    pred_cmp = pred_norm if order_sensitive else sorted(pred_norm)
    gold_cmp = gold_norm if order_sensitive else sorted(gold_norm)

    same = pred_cmp == gold_cmp
    pred_counter = Counter(pred_cmp)
    gold_counter = Counter(gold_cmp)
    symdiff_rows = sum(abs(pred_counter[k] - gold_counter[k]) for k in set(pred_counter) | set(gold_counter))

    return ComparisonResult(
        same=same,
        order_sensitive=order_sensitive,
        rows_pred=len(pred_norm),
        rows_gold=len(gold_norm),
        symdiff_rows=symdiff_rows,
        gold_sample=gold_cmp[:3],
        pred_sample=pred_cmp[:3],
    )
