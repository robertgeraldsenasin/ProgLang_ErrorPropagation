from __future__ import annotations

import multiprocessing as mp
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class ExecutionResult:
    ok: bool
    timed_out: bool
    runtime_ms: int
    columns: list[str]
    rows: list[tuple[Any, ...]]
    error_message: str | None

def _worker(db_path: str, sql: str, queue: mp.Queue) -> None:
    start = time.perf_counter()
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        runtime_ms = int((time.perf_counter() - start) * 1000)
        queue.put(
            {
                "ok": True,
                "timed_out": False,
                "runtime_ms": runtime_ms,
                "columns": columns,
                "rows": rows,
                "error_message": None,
            }
        )
    except Exception as e:
        runtime_ms = int((time.perf_counter() - start) * 1000)
        queue.put(
            {
                "ok": False,
                "timed_out": False,
                "runtime_ms": runtime_ms,
                "columns": [],
                "rows": [],
                "error_message": str(e),
            }
        )
    finally:
        conn.close()

def execute_sqlite(db_path: Path, sql: str, timeout_sec: float = 5.0) -> ExecutionResult:
    queue: mp.Queue = mp.Queue()
    proc = mp.Process(target=_worker, args=(str(db_path), sql, queue))
    proc.start()
    proc.join(timeout_sec)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        return ExecutionResult(
            ok=False,
            timed_out=True,
            runtime_ms=int(timeout_sec * 1000),
            columns=[],
            rows=[],
            error_message=f"Execution exceeded timeout of {timeout_sec:.1f}s",
        )

    if queue.empty():
        return ExecutionResult(
            ok=False,
            timed_out=False,
            runtime_ms=0,
            columns=[],
            rows=[],
            error_message="Execution process exited without returning a result.",
        )

    payload = queue.get()
    return ExecutionResult(
        ok=payload["ok"],
        timed_out=payload["timed_out"],
        runtime_ms=payload["runtime_ms"],
        columns=payload["columns"],
        rows=[tuple(r) for r in payload["rows"]],
        error_message=payload["error_message"],
    )
