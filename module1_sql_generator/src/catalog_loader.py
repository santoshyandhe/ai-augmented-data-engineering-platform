from pathlib import Path
from typing import Tuple

import yaml

from module1_sql_generator.src.models import SchemaCatalog, UDFCatalog


def load_yaml_file(file_path: str | Path) -> dict:
    """
    Load a YAML file and return it as a dictionary.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if data is None:
        raise ValueError(f"YAML file is empty: {path}")

    return data


def load_schema_catalog(schema_path: str | Path) -> SchemaCatalog:
    """
    Load and validate the database schema catalog.
    """
    raw_data = load_yaml_file(schema_path)
    return SchemaCatalog(**raw_data)


def load_udf_catalog(udf_path: str | Path) -> UDFCatalog:
    """
    Load and validate the UDF catalog.
    """
    raw_data = load_yaml_file(udf_path)
    return UDFCatalog(**raw_data)


def load_catalogs(
    schema_path: str | Path,
    udf_path: str | Path
) -> Tuple[SchemaCatalog, UDFCatalog]:
    """
    Load both schema and UDF catalogs.
    """
    schema_catalog = load_schema_catalog(schema_path)
    udf_catalog = load_udf_catalog(udf_path)

    return schema_catalog, udf_catalog