from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class Task:
    instance_id: str
    db: str
    question: str
    external_knowledge: str | list[str] | None
    raw: dict[str, Any]

def _candidate_task_files(spider2_root: Path) -> list[Path]:
    return [
        spider2_root / "spider2-lite" / "spider2-lite.jsonl",
        spider2_root / "spider2-lite" / "spider2-lite.json",
        spider2_root / "spider2-lite.jsonl",
        spider2_root / "spider2-lite.json",
    ]

def _load_any_json_records(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        rows = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported task file structure: {path}")

def load_tasks_from_root(spider2_root: Path) -> list[Task]:
    task_file = None
    for candidate in _candidate_task_files(spider2_root):
        if candidate.exists():
            task_file = candidate
            break
    if task_file is None:
        raise FileNotFoundError("Could not find spider2-lite task file under the supplied Spider2 root.")

    records = _load_any_json_records(task_file)
    tasks: list[Task] = []
    for row in records:
        tasks.append(
            Task(
                instance_id=str(row.get("instance_id") or row.get("id")),
                db=str(row.get("db") or row.get("database_id") or row.get("database")),
                question=str(row.get("question") or row.get("instruction") or row.get("query")),
                external_knowledge=row.get("external_knowledge"),
                raw=row,
            )
        )
    return tasks

def get_task_by_id(spider2_root: Path, instance_id: str) -> Task:
    for task in load_tasks_from_root(spider2_root):
        if task.instance_id == instance_id:
            return task
    raise KeyError(f"Task not found: {instance_id}")

def resolve_sqlite_db_path(spider2_root: Path, db_name: str, explicit_path: str | None = None) -> Path:
    candidates: list[Path] = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    candidates.extend(
        [
            spider2_root / "spider2-lite" / "resource" / "databases" / "spider2-localdb" / f"{db_name}.sqlite",
            spider2_root / "spider2-lite" / "resource" / "databases" / "sqlite" / f"{db_name}.sqlite",
            spider2_root / "resource" / "databases" / "spider2-localdb" / f"{db_name}.sqlite",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate

    search_roots = [
        spider2_root / "spider2-lite" / "resource" / "databases",
        spider2_root / "resource" / "databases",
        spider2_root,
    ]
    for root in search_roots:
        if root.exists():
            found = list(root.rglob(f"{db_name}.sqlite"))
            if found:
                return found[0]
    raise FileNotFoundError(f"Could not resolve SQLite database file for db={db_name}")

def validate_spider2_layout(spider2_root: Path) -> dict[str, Any]:
    lite_dir = spider2_root / "spider2-lite"
    task_file = next((p for p in _candidate_task_files(spider2_root) if p.exists()), None)
    sqlite_dir = lite_dir / "resource" / "databases" / "spider2-localdb"
    gold_sql_dir = lite_dir / "evaluation_suite" / "gold" / "sql"
    gold_exec_dir = lite_dir / "evaluation_suite" / "gold" / "exec_result"

    report = {
        "spider2_root_exists": spider2_root.exists(),
        "spider2_lite_dir_exists": lite_dir.exists(),
        "task_file": str(task_file) if task_file else None,
        "sqlite_dir_exists": sqlite_dir.exists(),
        "sqlite_file_count": len(list(sqlite_dir.glob("*.sqlite"))) if sqlite_dir.exists() else 0,
        "gold_sql_dir_exists": gold_sql_dir.exists(),
        "gold_exec_dir_exists": gold_exec_dir.exists(),
    }
    return report
