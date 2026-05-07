import re
from typing import List

from module1_sql_generator.src.models import (
    RetrievedContext,
    SchemaCatalog,
    Table,
    UDF,
    UDFCatalog,
)


def normalize_text(text: str) -> List[str]:
    """
    Convert text into lowercase searchable tokens.

    Example:
    "Top customers by lifetime value"
    becomes:
    ["top", "customers", "by", "lifetime", "value"]
    """
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def score_table(prompt_tokens: List[str], table: Table) -> int:
    """
    Score table relevance based on table name, description,
    column names, and column descriptions.
    """
    searchable_text_parts = [
        table.name,
        table.description or "",
        table.primary_key or "",
    ]

    for column in table.columns:
        searchable_text_parts.append(column.name)
        searchable_text_parts.append(column.description or "")

    searchable_text = " ".join(searchable_text_parts).lower()

    score = 0
    for token in prompt_tokens:
        if token in searchable_text:
            score += 1

    return score


def score_udf(prompt_tokens: List[str], udf: UDF) -> int:
    """
    Score UDF relevance based on name, signature, description,
    tags, business domain, and example usage.
    """
    searchable_text_parts = [
        udf.name,
        udf.signature,
        udf.return_type,
        udf.description,
        udf.example_usage,
        udf.business_domain or "",
        " ".join(udf.tags),
    ]

    searchable_text = " ".join(searchable_text_parts).lower()

    score = 0
    for token in prompt_tokens:
        if token in searchable_text:
            score += 1

    return score


def retrieve_relevant_tables(
    user_prompt: str,
    schema_catalog: SchemaCatalog,
    top_k: int = 3,
) -> List[Table]:
    """
    Retrieve the most relevant tables for a natural language prompt.
    """
    prompt_tokens = normalize_text(user_prompt)

    scored_tables = []
    for table in schema_catalog.tables:
        score = score_table(prompt_tokens, table)
        scored_tables.append((score, table))

    scored_tables.sort(key=lambda item: item[0], reverse=True)

    relevant_tables = [
        table for score, table in scored_tables
        if score > 0
    ]

    return relevant_tables[:top_k]


def retrieve_relevant_udfs(
    user_prompt: str,
    udf_catalog: UDFCatalog,
    top_k: int = 3,
) -> List[UDF]:
    """
    Retrieve the most relevant UDFs for a natural language prompt.
    """
    prompt_tokens = normalize_text(user_prompt)

    scored_udfs = []
    for udf in udf_catalog.udfs:
        score = score_udf(prompt_tokens, udf)
        scored_udfs.append((score, udf))

    scored_udfs.sort(key=lambda item: item[0], reverse=True)

    relevant_udfs = [
        udf for score, udf in scored_udfs
        if score > 0
    ]

    return relevant_udfs[:top_k]


def retrieve_context(
    user_prompt: str,
    schema_catalog: SchemaCatalog,
    udf_catalog: UDFCatalog,
    top_k_tables: int = 3,
    top_k_udfs: int = 3,
) -> RetrievedContext:
    """
    Retrieve relevant schema and UDF context for SQL generation.
    """
    relevant_tables = retrieve_relevant_tables(
        user_prompt=user_prompt,
        schema_catalog=schema_catalog,
        top_k=top_k_tables,
    )

    relevant_udfs = retrieve_relevant_udfs(
        user_prompt=user_prompt,
        udf_catalog=udf_catalog,
        top_k=top_k_udfs,
    )

    return RetrievedContext(
        relevant_tables=relevant_tables,
        relevant_udfs=relevant_udfs,
    )