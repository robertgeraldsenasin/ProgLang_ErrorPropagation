from pathlib import Path

from errorprop_sql.task_loader import get_task_by_id, resolve_sqlite_db_path
from errorprop_sql.schema_utils import dump_sqlite_schema
from errorprop_sql.executor import execute_sqlite
from errorprop_sql.oracle import load_oracle_result, compare_with_oracle
from errorprop_sql.states import classify_state

SAMPLE_ROOT = Path("samples/mini_spider2")

def test_sample_layout_and_gold_query():
    task = get_task_by_id(SAMPLE_ROOT, "local001")
    db_path = resolve_sqlite_db_path(SAMPLE_ROOT, task.db)
    schema = dump_sqlite_schema(db_path)
    assert "CREATE TABLE customers" in schema
    oracle = load_oracle_result(SAMPLE_ROOT, "local001", db_path)
    sql = (SAMPLE_ROOT / "spider2-lite" / "evaluation_suite" / "gold" / "sql" / "local001.sql").read_text()
    exec_result = execute_sqlite(db_path, sql)
    cmp = compare_with_oracle(sql, exec_result, oracle)
    state = classify_state(format_error=False, execution_result=exec_result, comparison=cmp)
    assert state == "Pass"

def test_wrong_query_is_wrong_result():
    task = get_task_by_id(SAMPLE_ROOT, "local001")
    db_path = resolve_sqlite_db_path(SAMPLE_ROOT, task.db)
    oracle = load_oracle_result(SAMPLE_ROOT, "local001", db_path)
    sql = "SELECT first_name || ' ' || last_name AS full_name FROM customers ORDER BY customer_id LIMIT 1;"
    exec_result = execute_sqlite(db_path, sql)
    cmp = compare_with_oracle(sql, exec_result, oracle)
    state = classify_state(format_error=False, execution_result=exec_result, comparison=cmp)
    assert state == "WrongResult"
