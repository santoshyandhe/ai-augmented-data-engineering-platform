from module1_sql_generator.src.catalog_loader import load_catalogs
from module1_sql_generator.src.validator import validate_sql


SCHEMA_PATH = "module1_sql_generator/catalog/schema.yaml"
UDF_PATH = "module1_sql_generator/catalog/udfs.yaml"


def test_valid_sql_passes_validation():
    schema_catalog, udf_catalog = load_catalogs(SCHEMA_PATH, UDF_PATH)

    sql = """
    WITH customer_ltv AS (
        SELECT
            c.customer_id,
            fn_calc_customer_ltv(c.customer_id, CURRENT_DATE) AS lifetime_value
        FROM customers c
    )
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        cl.lifetime_value
    FROM customers c
    JOIN customer_ltv cl
        ON c.customer_id = cl.customer_id
    ORDER BY cl.lifetime_value DESC
    LIMIT 10
    """

    report = validate_sql(sql, schema_catalog, udf_catalog)

    assert report.is_valid is True


def test_select_star_fails_validation():
    schema_catalog, udf_catalog = load_catalogs(SCHEMA_PATH, UDF_PATH)

    sql = "SELECT * FROM customers"

    report = validate_sql(sql, schema_catalog, udf_catalog)

    assert report.is_valid is False
    assert any("SELECT *" in issue.message for issue in report.issues)


def test_unsafe_sql_fails_validation():
    schema_catalog, udf_catalog = load_catalogs(SCHEMA_PATH, UDF_PATH)

    sql = "DROP TABLE customers"

    report = validate_sql(sql, schema_catalog, udf_catalog)

    assert report.is_valid is False
    assert any("Unsafe SQL keyword" in issue.message for issue in report.issues)


def test_udf_wrong_argument_count_fails_validation():
    schema_catalog, udf_catalog = load_catalogs(SCHEMA_PATH, UDF_PATH)

    sql = """
    SELECT
        c.customer_id,
        fn_calc_customer_ltv(c.customer_id) AS lifetime_value
    FROM customers c
    """

    report = validate_sql(sql, schema_catalog, udf_catalog)

    assert report.is_valid is False
    assert any("expects 2 arguments" in issue.message for issue in report.issues)