from module1_sql_generator.src.catalog_loader import load_catalogs


SCHEMA_PATH = "module1_sql_generator/catalog/schema.yaml"
UDF_PATH = "module1_sql_generator/catalog/udfs.yaml"


def test_catalog_loader_loads_schema_and_udfs():
    schema_catalog, udf_catalog = load_catalogs(SCHEMA_PATH, UDF_PATH)

    assert schema_catalog.database.name == "customer_analytics"
    assert len(schema_catalog.tables) == 4
    assert len(udf_catalog.udfs) == 5


def test_schema_contains_customers_table():
    schema_catalog, _ = load_catalogs(SCHEMA_PATH, UDF_PATH)

    table_names = [table.name for table in schema_catalog.tables]

    assert "customers" in table_names


def test_udf_catalog_contains_ltv_udf():
    _, udf_catalog = load_catalogs(SCHEMA_PATH, UDF_PATH)

    udf_names = [udf.name for udf in udf_catalog.udfs]

    assert "fn_calc_customer_ltv" in udf_names