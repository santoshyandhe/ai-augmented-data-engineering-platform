from pathlib import Path
from typing import Any

import yaml


def _split_table_name(table_name: str) -> tuple[str, str]:
    parts = table_name.split(".")

    if len(parts) == 2:
        return parts[0], parts[1]

    return "default", table_name


def generate_dbt_model(
    sql_analysis: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, str]:
    output_path = Path(output_dir)
    dbt_output_path = output_path / "dbt"
    dbt_output_path.mkdir(parents=True, exist_ok=True)

    target_table = sql_analysis["target_table"]["table_name"]
    target_columns = sql_analysis["target_table"]["columns"]
    source_tables = sql_analysis["source_tables"]

    _, model_name = _split_table_name(target_table)

    source_refs = []
    for source in source_tables:
        schema_name, table_name = _split_table_name(source["table_name"])
        source_refs.append(
            {
                "schema_name": schema_name,
                "table_name": table_name,
                "columns_used": source.get("columns_used", []),
            }
        )

    selected_columns = sql_analysis["transformations"]["selected_columns"]
    joins = sql_analysis["transformations"]["joins"]
    filters = sql_analysis["transformations"]["filters"]
    group_by = sql_analysis["transformations"]["group_by"]

    from_source = source_refs[0]

    dbt_sql_lines = [
        "{{ config(materialized='table') }}",
        "",
        "WITH transformed AS (",
        "    SELECT",
    ]

    for index, column in enumerate(selected_columns):
        comma = "," if index < len(selected_columns) - 1 else ""
        dbt_sql_lines.append(f"        {column}{comma}")

    dbt_sql_lines.append(
        f"    FROM {{{{ source('{from_source['schema_name']}', "
        f"'{from_source['table_name']}') }}}} "
        f"{source_tables[0].get('alias', '')}"
    )

    for join in joins:
        dbt_sql_lines.append(f"    {join}")

    for filter_condition in filters:
        dbt_sql_lines.append(f"    WHERE {filter_condition}")

    if group_by:
        dbt_sql_lines.append("    GROUP BY")
        for index, column in enumerate(group_by):
            comma = "," if index < len(group_by) - 1 else ""
            dbt_sql_lines.append(f"        {column}{comma}")

    dbt_sql_lines.extend(
        [
            ")",
            "",
            "SELECT",
        ]
    )

    for index, column in enumerate(target_columns):
        comma = "," if index < len(target_columns) - 1 else ""
        dbt_sql_lines.append(f"    {column}{comma}")

    dbt_sql_lines.append("FROM transformed")

    model_sql = "\n".join(dbt_sql_lines)

    model_path = dbt_output_path / f"{model_name}.sql"
    model_path.write_text(model_sql, encoding="utf-8")

    schema_yml = {
        "version": 2,
        "models": [
            {
                "name": model_name,
                "description": (
                    "Migrated dbt model generated from legacy SQL analysis."
                ),
                "columns": [
                    {
                        "name": column,
                        "tests": ["not_null"]
                        if column.endswith("_id") or column == "customer_id"
                        else [],
                    }
                    for column in target_columns
                ],
            }
        ],
        "sources": [
            {
                "name": source["schema_name"],
                "tables": [
                    {
                        "name": source["table_name"],
                        "columns": [
                            {"name": column}
                            for column in source["columns_used"]
                        ],
                    }
                ],
            }
            for source in source_refs
        ],
    }

    schema_path = dbt_output_path / "schema.yml"
    schema_path.write_text(
        yaml.dump(schema_yml, sort_keys=False),
        encoding="utf-8",
    )

    return {
        "dbt_model_path": str(model_path),
        "dbt_schema_path": str(schema_path),
    }