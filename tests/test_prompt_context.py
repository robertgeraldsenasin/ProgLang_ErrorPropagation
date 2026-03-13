from pathlib import Path

from errorprop_sql.prompt_context import render_supporting_context


SAMPLE_ROOT = Path("samples/mini_spider2")


def test_render_supporting_context_loads_external_markdown() -> None:
    from errorprop_sql.task_loader import get_task_by_id

    task = get_task_by_id(SAMPLE_ROOT, "local001")
    rendered = render_supporting_context(SAMPLE_ROOT, task)
    assert "sqlite_demo_note.md" in rendered
    assert "customer full name" in rendered.lower()
