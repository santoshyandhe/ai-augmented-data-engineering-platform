from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from module1_sql_generator.src.database_adapter import DuckDBAdapter
from module1_sql_generator.src.generator import SQLGenerator
from module1_sql_generator.src.validator import validate_sql

app = typer.Typer()
console = Console()


DEFAULT_SCHEMA_PATH = Path("module1_sql_generator/catalog/schema.yaml")
DEFAULT_UDF_PATH = Path("module1_sql_generator/catalog/udfs.yaml")
DEFAULT_PROMPT_TEMPLATE_PATH = Path("module1_sql_generator/prompts/sql_generator.md")


def print_validation_report(title: str, is_valid: bool, issues: list) -> None:
    """
    Print validation report in a readable table.
    """
    table = Table(title=title)
    table.add_column("Severity")
    table.add_column("Message")

    if not issues:
        table.add_row("INFO", "No issues found.")
    else:
        for issue in issues:
            table.add_row(issue.severity, issue.message)

    console.print(table)

    status = "PASSED" if is_valid else "FAILED"
    console.print(f"[bold]Validation Status:[/bold] {status}")


@app.command()
def generate(user_prompt: str) -> None:
    """
    Generate SQL from a natural language prompt.
    """
    generator = SQLGenerator(
        schema_path=DEFAULT_SCHEMA_PATH,
        udf_path=DEFAULT_UDF_PATH,
        prompt_template_path=DEFAULT_PROMPT_TEMPLATE_PATH,
    )

    result = generator.generate(user_prompt)

    console.print(Panel(result.sql, title="Generated SQL", expand=False))

    reasoning_text = "\n".join(
        f"{idx + 1}. {step}"
        for idx, step in enumerate(result.reasoning_steps)
    ) or "No reasoning steps returned."

    console.print(Panel(reasoning_text, title="Reasoning Trace", expand=False))

    console.print(f"[bold]Tables Used:[/bold] {', '.join(result.tables_used) or 'N/A'}")
    console.print(f"[bold]UDFs Used:[/bold] {', '.join(result.udfs_used) or 'N/A'}")

    validation_report = validate_sql(
        sql=result.sql,
        schema_catalog=generator.schema_catalog,
        udf_catalog=generator.udf_catalog,
        dialect=generator.schema_catalog.database.dialect,
    )

    print_validation_report(
        title="Static SQL Validation",
        is_valid=validation_report.is_valid,
        issues=validation_report.issues,
    )

    db_adapter = DuckDBAdapter(generator.schema_catalog)
    db_adapter.setup_demo_schema()

    explain_ok, explain_message = db_adapter.explain_query(result.sql)

    console.print(
        Panel(
            explain_message[:2000],
            title="Database EXPLAIN / Dry Run",
            expand=False,
        )
    )

    explain_status = "PASSED" if explain_ok else "FAILED"
    console.print(f"[bold]EXPLAIN Status:[/bold] {explain_status}")


if __name__ == "__main__":
    app()