from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .task_loader import Task


def _normalize_external_knowledge(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            items.extend(_normalize_external_knowledge(item))
        return items
    text = str(value).strip()
    if not text:
        return []
    for sep in ["\n", ";"]:
        text = text.replace(sep, ",")
    items = [item.strip() for item in text.split(",")]
    return [item for item in items if item]


def _candidate_roots(spider2_root: Path) -> list[Path]:
    lite = spider2_root / "spider2-lite"
    return [
        lite / "resource" / "documents",
        lite / "resource" / "documentation" / "external_knowledge",
        lite / "resource" / "documentation",
        lite / "resource",
    ]


def _resolve_support_file(spider2_root: Path, name: str) -> Path | None:
    candidate = Path(name)
    if candidate.is_absolute() and candidate.exists():
        return candidate
    if candidate.parts:
        direct = spider2_root / candidate
        if direct.exists():
            return direct
    for root in _candidate_roots(spider2_root):
        exact = root / name
        if exact.exists():
            return exact
        if root.exists():
            matches = sorted(root.rglob(name))
            if matches:
                return matches[0]
    return None


def render_supporting_context(
    spider2_root: Path,
    task: Task,
    *,
    max_chars_per_doc: int = 1800,
    max_total_chars: int = 5000,
) -> str:
    doc_names = _normalize_external_knowledge(task.external_knowledge)
    if not doc_names:
        return "No external knowledge files were referenced for this task."

    rendered_parts: list[str] = []
    total_chars = 0

    for doc_name in doc_names:
        path = _resolve_support_file(spider2_root, doc_name)
        if path is None:
            rendered = f"[Missing support file: {doc_name}]"
        else:
            text = path.read_text(encoding="utf-8", errors="ignore").strip()
            if len(text) > max_chars_per_doc:
                text = text[:max_chars_per_doc].rstrip() + "\n...[truncated for prompt length]"
            rendered = f"[File: {path.name}]\n{text}"

        remaining = max_total_chars - total_chars
        if remaining <= 0:
            break
        if len(rendered) > remaining:
            rendered = rendered[:remaining].rstrip() + "\n...[truncated for prompt length]"
        rendered_parts.append(rendered)
        total_chars += len(rendered)

    return "\n\n".join(rendered_parts) if rendered_parts else "No supporting context was loaded."
