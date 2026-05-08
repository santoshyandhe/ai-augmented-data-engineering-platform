import importlib
import sys
import types
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pyspark.sql import Row
from pyspark.sql import types as T


class ColumnStub:
    def __init__(self, expr):
        self.expr = expr

    def alias(self, name):
        return ColumnStub(f"alias({self.expr},{name})")

    def cast(self, dtype):
        return ColumnStub(f"cast({self.expr},{dtype})")

    def isNotNull(self):
        return ColumnStub(f"isNotNull({self.expr})")


class DataFrameStub:
    def __init__(self, name="df"):
        self.name = name
        self.calls = []

    def select(self, *args):
        self.calls.append(("select", args))
        return self

    def where(self, condition):
        self.calls.append(("where", condition))
        return self

    def withWatermark(self, *args):
        self.calls.append(("withWatermark", args))
        return self

    def groupBy(self, *args):
        self.calls.append(("groupBy", args))
        return GroupedDataStub(self)


class GroupedDataStub:
    def __init__(self, df):
        self.df = df

    def agg(self, *args, **kwargs):
        self.df.calls.append(("agg", args, kwargs))
        return self.df


class SparkReadStreamStub:
    def __init__(self):
        self.calls = []
        self._df = DataFrameStub("stream")

    def format(self, value):
        self.calls.append(("format", value))
        return self

    def option(self, key, value):
        self.calls.append(("option", key, value))
        return self

    def load(self):
        self.calls.append(("load",))
        return self._df


class SparkStub:
    def __init__(self):
        self.readStream = SparkReadStreamStub()


class DLTStub(types.ModuleType):
    def __init__(self):
        super().__init__("dlt")
        self.tables = []
        self.expects = []
        self._read_stream = MagicMock()

    def table(self, **kwargs):
        def decorator(fn):
            self.tables.append((kwargs, fn.__name__))
            return fn
        return decorator

    def expect_or_drop(self, name, expr):
        def decorator(fn):
            self.expects.append((name, expr, fn.__name__))
            return fn
        return decorator

    def read_stream(self, name):
        return self._read_stream(name)


@pytest.fixture()
def module_under_test(monkeypatch):
    dlt_stub = DLTStub()
    monkeypatch.setitem(sys.modules, "dlt", dlt_stub)
    monkeypatch.setitem(sys.modules, "pyspark", importlib.import_module("pyspark"))
    monkeypatch.setitem(sys.modules, "pyspark.sql", importlib.import_module("pyspark.sql"))
    monkeypatch.setitem(sys.modules, "pyspark.sql.functions", importlib.import_module("pyspark.sql.functions"))
    monkeypatch.setitem(sys.modules, "pyspark.sql.types", importlib.import_module("pyspark.sql.types"))

    mod = importlib.import_module("generated_module")
    mod.dlt = dlt_stub
    mod.spark = SparkStub()
    return mod


def test_event_schema_has_expected_fields(module_under_test):
    schema = module_under_test.EVENT_SCHEMA
    assert isinstance(schema, T.StructType)
    assert [f.name for f in schema.fields] == ["event_id", "event_type", "user_id", "event_ts", "value"]
    assert schema["event_ts"].dataType == T.TimestampType()
    assert schema["value"].dataType == T.DoubleType()


def test_parse_event_payload_returns_from_json_expression(module_under_test):
    col = ColumnStub("payload")
    parsed = module_under_test.parse_event_payload(col)
    assert "from_json" in str(parsed)
    assert "payload" in str(parsed)


def test_bronze_kafka_events_builds_expected_stream(module_under_test):
    df = module_under_test.bronze_kafka_events()
    assert isinstance(df, DataFrameStub)
    read_calls = module_under_test.spark.readStream.calls
    assert read_calls[0] == ("format", "kafka")
    assert ("option", "kafka.bootstrap.servers", "KAFKA_BOOTSTRAP_SERVERS") in read_calls
    assert ("option", "subscribe", "KAFKA_TOPIC") in read_calls
    assert ("option", "startingOffsets", "latest") in read_calls
    assert ("load",) in read_calls
    select_calls = [c for c in df.calls if c[0] == "select"]
    assert select_calls


def test_silver_events_requires_bronze_stream_and_filters_null_event_id(module_under_test, monkeypatch):
    bronze_df = DataFrameStub("bronze")
    module_under_test.dlt._read_stream = MagicMock(return_value=bronze_df)

    result = module_under_test.silver_events()

    module_under_test.dlt._read_stream.assert_called_once_with("bronze_kafka_events")
    assert result is bronze_df or isinstance(result, DataFrameStub)
    assert any(call[0] == "where" for call in bronze_df.calls)


def test_gold_event_metrics_builds_windowed_aggregation(module_under_test):
    silver_df = DataFrameStub("silver")
    module_under_test.dlt._read_stream = MagicMock(return_value=silver_df)

    result = module_under_test.gold_event_metrics()

    module_under_test.dlt._read_stream.assert_called_once_with("silver_events")
    assert result is silver_df or isinstance(result, DataFrameStub)
    assert any(call[0] == "withWatermark" for call in silver_df.calls)
    assert any(call[0] == "groupBy" for call in silver_df.calls)
    assert any(call[0] == "agg" for call in silver_df.calls)


def test_silver_events_decorators_registered(module_under_test):
    names = [x[0] for x in module_under_test.dlt.expects]
    assert names == ["valid_event_id", "valid_event_type", "valid_user_id", "valid_event_ts"]


def test_module_decorated_tables_registered(module_under_test):
    table_names = [t[0]["name"] for t in module_under_test.dlt.tables]
    assert table_names == ["bronze_kafka_events", "silver_events", "gold_event_metrics"]
