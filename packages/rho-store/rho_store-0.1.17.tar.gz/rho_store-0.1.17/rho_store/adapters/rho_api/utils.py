import orjson


def table_data_to_list(table_data: dict) -> list[dict]:
    rows_raw = table_data["rows"]
    columns_raw = table_data["columns"]
    rows = orjson.loads(rows_raw)
    columns = orjson.loads(columns_raw)
    return to_list(columns, rows)


def to_list(columns: list, rows: list[list], skip_first_col: bool = True) -> list[dict]:
    # first column is internal "_id"-column
    first_index = 1 if skip_first_col else 0
    return [dict(zip(columns[first_index:], row[first_index:])) for row in rows]
