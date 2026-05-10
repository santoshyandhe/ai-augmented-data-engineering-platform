import asyncio
import json
from pathlib import Path

import streamlit as st

from src.orchestrator import run_agent_workflow


st.set_page_config(
    page_title="AI Agent Personas Workflow",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Multi-Agent AI Development Workflow")

st.markdown("""
This module demonstrates an enterprise-style AI workflow using multiple agents:

- 👨‍💻 Developer Agent
- 🧪 Tester Agent
- 🔍 Reviewer Agent

The agents collaborate to:
1. Generate Python implementation
2. Generate Pytest test cases
3. Review code quality
4. Retry automatically if issues are found
""")

st.divider()

feature_request = st.text_area(
    "Enter Feature Request",
    height=150,
    placeholder="Example: Create a factorial function with input validation",
)

run_button = st.button("🚀 Run Agent Workflow")

if run_button:
    if not feature_request.strip():
        st.error("Please enter a feature request.")
        st.stop()

    with st.spinner("Running multi-agent workflow..."):

        result = asyncio.run(
            run_agent_workflow(feature_request)
        )

    st.success("Workflow completed!")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Final Verdict",
            result["final_verdict"]
        )

    with col2:
        st.metric(
            "Total Attempts",
            len(result["attempts"])
        )

    st.divider()

    st.subheader("📂 Generated Files")

    generated_files = result["generated_files"]

    for file_type, file_path in generated_files.items():
        st.code(f"{file_type}: {file_path}")

    st.divider()

    final_review = result["attempts"][-1]["reviewer_output"]

    st.subheader("🔍 Final Reviewer Output")

    st.json(final_review)

    st.divider()

    st.subheader("📜 Attempt History")

    for attempt in result["attempts"]:

        with st.expander(
            f"Attempt {attempt['attempt_number']}"
        ):

            st.markdown("### Developer Output")

            developer_output = attempt["developer_output"]

            markdown_cells = developer_output.get(
                "markdown_cells",
                []
            )

            code_cells = developer_output.get(
                "code_cells",
                []
            )

            for markdown in markdown_cells:
                st.markdown(markdown)

            for code in code_cells:
                st.code(code, language="python")

            st.markdown("### Tester Output")

            tester_output = attempt["tester_output"]

            st.code(
                tester_output["test_code"],
                language="python",
            )

            st.markdown("### Reviewer Output")

            st.json(attempt["reviewer_output"])

    st.divider()

    st.subheader("📄 Raw Workflow Result")

    st.code(
        json.dumps(result, indent=4),
        language="json",
    )