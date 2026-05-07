from module1_sql_generator.src.catalog_loader import load_catalogs
from module1_sql_generator.src.retriever import retrieve_context


SCHEMA_PATH = "module1_sql_generator/catalog/schema.yaml"
UDF_PATH = "module1_sql_generator/catalog/udfs.yaml"


def test_retriever_finds_customer_table_for_ltv_prompt():
    schema_catalog, udf_catalog = load_catalogs(SCHEMA_PATH, UDF_PATH)

    context = retrieve_context(
        "show top customers by lifetime value",
        schema_catalog,
        udf_catalog,
    )

    table_names = [table.name for table in context.relevant_tables]

    assert "customers" in table_names


def test_retriever_finds_ltv_udf_for_lifetime_value_prompt():
    schema_catalog, udf_catalog = load_catalogs(SCHEMA_PATH, UDF_PATH)

    context = retrieve_context(
        "show top customers by lifetime value",
        schema_catalog,
        udf_catalog,
    )

    udf_names = [udf.name for udf in context.relevant_udfs]

    assert "fn_calc_customer_ltv" in udf_names


def test_retriever_finds_fraud_udf_for_fraud_prompt():
    schema_catalog, udf_catalog = load_catalogs(SCHEMA_PATH, UDF_PATH)

    context = retrieve_context(
        "show suspicious transactions flagged for fraud",
        schema_catalog,
        udf_catalog,
    )

    udf_names = [udf.name for udf in context.relevant_udfs]

    assert "fn_is_fraud_flagged" in udf_names