import json
from pathlib import Path
from typing import Any

from src.python_analyzer import analyze_python_file
from src.sql_analyzer import analyze_sql_file
from src.yaml_analyzer import analyze_yaml_file
from src.dag_analyzer import analyze_dag_file

def _is_dag_file(file_path: Path) -> bool:
    content = file_path.read_text(encoding="utf-8").lower()

    dag_indicators = [
        "from airflow import dag",
        "airflow",
        "pythonoperator",
        "dag_id",
        "schedule_interval",
    ]

    return any(indicator in content for indicator in dag_indicators)


def _write_artifact_output(
    analysis_result: dict[str, Any],
    outputs_dir: Path,
) -> Path:
    artifact_type = analysis_result["artifact_type"]
    file_stem = Path(analysis_result["file_name"]).stem

    artifact_output_dir = outputs_dir / artifact_type
    artifact_output_dir.mkdir(parents=True, exist_ok=True)

    output_path = artifact_output_dir / f"{file_stem}_analysis.json"

    output_path.write_text(
        json.dumps(analysis_result, indent=4),
        encoding="utf-8",
    )

    return output_path


def scan_legacy_artifacts(
    legacy_dir: str | Path,
    outputs_dir: str | Path,
) -> list[dict[str, Any]]:
    legacy_path = Path(legacy_dir)
    output_path = Path(outputs_dir)

    analysis_results = []

    for artifact_path in legacy_path.iterdir():
        if artifact_path.is_dir():
            continue

        suffix = artifact_path.suffix.lower()

        if suffix == ".sql":
            result = analyze_sql_file(artifact_path)

        elif suffix == ".py":
            if _is_dag_file(artifact_path):
                result = analyze_dag_file(artifact_path)
            else:
                result = analyze_python_file(artifact_path)

    

        elif suffix in [".yaml", ".yml"]:
            result = analyze_yaml_file(artifact_path)





        else:
            result = {
                "artifact_type": "unknown",
                "file_name": artifact_path.name,
                "message": "Unsupported artifact type.",
                "confidence_score": 0.20,
                "parser": "extension_detection",
            }

        artifact_output_file = _write_artifact_output(
            result,
            output_path,
        )

        result["output_file"] = str(artifact_output_file)
        analysis_results.append(result)

    combined_inventory_path = output_path / "combined_inventory.json"
    combined_inventory_path.write_text(
        json.dumps(
            {"artifacts_analyzed": analysis_results},
            indent=4,
        ),
        encoding="utf-8",
    )

    return analysis_results