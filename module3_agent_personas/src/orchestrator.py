import asyncio
import json
from pathlib import Path
from typing import Any

import nbformat
from agents import Agent, Runner
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUTS_DIR = BASE_DIR / "outputs"

load_dotenv(BASE_DIR / ".env")


def read_prompt(file_name: str) -> str:
    prompt_path = PROMPTS_DIR / file_name
    return prompt_path.read_text(encoding="utf-8")


def parse_json_output(raw_output: str) -> dict[str, Any]:
    cleaned_output = raw_output.strip()

    try:
        return json.loads(cleaned_output)
    except json.JSONDecodeError:
        start_index = cleaned_output.find("{")
        end_index = cleaned_output.rfind("}")

        if start_index == -1 or end_index == -1:
            raise ValueError(
                f"Agent returned invalid JSON with no JSON object: {raw_output}"
            )

        json_text = cleaned_output[start_index:end_index + 1]

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Agent returned invalid JSON: {raw_output}"
            ) from exc


def extract_code_from_notebook_payload(notebook_payload: dict[str, Any]) -> str:
    code_cells = notebook_payload.get("code_cells", [])
    return "\n\n".join(code_cells)


def write_notebook(notebook_payload: dict[str, Any]) -> Path:
    notebook = nbformat.v4.new_notebook()
    cells = []

    markdown_cells = notebook_payload.get("markdown_cells", [])
    code_cells = notebook_payload.get("code_cells", [])

    for markdown in markdown_cells:
        cells.append(nbformat.v4.new_markdown_cell(markdown))

    for code in code_cells:
        cells.append(nbformat.v4.new_code_cell(code))

    notebook["cells"] = cells

    output_path = OUTPUTS_DIR / "generated_notebook.ipynb"

    with output_path.open("w", encoding="utf-8") as file:
        nbformat.write(notebook, file)

    return output_path


def write_test_file(test_payload: dict[str, Any]) -> Path:
    output_path = OUTPUTS_DIR / test_payload.get(
        "test_file_name",
        "test_generated_module.py",
    )

    output_path.write_text(
        test_payload["test_code"],
        encoding="utf-8",
    )

    return output_path


def write_review_report(review_payload: dict[str, Any]) -> Path:
    output_path = OUTPUTS_DIR / "review_report.json"

    output_path.write_text(
        json.dumps(review_payload, indent=4),
        encoding="utf-8",
    )

    return output_path


async def run_agent_workflow(feature_request: str) -> dict[str, Any]:
    OUTPUTS_DIR.mkdir(exist_ok=True)

    developer_agent = Agent(
        name="Developer Agent",
        instructions=read_prompt("developer_agent.md"),
    )

    tester_agent = Agent(
        name="Tester Agent",
        instructions=read_prompt("tester_agent.md"),
    )

    reviewer_agent = Agent(
        name="Reviewer Agent",
        instructions=read_prompt("reviewer_agent.md"),
    )

    max_attempts = 4
    attempts = []

    current_feature_request = feature_request

    for attempt_number in range(1, max_attempts + 1):
        print(f"\nRunning attempt {attempt_number}...")

        developer_result = await Runner.run(
            developer_agent,
            current_feature_request,
        )

        notebook_payload = parse_json_output(
            developer_result.final_output
        )

        implementation_code = extract_code_from_notebook_payload(
            notebook_payload
        )

        tester_result = await Runner.run(
            tester_agent,
            implementation_code,
        )

        test_payload = parse_json_output(
            tester_result.final_output
        )

        test_code = test_payload["test_code"]

        reviewer_input = f"""
Python implementation code:
{implementation_code}

Pytest test code:
{test_code}
"""

        reviewer_result = await Runner.run(
            reviewer_agent,
            reviewer_input,
        )

        review_payload = parse_json_output(
            reviewer_result.final_output
        )

        attempt_result = {
            "attempt_number": attempt_number,
            "developer_output": notebook_payload,
            "tester_output": test_payload,
            "reviewer_output": review_payload,
        }

        attempts.append(attempt_result)

        has_warn_or_fail = any(
            finding.get("severity") in ["WARN", "FAIL"]
            for finding in review_payload.get("findings", [])
        )

        verdict = review_payload.get("verdict")

        if verdict == "APPROVED" and not has_warn_or_fail:
            print("Reviewer approved the implementation.")
            break

        print("Reviewer requested changes. Preparing next attempt...")

        current_feature_request = f"""
Original feature request:
{feature_request}

The Reviewer Agent requested changes.

Reviewer findings:
{json.dumps(review_payload, indent=4)}

Please revise the implementation and fix all WARN and FAIL findings.
Return the same JSON structure as before.
"""

    final_attempt = attempts[-1]

    notebook_path = write_notebook(
        final_attempt["developer_output"]
    )

    test_file_path = write_test_file(
        final_attempt["tester_output"]
    )

    review_report_path = write_review_report(
        final_attempt["reviewer_output"]
    )

    workflow_result = {
        "feature_request": feature_request,
        "final_verdict": final_attempt["reviewer_output"].get("verdict"),
        "generated_files": {
            "notebook": str(notebook_path),
            "test_file": str(test_file_path),
            "review_report": str(review_report_path),
        },
        "attempts": attempts,
    }

    output_path = OUTPUTS_DIR / "agent_workflow_result.json"

    output_path.write_text(
        json.dumps(workflow_result, indent=4),
        encoding="utf-8",
    )

    return workflow_result


if __name__ == "__main__":
    feature_request = input(
        "Enter your feature request: "
    )

    result = asyncio.run(
        run_agent_workflow(feature_request)
    )

    print("\nFinal Verdict:")
    print(result["final_verdict"])

    print("\nGenerated Files:")
    for file_type, file_path in result["generated_files"].items():
        print(f"{file_type}: {file_path}")

    print("\nFinal Reviewer Output:")
    print(
        json.dumps(
            result["attempts"][-1]["reviewer_output"],
            indent=4,
        )
    )