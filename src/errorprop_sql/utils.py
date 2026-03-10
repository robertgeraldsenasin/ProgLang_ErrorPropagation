from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Any

def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def normalize_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return format(value, ".10g")
    return str(value)

def normalize_rows(rows: Iterable[Iterable[Any]]) -> list[tuple[str, ...]]:
    return [tuple(normalize_value(v) for v in row) for row in rows]

def safe_model_slug(model_label: str) -> str:
    return (
        model_label.strip()
        .lower()
        .replace("/", "-")
        .replace(" ", "-")
        .replace(".", "-")
    )
