import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI

from module1_sql_generator.src.models import SQLGenerationResult


load_dotenv()


class LLMClient:
    """
    Thin wrapper around OpenAI API.

    Purpose:
    - Send the final prompt to the LLM
    - Receive JSON response
    - Convert it into SQLGenerationResult
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing. Add it to your .env file."
            )

        self.client = OpenAI(api_key=self.api_key)

    def generate_sql(self, prompt: str) -> SQLGenerationResult:
        """
        Generate SQL from the final prepared prompt.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior SQL generation assistant. "
                        "Return only valid JSON. Do not include markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
        )

        content = response.choices[0].message.content

        if content is None:
            raise ValueError("LLM returned empty response.")

        parsed_response = self._parse_json_response(content)

        return SQLGenerationResult(**parsed_response)

    @staticmethod
    def _parse_json_response(content: str) -> Dict[str, Any]:
        """
        Parse LLM JSON safely.

        Sometimes models wrap JSON with whitespace or accidental markdown.
        This function tries to recover the JSON object.
        """
        cleaned = content.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "")
            cleaned = cleaned.replace("```", "")
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"LLM response was not valid JSON. Raw response: {content}"
            ) from exc