# Legacy Pipeline Migration Plan

## 1. Current State Summary

This appears to be a daily customer revenue summary pipeline. It combines customer master data with order data to produce a customer-level summary containing customer identity, total revenue, and order count. The business logic is inferred from the transformations and suggests reporting or analytics use for customer performance tracking.

## 2. Technical Summary

Lineage is available across DAG, Python ETL, SQL, and YAML. Sources include raw.customers, raw.orders, and local CSV files data/customers.csv and data/orders.csv. The SQL builds mart.customer_summary from raw.customers and raw.orders with an inner join on customer_id, a date filter on orders since 2024-01-01, and aggregation at customer_id/first_name/last_name grain. The Python ETL reads the same CSV sources, performs merge/groupby/aggregation, and writes output/customer_summary.csv. The Airflow DAG customer_summary_dag runs daily with three tasks: extract_customers -> transform_customer_summary -> load_customer_summary. The YAML config confirms the same pipeline name, owner, sources, target, and basic quality checks. There is partial inconsistency between file-based ETL and warehouse-style SQL/YAML targets, but the overall intent is clear.

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

- Consolidate the pipeline into a single orchestration pattern, preferably dbt for SQL transformations plus Airflow/Databricks Jobs for scheduling.
- Implement mart.customer_summary as a dbt model with explicit tests for not_null customer_id and non-negative total_revenue.
- Standardize sources by replacing local CSV reads with governed lakehouse/warehouse input tables or external tables.
- If migrating to Databricks, use Delta tables for raw and mart layers and preserve the daily incremental load pattern.
- Document the business grain as one row per customer per run/date scope and validate whether the 2024-01-01 filter is a permanent rule or a temporary backfill constraint.
- Add lineage and data quality checks around duplicate customers, missing orders, and late-arriving orders before production migration.

## 7. Risks and Gaps

- Lineage is mixed between file-based Python ETL and SQL/YAML warehouse objects, so the authoritative source of truth is unclear.
- The SQL references mart.customer_summary in source_tables metadata, which may indicate parser ambiguity or self-referential lineage.
- The Python ETL transformation details are high-level only; join keys, aggregation columns, and filter logic are not fully visible.
- The order_date >= '2024-01-01' filter may exclude historical revenue and could change business meaning if not intentional.
- No explicit handling of duplicates, null customer_ids, or late-arriving orders is shown.
- No retry, alerting, partitioning, or incremental strategy is exposed in the DAG metadata.

## 8. Human Review Required

- Confirm whether the 2024-01-01 date filter is a business requirement, backfill boundary, or temporary test condition.
- Validate the intended grain of mart.customer_summary and whether one record per customer is sufficient.
- Confirm whether raw/customers and raw/orders are the true governed sources or whether the CSV files are only local development inputs.
- Review the SQL source_tables metadata for the apparent mart.customer_summary self-reference.
- Validate the quality checks and define failure actions for null customer_id and negative revenue.
- Confirm DAG task dependencies are complete, since only extract_task -> transform_task is explicitly listed.

## 9. Confidence Explanation

Confidence is moderately high because the SQL and YAML provide strong, consistent lineage and business logic, while the DAG confirms orchestration. Confidence is reduced by partial and potentially conflicting Python file-based ETL lineage, limited visibility into function internals, and some metadata ambiguity in the SQL source table listing.
