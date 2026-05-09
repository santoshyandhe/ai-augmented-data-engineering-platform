import json
from pathlib import Path
from typing import Any

from agents import Agent, Runner
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
PROMPTS_DIR = BASE_DIR / "prompts"

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
                f"LLM returned invalid JSON: {raw_output}"
            )

        json_text = cleaned_output[start_index:end_index + 1]
        return json.loads(json_text)


async def interpret_legacy_metadata(
    static_analysis_result: dict[str, Any],
) -> dict[str, Any]:
    interpreter_agent = Agent(
        name="Legacy Pipeline Interpreter Agent",
        instructions=read_prompt("legacy_interpreter.md"),
    )

    agent_input = json.dumps(
        static_analysis_result,
        indent=4,
    )

    result = await Runner.run(
        interpreter_agent,
        agent_input,
    )

    return parse_json_output(result.final_output)