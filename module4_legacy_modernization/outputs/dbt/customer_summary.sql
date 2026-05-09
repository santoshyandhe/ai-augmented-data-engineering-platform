{{ config(materialized='table') }}

WITH transformed AS (
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        SUM(o.order_amount) AS total_revenue,
        COUNT(o.order_id) AS order_count
    FROM {{ source('mart', 'customer_summary') }} 
    JOIN raw.orders AS o ON c.customer_id = o.customer_id
    WHERE o.order_date >= '2024-01-01'
    GROUP BY
        c.customer_id,
        c.first_name,
        c.last_name
)

SELECT
    customer_id,
    first_name,
    last_name,
    total_revenue,
    order_count
FROM transformed