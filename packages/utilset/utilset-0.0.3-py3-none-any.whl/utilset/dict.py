def value_is_empty(row, key) -> bool:
    v = row.get(key, None)
    return v is None or str(v).strip() == ''