from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def extract_customers():
    pass


def transform_customer_summary():
    pass


def load_customer_summary():
    pass


with DAG(
    dag_id="customer_summary_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id="extract_customers",
        python_callable=extract_customers,
    )

    transform_task = PythonOperator(
        task_id="transform_customer_summary",
        python_callable=transform_customer_summary,
    )

    load_task = PythonOperator(
        task_id="load_customer_summary",
        python_callable=load_customer_summary,
    )

    extract_task >> transform_task >> load_task