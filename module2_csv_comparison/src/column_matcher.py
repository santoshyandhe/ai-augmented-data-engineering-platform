from rapidfuzz import fuzz


def match_columns(source_columns, target_columns, threshold=60):
    matches = []

    for source_col in source_columns:
        best_target_col = None
        best_score = 0

        for target_col in target_columns:
            score = fuzz.ratio(source_col.lower(), target_col.lower())

            if score > best_score:
                best_score = score
                best_target_col = target_col

        if best_score >= threshold:
            matches.append({
                "source_column": source_col,
                "target_column": best_target_col,
                "confidence_score": round(best_score / 100, 2)
            })

    return matches