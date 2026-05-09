# Legacy Pipeline Migration Plan

## 1. Current State Summary

This pipeline appears to build a daily customer summary mart. It combines customer master data with order transactions to produce customer-level revenue and order counts, likely for reporting or analytics. The business meaning is inferred from the table names and aggregations.

## 2. Technical Summary

The DAG customer_summary_dag runs daily and orchestrates three tasks: extract_customers, transform_customer_summary, and load_customer_summary, with an explicit dependency from extract to transform; the load dependency is not shown, so lineage is partial. The Python ETL reads data/customers.csv and data/orders.csv, performs merge/join, group_by, and aggregation, then writes output/customer_summary.csv. The SQL source reads raw.customers c and raw.orders o, joins on customer_id, filters orders from 2024-01-01 onward, groups by customer_id, first_name, and last_name, and writes to mart.customer_summary with total_revenue and order_count. The YAML config confirms the pipeline name customer_summary_pipeline, daily schedule, owner data_engineering, sources raw.customers/raw.orders, target mart.customer_summary, and data quality checks for non-null customer_id and non-negative total_revenue.

## 3. Artifacts Analyzed

- **dag**: customer_dag.py (confidence: 0.82)
- **python_etl**: customer_etl.py (confidence: 0.78)
- **sql**: customer_pipeline.sql (confidence: 0.92)
- **yaml**: pipeline_config.yaml (confidence: 0.9)

## 4. Recommended Target State

- Move transformation logic into version-controlled dbt models.
- Use modern lakehouse or warehouse platform such as Databricks, Snowflake, or BigQuery.
- Store source definitions and tests in dbt `schema.yml` files.
- Add automated data quality tests for primary keys, null checks, and revenue metrics.
- Use orchestration through Airflow, Prefect, Dagster, or Databricks Workflows.

## 5. Generated dbt Artifacts

- dbt model: `C:\Users\santo\DataEngineer\Trendytech Superstar\projects\ai-augmented-data-engineering-platform\module4_legacy_modernization\outputs\dbt\customer_summary.sql`
- dbt schema: `C:\Users\santo\DataEngineer\Trendytech Superstar\projects\ai-augmented-data-engineering-platform\module4_legacy_modernization\outputs\dbt\schema.yml`

## 6. Migration Recommendations

- Model the summary logic as a dbt incremental or table model on top of raw.customer and raw.orders, with tests for not_null and accepted values/non-negative revenue.
- Move CSV reads/writes into cloud storage or a lakehouse staging layer before migrating to Databricks/Snowflake.
- Use a single governed transformation layer for the join and aggregation to avoid divergence between Python ETL and SQL logic.
- Define the missing DAG dependency explicitly so extract, transform, and load lineage is fully captured.
- Parameterize the date filter (currently hardcoded to 2024-01-01) for maintainability and backfills.
- Implement orchestration retries, alerts, and idempotent writes for the mart.customer_summary target.

## 7. Risks and Gaps

- Lineage is partial because the DAG only exposes extract -> transform dependency; load dependency is not shown.
- There is potential logic duplication between the Python ETL and SQL artifacts; it is unclear which is authoritative.
- The SQL artifact includes mart.customer_summary in source_tables and as target_table, which may reflect self-reference or parser ambiguity.
- The hardcoded order_date filter may cause silent data gaps for historical backfills or changing business windows.
- CSV-based file paths in Python suggest local-file dependencies and weaker production robustness.
- No retry, SLA, alerting, or failure handling details are available from the DAG analysis.
- No schema enforcement, null handling, or deduplication logic is visible in the Python ETL.

## 8. Human Review Required

- Confirm whether Python ETL or SQL is the production source of truth for customer_summary.
- Validate the intended business definition of total_revenue and whether refunds/cancellations should be excluded.
- Confirm the missing DAG dependency between transform_customer_summary and load_customer_summary.
- Review whether the 2024-01-01 filter is intentional and whether it should be configurable.
- Verify if customer names should be aggregated at customer_id grain only, especially if names can change over time.
- Check whether raw.orders should be filtered by status in addition to order_date.

## 9. Confidence Explanation

Confidence is high for the SQL and YAML interpretation because the parsers reported explicit tables, joins, filters, aggregations, schedule, owner, and quality checks. Confidence is moderate for the DAG because one task dependency is missing from the static metadata. Confidence is moderate for the Python ETL because only high-level pandas operations and file paths were detected, so some business logic is inferred rather than fully visible.
