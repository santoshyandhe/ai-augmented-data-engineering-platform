import pandas as pd


def run_customer_etl():
    customers = pd.read_csv("data/customers.csv")
    orders = pd.read_csv("data/orders.csv")

    merged = customers.merge(
        orders,
        on="customer_id",
        how="inner",
    )

    summary = (
        merged
        .groupby(["customer_id", "first_name", "last_name"])
        .agg(
            total_revenue=("order_amount", "sum"),
            order_count=("order_id", "count"),
        )
        .reset_index()
    )

    summary.to_csv("output/customer_summary.csv", index=False)