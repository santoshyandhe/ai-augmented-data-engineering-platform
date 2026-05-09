from pathlib import Path
from typing import Any

import sqlglot
from sqlglot import exp


def _read_sql(file_path: str | Path) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def _parse_sql(sql_text: str) -> exp.Expression:
    return sqlglot.parse_one(sql_text)


def _extract_target_table(parsed_sql: exp.Expression) -> str | None:
    insert_node = parsed_sql.find(exp.Insert)

    if not insert_node:
        return None

    table_node = insert_node.find(exp.Table)

    if not table_node:
        return None

    return table_node.sql()


def _extract_source_tables(parsed_sql: exp.Expression) -> list[dict[str, str | None]]:
    source_tables = []

    for table in parsed_sql.find_all(exp.Table):
        table_name = table.sql()
        alias = table.alias_or_name

        # Skip target table if it appears inside INSERT INTO
        parent = table.parent
        if isinstance(parent, exp.Schema):
            continue

        source_tables.append(
            {
                "table_name": table_name,
                "alias": alias,
            }
        )

    return source_tables


def _extract_select_columns(parsed_sql: exp.Expression) -> list[str]:
    select_node = parsed_sql.find(exp.Select)

    if not select_node:
        return []

    return [
        expression.sql()
        for expression in select_node.expressions
    ]


def _extract_target_columns(select_columns: list[str]) -> list[str]:
    target_columns = []

    for column in select_columns:
        parsed_column = sqlglot.parse_one(f"SELECT {column}")

        select_expr = parsed_column.find(exp.Select).expressions[0]

        if isinstance(select_expr, exp.Alias):
            target_columns.append(select_expr.alias)
        elif isinstance(select_expr, exp.Column):
            target_columns.append(select_expr.name)
        else:
            target_columns.append(select_expr.sql())

    return target_columns


def _extract_columns_by_table(
    parsed_sql: exp.Expression,
    source_tables: list[dict[str, str | None]],
) -> list[dict[str, Any]]:
    alias_to_table = {
        source["alias"]: source["table_name"]
        for source in source_tables
    }

    table_columns: dict[str, set[str]] = {
        source["table_name"]: set()
        for source in source_tables
    }

    for column in parsed_sql.find_all(exp.Column):
        column_name = column.name
        table_alias = column.table

        if table_alias in alias_to_table:
            table_name = alias_to_table[table_alias]
            table_columns[table_name].add(column_name)

    return [
        {
            "table_name": table_name,
            "columns_used": sorted(columns),
        }
        for table_name, columns in table_columns.items()
    ]


def _extract_joins(parsed_sql: exp.Expression) -> list[str]:
    joins = []

    for join in parsed_sql.find_all(exp.Join):
        joins.append(join.sql())

    return joins


def _extract_filters(parsed_sql: exp.Expression) -> list[str]:
    where_node = parsed_sql.find(exp.Where)

    if not where_node:
        return []

    return [where_node.this.sql()]


def _extract_group_by(parsed_sql: exp.Expression) -> list[str]:
    group_node = parsed_sql.find(exp.Group)

    if not group_node:
        return []

    return [
        expression.sql()
        for expression in group_node.expressions
    ]


def _extract_order_by(parsed_sql: exp.Expression) -> list[str]:
    order_node = parsed_sql.find(exp.Order)

    if not order_node:
        return []

    return [
        expression.sql()
        for expression in order_node.expressions
    ]


def _extract_limit(parsed_sql: exp.Expression) -> str | None:
    limit_node = parsed_sql.find(exp.Limit)

    if not limit_node:
        return None

    return limit_node.expression.sql()


def _extract_aggregations(parsed_sql: exp.Expression) -> list[str]:
    aggregations = []

    aggregate_types = (
        exp.Sum,
        exp.Count,
        exp.Avg,
        exp.Min,
        exp.Max,
    )

    for aggregate_type in aggregate_types:
        for node in parsed_sql.find_all(aggregate_type):
            aggregations.append(node.sql())

    return aggregations


def analyze_sql_file(file_path: str | Path) -> dict[str, Any]:
    sql_text = _read_sql(file_path)
    parsed_sql = _parse_sql(sql_text)

    target_table = _extract_target_table(parsed_sql)
    source_tables = _extract_source_tables(parsed_sql)
    select_columns = _extract_select_columns(parsed_sql)

    source_column_details = _extract_columns_by_table(
        parsed_sql,
        source_tables,
    )

    target_columns = _extract_target_columns(select_columns)

    transformations = {
        "selected_columns": select_columns,
        "joins": _extract_joins(parsed_sql),
        "filters": _extract_filters(parsed_sql),
        "aggregations": _extract_aggregations(parsed_sql),
        "group_by": _extract_group_by(parsed_sql),
        "order_by": _extract_order_by(parsed_sql),
        "limit": _extract_limit(parsed_sql),
    }

    return {
        "artifact_type": "sql",
        "file_name": Path(file_path).name,
        "source_tables": source_column_details,
        "target_table": {
            "table_name": target_table,
            "columns": target_columns,
        },
        "transformations": transformations,
        "dependencies": [
            source["table_name"]
            for source in source_tables
        ],
        "confidence_score": 0.92,
        "parser": "sqlglot",
    }