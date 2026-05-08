import streamlit as st

from src.loader import load_csv
from src.column_matcher import match_columns
from src.key_detector import detect_key_column
from src.comparator import compare_rows
from src.report_writer import write_report


st.title("AI CSV Comparison Tool")

source_file = st.file_uploader(
    "Upload Source CSV",
    type=["csv"]
)

target_file = st.file_uploader(
    "Upload Target CSV",
    type=["csv"]
)

if source_file and target_file:

    source_df = load_csv(source_file)
    target_df = load_csv(target_file)

    column_matches = match_columns(
        source_df.columns,
        target_df.columns
    )

    key_match = detect_key_column(column_matches)

    comparison_results = compare_rows(
        source_df,
        target_df,
        column_matches,
        key_match
    )

    final_report = {
        "column_matches": column_matches,
        "detected_key": key_match,
        "comparison_results": comparison_results
    }

    report_path = write_report(final_report)

    st.subheader("Detected Column Matches")
    st.json(column_matches)

    st.subheader("Detected Key")
    st.json(key_match)

    st.subheader("Comparison Results")
    st.json(comparison_results)

    st.success(f"Report generated: {report_path}")
    import json

    report_json = json.dumps(final_report, indent=4)

    st.download_button(
        label="Download JSON Report",
        data=report_json,
        file_name="csv_comparison_report.json",
        mime="application/json"
)