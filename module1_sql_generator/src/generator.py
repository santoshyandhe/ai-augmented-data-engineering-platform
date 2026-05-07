from pathlib import Path

from module1_sql_generator.src.catalog_loader import load_catalogs
from module1_sql_generator.src.llm_client import LLMClient
from module1_sql_generator.src.models import SQLGenerationResult
from module1_sql_generator.src.prompt_builder import build_prompt
from module1_sql_generator.src.retriever import retrieve_context


class SQLGenerator:
    """
    End-to-end SQL generation pipeline.

    This class orchestrates:
    1. Catalog loading
    2. Relevant schema/UDF retrieval
    3. Prompt construction
    4. LLM SQL generation
    """

    def __init__(
        self,
        schema_path: str | Path,
        udf_path: str | Path,
        prompt_template_path: str | Path,
    ) -> None:
        self.schema_path = Path(schema_path)
        self.udf_path = Path(udf_path)
        self.prompt_template_path = Path(prompt_template_path)

        self.schema_catalog, self.udf_catalog = load_catalogs(
            self.schema_path,
            self.udf_path,
        )

        self.llm_client = LLMClient()

    def generate(self, user_prompt: str) -> SQLGenerationResult:
        """
        Generate SQL for a natural language user request.
        """
        context = retrieve_context(
            user_prompt=user_prompt,
            schema_catalog=self.schema_catalog,
            udf_catalog=self.udf_catalog,
        )

        final_prompt = build_prompt(
            user_prompt=user_prompt,
            context=context,
            template_path=self.prompt_template_path,
        )

        return self.llm_client.generate_sql(final_prompt)