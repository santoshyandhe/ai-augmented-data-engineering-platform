import asyncio
import json
from pathlib import Path

import streamlit as st

from src.artifact_scanner import scan_legacy_artifacts
from src.dbt_generator import generate_dbt_model
from src.gap_reporter import generate_gap_report
from src.llm_interpreter import interpret_legacy_metadata
from src.mermaid_writer import generate_mermaid_diagram
from src.migration_planner import generate_migration_plan


BASE_DIR = Path(__file__).resolve().parent
LEGACY_DIR = BASE_DIR / "legacy_artifacts"
OUTPUTS_DIR = BASE_DIR / "outputs"

LEGACY_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)


async def run_analysis():
    analysis_results = scan_legacy_artifacts(
        LEGACY_DIR,
        OUTPUTS_DIR,
    )

    static_analysis_result = {
        "artifacts_analyzed": analysis_results
    }

    interpretation_result = await interpret_legacy_metadata(
        static_analysis_result
    )

    mermaid_path = generate_mermaid_diagram(
        analysis_results,
        OUTPUTS_DIR,
    )

    gap_report_path = generate_gap_report(
        analysis_results,
        OUTPUTS_DIR,
    )

    sql_artifacts = [
        artifact
        for artifact in analysis_results
        if artifact["artifact_type"] == "sql"
    ]

    dbt_results = []

    for sql_artifact in sql_artifacts:
        dbt_result = generate_dbt_model(
            sql_artifact,
            OUTPUTS_DIR,
        )

        dbt_results.append(dbt_result)

    migration_plan_path = generate_migration_plan(
        analysis_results,
        interpretation_result,
        dbt_results,
        OUTPUTS_DIR,
    )

    final_result = {
        "static_analysis": static_analysis_result,
        "llm_interpretation": interpretation_result,
        "dbt_generation": dbt_results,
        "generated_artifacts": {
            "mermaid_diagram": str(mermaid_path),
            "gap_report": str(gap_report_path),
            "migration_plan": str(migration_plan_path),
        },
    }

    output_path = OUTPUTS_DIR / "legacy_analysis_result.json"

    output_path.write_text(
        json.dumps(final_result, indent=4),
        encoding="utf-8",
    )

    return final_result


st.set_page_config(
    page_title="Legacy Pipeline Modernization",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Legacy Pipeline Modernization System")

st.markdown(
    """
Upload legacy artifacts such as:
- SQL scripts
- Python ETL files
- YAML configs
- DAG definitions

The system performs:
- Static analysis
- LLM-assisted interpretation
- Gap analysis
- dbt migration generation
- Mermaid lineage generation
"""
)

uploaded_files = st.file_uploader(
    "Upload Legacy Artifacts",
    accept_multiple_files=True,
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        save_path = LEGACY_DIR / uploaded_file.name

        with open(save_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

    st.success(f"{len(uploaded_files)} files uploaded successfully.")

if st.button("Run Modernization Analysis"):
    with st.spinner("Running analysis..."):
        result = asyncio.run(run_analysis())

    st.success("Analysis completed.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Static Analysis",
            "LLM Interpretation",
            "Gap Report",
            "dbt Generation",
            "Migration Plan",
        ]
    )

    with tab1:
        st.json(result["static_analysis"])

    with tab2:
        st.json(result["llm_interpretation"])

    with tab3:
        gap_report_path = Path(
            result["generated_artifacts"]["gap_report"]
        )

        gap_report = json.loads(
            gap_report_path.read_text(encoding="utf-8")
        )

        st.json(gap_report)

    with tab4:
        st.json(result["dbt_generation"])

    with tab5:
        migration_plan_path = Path(
            result["generated_artifacts"]["migration_plan"]
        )

        migration_plan = migration_plan_path.read_text(
            encoding="utf-8"
        )

        st.markdown(migration_plan)