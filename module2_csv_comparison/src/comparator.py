def compare_rows(source_df, target_df, column_matches, key_match):
    results = {
        "missing_in_target": [],
        "new_in_target": [],
        "value_mismatches": []
    }

    source_key = key_match["source_column"]
    target_key = key_match["target_column"]

    source_indexed = source_df.set_index(source_key)
    target_indexed = target_df.set_index(target_key)

    source_keys = set(source_indexed.index)
    target_keys = set(target_indexed.index)

    results["missing_in_target"] = list(source_keys - target_keys)
    results["new_in_target"] = list(target_keys - source_keys)

    common_keys = source_keys.intersection(target_keys)

    for key in common_keys:
        for match in column_matches:
            src_col = match["source_column"]
            tgt_col = match["target_column"]

            if src_col == source_key:
                continue

            source_value = source_indexed.loc[key, src_col]
            target_value = target_indexed.loc[key, tgt_col]

            if source_value != target_value:
                results["value_mismatches"].append({
                    "key": key,
                    "source_column": src_col,
                    "target_column": tgt_col,
                    "source_value": source_value.item() if hasattr(source_value, "item") else source_value,
                    "target_value": target_value.item() if hasattr(target_value, "item") else target_value
                })

    return results