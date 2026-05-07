from pathlib import Path

from jinja2 import Template

from module1_sql_generator.src.models import RetrievedContext, Table, UDF


def format_table(table: Table) -> str:
    """
    Convert a table object into readable prompt context.
    """
    column_lines = []
    for column in table.columns:
        column_lines.append(
            f"- {column.name} ({column.type}): {column.description or ''}"
        )

    return f"""
Table: {table.name}
Description: {table.description or ''}
Primary Key: {table.primary_key or 'N/A'}
Columns:
{chr(10).join(column_lines)}
""".strip()


def format_udf(udf: UDF) -> str:
    """
    Convert a UDF object into readable prompt context.
    """
    return f"""
UDF: {udf.name}
Signature: {udf.signature}
Return Type: {udf.return_type}
Description: {udf.description}
Example Usage:
{udf.example_usage}
Tags: {", ".join(udf.tags)}
Business Domain: {udf.business_domain or 'N/A'}
""".strip()


def load_prompt_template(template_path: str | Path) -> Template:
    """
    Load the prompt template from a markdown file.
    """
    path = Path(template_path)

    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")

    template_text = path.read_text(encoding="utf-8")
    return Template(template_text)


def build_prompt(
    user_prompt: str,
    context: RetrievedContext,
    template_path: str | Path,
) -> str:
    """
    Build the final LLM prompt using user request,
    relevant schema context, and relevant UDF context.
    """
    template = load_prompt_template(template_path)

    formatted_tables = "\n\n".join(
        format_table(table) for table in context.relevant_tables
    )

    formatted_udfs = "\n\n".join(
        format_udf(udf) for udf in context.relevant_udfs
    )

    return template.render(
        user_prompt=user_prompt,
        schema_context=formatted_tables or "No relevant tables found.",
        udf_context=formatted_udfs or "No relevant UDFs found.",
    )