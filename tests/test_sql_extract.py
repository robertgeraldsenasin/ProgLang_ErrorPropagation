from errorprop_sql.sql_extract import extract_sql

def test_extract_sql_fenced():
    text = "hello\n```sql\nSELECT * FROM customers;\n```"
    sql, mode = extract_sql(text)
    assert sql == "SELECT * FROM customers;"
    assert mode == "sql_fenced_block"

def test_extract_sql_raw():
    sql, mode = extract_sql("SELECT 1;")
    assert sql == "SELECT 1;"
    assert mode == "raw_sql"

def test_extract_sql_none():
    sql, mode = extract_sql("I think the answer is customer A")
    assert sql is None
    assert mode == "no_sql_detected"
