def detect_key_column(column_matches):
    key_keywords = ["id", "key", "number", "num", "code"]

    for match in column_matches:
        source_col = match["source_column"].lower()
        target_col = match["target_column"].lower()

        for keyword in key_keywords:
            if keyword in source_col or keyword in target_col:
                return match

    return column_matches[0] if column_matches else None