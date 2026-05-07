from abc import ABC, abstractmethod

import duckdb

from module1_sql_generator.src.models import SchemaCatalog


class DatabaseAdapter(ABC):
    """
    Abstract database adapter.

    Any real database implementation should provide:
    - setup_demo_schema
    - explain_query
    """

    @abstractmethod
    def setup_demo_schema(self) -> None:
        pass

    @abstractmethod
    def explain_query(self, sql: str) -> tuple[bool, str]:
        pass


class DuckDBAdapter(DatabaseAdapter):
    """
    DuckDB implementation used for local demo dry-run validation.
    """

    def __init__(self, schema_catalog: SchemaCatalog) -> None:
        self.schema_catalog = schema_catalog
        self.connection = duckdb.connect(database=":memory:")

    def setup_demo_schema(self) -> None:
        """
        Create local demo tables in DuckDB based on schema catalog.

        Note:
        This is only for EXPLAIN validation, not real production data.
        """
        for table in self.schema_catalog.tables:
            column_definitions = []

            for column in table.columns:
                duckdb_type = self._map_type_to_duckdb(column.type)
                column_definitions.append(f"{column.name} {duckdb_type}")

            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table.name} (
                {", ".join(column_definitions)}
            )
            """

            self.connection.execute(create_sql)

        self._register_demo_udfs()

    def explain_query(self, sql: str) -> tuple[bool, str]:
        """
        Run EXPLAIN against DuckDB.

        Returns:
            (True, explain_output) if successful
            (False, error_message) if failed
        """
        try:
            result = self.connection.execute(f"EXPLAIN {sql}").fetchall()
            explain_text = "\n".join(str(row) for row in result)
            return True, explain_text

        except Exception as exc:
            return False, str(exc)

    def _map_type_to_duckdb(self, source_type: str) -> str:
        """
        Map catalog/Postgres-style types to DuckDB-compatible types.
        """
        normalized_type = source_type.upper()

        type_mapping = {
            "BIGINT": "BIGINT",
            "INTEGER": "INTEGER",
            "INT": "INTEGER",
            "VARCHAR": "VARCHAR",
            "TEXT": "VARCHAR",
            "DATE": "DATE",
            "TIMESTAMP": "TIMESTAMP",
            "NUMERIC": "DOUBLE",
            "DECIMAL": "DOUBLE",
            "BOOLEAN": "BOOLEAN",
            "BOOL": "BOOLEAN",
        }

        return type_mapping.get(normalized_type, "VARCHAR")

    def _register_demo_udfs(self) -> None:
        """
        Register Python-backed DuckDB demo UDFs.

        These do not implement real business logic.
        They only allow EXPLAIN/dry-run to understand function calls.
        """

        def fn_calc_customer_ltv(customer_id: int, as_of_date) -> float:
            return float(customer_id or 0) * 10.0

        def fn_is_fraud_flagged(transaction_id: int) -> bool:
            return False

        def fn_customer_risk_score(customer_id: int) -> float:
            return 0.75

        def fn_mask_account_number(account_number: str) -> str:
            if account_number is None:
                return None
            return "****" + str(account_number)[-4:]

        def fn_calculate_loan_eligibility(
            customer_id: int,
            requested_amount: float,
        ) -> bool:
            return True

        self.connection.create_function(
            "fn_calc_customer_ltv",
            fn_calc_customer_ltv,
            return_type="DOUBLE",
        )

        self.connection.create_function(
            "fn_is_fraud_flagged",
            fn_is_fraud_flagged,
            return_type="BOOLEAN",
        )

        self.connection.create_function(
            "fn_customer_risk_score",
            fn_customer_risk_score,
            return_type="DOUBLE",
        )

        self.connection.create_function(
            "fn_mask_account_number",
            fn_mask_account_number,
            return_type="VARCHAR",
        )

        self.connection.create_function(
            "fn_calculate_loan_eligibility",
            fn_calculate_loan_eligibility,
            return_type="BOOLEAN",
        )