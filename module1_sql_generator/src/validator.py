import re
from typing import Set

import sqlglot
from sqlglot import exp

from module1_sql_generator.src.models import (
    SchemaCatalog,
    UDFCatalog,
    ValidationIssue,
    ValidationReport,
)


UNSAFE_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "MERGE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
}


def validate_sql(
    sql: str,
    schema_catalog: SchemaCatalog,
    udf_catalog: UDFCatalog,
    dialect: str = "postgres",
) -> ValidationReport:
    """
    Validate generated SQL for syntax, safety, schema usage,
    join conditions, SELECT *, and UDF usage.
    """
    issues: list[ValidationIssue] = []

    parsed = None

    try:
        parsed = sqlglot.parse_one(sql, dialect=dialect)
    except Exception as exc:
        issues.append(
            ValidationIssue(
                severity="ERROR",
                message=f"SQL syntax validation failed: {exc}",
            )
        )
        return ValidationReport(is_valid=False, issues=issues)

    issues.extend(check_read_only(sql))
    issues.extend(check_select_star(parsed))
    issues.extend(check_join_conditions(parsed))
    issues.extend(check_tables_exist(parsed, schema_catalog))
    issues.extend(check_columns_exist(parsed, schema_catalog))
    issues.extend(check_udfs_exist_and_arity(parsed, udf_catalog))

    has_errors = any(issue.severity == "ERROR" for issue in issues)

    return ValidationReport(
        is_valid=not has_errors,
        issues=issues,
    )


def check_read_only(sql: str) -> list[ValidationIssue]:
    """
    Block unsafe non-read-only SQL statements.
    """
    issues = []
    upper_sql = sql.upper()

    for keyword in UNSAFE_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    message=f"Unsafe SQL keyword detected: {keyword}",
                )
            )

    return issues


def check_select_star(parsed: exp.Expression) -> list[ValidationIssue]:
    """
    Detect SELECT * usage.
    """
    issues = []

    for star in parsed.find_all(exp.Star):
        issues.append(
            ValidationIssue(
                severity="ERROR",
                message="SELECT * is not allowed. Use explicit columns.",
            )
        )

    return issues


def check_join_conditions(parsed: exp.Expression) -> list[ValidationIssue]:
    """
    Detect JOINs without ON condition.
    """
    issues = []

    for join in parsed.find_all(exp.Join):
        if join.args.get("on") is None:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    message="JOIN without ON condition detected.",
                )
            )

    return issues

def get_cte_names(parsed: exp.Expression) -> set[str]:
    """
    Extract CTE names from a SQL query.

    Example:
    WITH customer_ltv AS (...)
    returns {"customer_ltv"}
    """
    cte_names = set()

    for cte in parsed.find_all(exp.CTE):
        if cte.alias:
            cte_names.add(cte.alias.lower())

    return cte_names

def check_tables_exist(
    parsed: exp.Expression,
    schema_catalog: SchemaCatalog,
) -> list[ValidationIssue]:
    """
    Validate referenced base tables exist in schema catalog.
    Ignore CTE names because they are query-local virtual tables.
    """
    issues = []
    valid_tables = {table.name.lower() for table in schema_catalog.tables}
    cte_names = get_cte_names(parsed)

    for table in parsed.find_all(exp.Table):
        table_name = table.name.lower()

        if table_name in cte_names:
            continue

        if table_name not in valid_tables:
            issues.append(
                ValidationIssue(
                    severity="WARNING",
                    message=(
                        f"Referenced table '{table.name}' is not found in "
                        "schema catalog."
                    ),
                )
            )

    return issues

def build_table_column_map(schema_catalog: SchemaCatalog) -> dict[str, Set[str]]:
    """
    Build table to column-name lookup map.
    """
    return {
        table.name.lower(): {column.name.lower() for column in table.columns}
        for table in schema_catalog.tables
    }


def build_alias_to_table_map(parsed: exp.Expression) -> dict[str, str]:
    """
    Build alias-to-table mapping from SQL AST.

    Example:
    customers c -> {"c": "customers"}
    """
    alias_map = {}

    for table in parsed.find_all(exp.Table):
        table_name = table.name.lower()
        alias = table.alias

        if alias:
            alias_map[alias.lower()] = table_name
        else:
            alias_map[table_name] = table_name

    return alias_map


def check_columns_exist(
    parsed: exp.Expression,
    schema_catalog: SchemaCatalog,
) -> list[ValidationIssue]:
    """
    Validate referenced columns exist for known table aliases.

    Note:
    Columns from CTEs are difficult to validate statically in a simple prototype,
    so unresolved aliases are warnings instead of hard errors.
    """
    issues = []
    table_column_map = build_table_column_map(schema_catalog)
    alias_map = build_alias_to_table_map(parsed)

    for column in parsed.find_all(exp.Column):
        column_name = column.name.lower()
        table_alias = column.table

        if not table_alias:
            issues.append(
                ValidationIssue(
                    severity="WARNING",
                    message=f"Column '{column.name}' is not qualified with a table alias.",
                )
            )
            continue

        resolved_table = alias_map.get(table_alias.lower())

        if not resolved_table:
            issues.append(
                ValidationIssue(
                    severity="WARNING",
                    message=(
                        f"Could not resolve alias '{table_alias}' for column "
                        f"'{column.name}'. It may refer to a CTE."
                    ),
                )
            )
            continue

        valid_columns = table_column_map.get(resolved_table)

        if valid_columns and column_name not in valid_columns:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    message=(
                        f"Column '{column.name}' does not exist in table "
                        f"'{resolved_table}'."
                    ),
                )
            )

    return issues


def parse_udf_arg_count(signature: str) -> int:
    """
    Parse number of arguments from UDF signature.

    Example:
    fn_calc_customer_ltv(customer_id BIGINT, as_of_date DATE) -> 2
    """
    match = re.search(r"\((.*?)\)", signature)

    if not match:
        return 0

    args = match.group(1).strip()

    if not args:
        return 0

    return len([arg for arg in args.split(",") if arg.strip()])


def check_udfs_exist_and_arity(
    parsed: exp.Expression,
    udf_catalog: UDFCatalog,
) -> list[ValidationIssue]:
    """
    Validate referenced UDFs exist and argument count matches catalog signature.
    """
    issues = []

    udf_arg_counts = {
        udf.name.lower(): parse_udf_arg_count(udf.signature)
        for udf in udf_catalog.udfs
    }

    for function in parsed.find_all(exp.Anonymous):
        function_name = function.name.lower()

        if function_name not in udf_arg_counts:
            continue

        expected_arg_count = udf_arg_counts[function_name]
        actual_arg_count = len(function.expressions)

        if actual_arg_count != expected_arg_count:
            issues.append(
                ValidationIssue(
                    severity="ERROR",
                    message=(
                        f"UDF '{function.name}' expects {expected_arg_count} "
                        f"arguments but received {actual_arg_count}."
                    ),
                )
            )

    return issues