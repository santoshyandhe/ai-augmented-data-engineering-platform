
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st

from module1_sql_generator.src.database_adapter import DuckDBAdapter
from module1_sql_generator.src.generator import SQLGenerator
from module1_sql_generator.src.validator import validate_sql


SCHEMA_PATH = "module1_sql_generator/catalog/schema.yaml"
UDF_PATH = "module1_sql_generator/catalog/udfs.yaml"
PROMPT_PATH = "module1_sql_generator/prompts/sql_generator.md"


@st.cache_resource
def load_generator():
    return SQLGenerator(
        schema_path=SCHEMA_PATH,
        udf_path=UDF_PATH,
        prompt_template_path=PROMPT_PATH,
    )


generator = load_generator()

st.set_page_config(
    page_title="AI SQL Generator",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Intelligent SQL Generator")

st.markdown(
    """
Generate validated PostgreSQL SQL using:

- schema-aware retrieval
- UDF-aware generation
- static validation
- database EXPLAIN validation
"""
)

user_prompt = st.text_area(
    "Enter your business question",
    placeholder="show top 10 customers by lifetime value",
    height=120,
)

generate_button = st.button("Generate SQL")


if generate_button and not user_prompt.strip():

    st.warning(
        "Please enter a business question before generating SQL."
    )

elif generate_button and user_prompt.strip():

    with st.spinner("Generating SQL..."):

        result = generator.generate(user_prompt)

        # -----------------------------------------------------
        # Generated SQL
        # -----------------------------------------------------

        st.subheader("Generated SQL")

        st.code(result.sql, language="sql")

        # -----------------------------------------------------
        # Reasoning + Metadata
        # -----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Reasoning Trace")

            if result.reasoning_steps:
                for step in result.reasoning_steps:
                    st.write(f"- {step}")
            else:
                st.write("No reasoning steps returned.")

        with col2:

            st.subheader("Metadata")

            st.write("Tables Used:")
            st.write(result.tables_used or "N/A")

            st.write("UDFs Used:")
            st.write(result.udfs_used or "N/A")

        # -----------------------------------------------------
        # Static Validation
        # -----------------------------------------------------

        validation_report = validate_sql(
            sql=result.sql,
            schema_catalog=generator.schema_catalog,
            udf_catalog=generator.udf_catalog,
            dialect=generator.schema_catalog.database.dialect,
        )

        st.subheader("Static Validation")

        if validation_report.is_valid:
            st.success("Validation PASSED")
        else:
            st.error("Validation FAILED")

        if validation_report.issues:

            for issue in validation_report.issues:

                if issue.severity == "ERROR":
                    st.error(issue.message)

                elif issue.severity == "WARNING":
                    st.warning(issue.message)

                else:
                    st.info(issue.message)

        else:
            st.write("No issues found.")

        # -----------------------------------------------------
        # Database EXPLAIN / Dry Run
        # -----------------------------------------------------

        db_adapter = DuckDBAdapter(generator.schema_catalog)

        db_adapter.setup_demo_schema()

        explain_ok, explain_output = db_adapter.explain_query(
            result.sql
        )

        st.subheader("Database EXPLAIN / Dry Run")

        if explain_ok:

            st.success("EXPLAIN PASSED")

            st.info(
                "DuckDB successfully generated an execution "
                "plan for this SQL. This confirms the query "
                "can be parsed, planned, and dry-run validated."
            )

        else:

            st.error("EXPLAIN FAILED")

        with st.expander("View Full EXPLAIN Plan"):

            st.code(
                explain_output[:5000],
                language="text",
            )