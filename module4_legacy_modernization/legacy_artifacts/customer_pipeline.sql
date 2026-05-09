INSERT INTO mart.customer_summary
SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    SUM(o.order_amount) AS total_revenue,
    COUNT(o.order_id) AS order_count
FROM raw.customers c
JOIN raw.orders o
    ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01'
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name;