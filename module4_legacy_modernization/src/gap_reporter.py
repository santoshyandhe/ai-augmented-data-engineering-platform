from pathlib import Path
from typing import Any
import json


def generate_gap_report(
    analysis_results: list[dict[str, Any]],
    output_dir: str | Path,
) -> Path:
    gaps = []

    for artifact in analysis_results:
        artifact_type = artifact.get("artifact_type")
        file_name = artifact.get("file_name")
        confidence_score = artifact.get("confidence_score", 0)

        if confidence_score < 0.80:
            gaps.append({
                "file_name": file_name,
                "artifact_type": artifact_type,
                "gap_type": "low_confidence",
                "description": (
                    f"Analyzer confidence is {confidence_score}. "
                    "Human review is recommended."
                ),
                "severity": "medium",
            })

        if artifact_type == "sql":
            if not artifact.get("target_table", {}).get("table_name"):
                gaps.append({
                    "file_name": file_name,
                    "artifact_type": artifact_type,
                    "gap_type": "missing_target_table",
                    "description": "SQL target table could not be identified.",
                    "severity": "high",
                })

            if not artifact.get("source_tables"):
                gaps.append({
                    "file_name": file_name,
                    "artifact_type": artifact_type,
                    "gap_type": "missing_source_tables",
                    "description": "SQL source tables could not be identified.",
                    "severity": "high",
                })

            if not artifact.get("transformations", {}).get("filters"):
                gaps.append({
                    "file_name": file_name,
                    "artifact_type": artifact_type,
                    "gap_type": "missing_filter_logic",
                    "description": "No WHERE filter detected. Confirm whether full load is intended.",
                    "severity": "low",
                })

        elif artifact_type == "python_etl":
            if not artifact.get("sources"):
                gaps.append({
                    "file_name": file_name,
                    "artifact_type": artifact_type,
                    "gap_type": "missing_python_sources",
                    "description": "Python ETL source reads were not detected.",
                    "severity": "high",
                })

            if not artifact.get("targets"):
                gaps.append({
                    "file_name": file_name,
                    "artifact_type": artifact_type,
                    "gap_type": "missing_python_targets",
                    "description": "Python ETL output writes were not detected.",
                    "severity": "high",
                })

        elif artifact_type == "yaml":
            if not artifact.get("owner"):
                gaps.append({
                    "file_name": file_name,
                    "artifact_type": artifact_type,
                    "gap_type": "missing_owner",
                    "description": "Pipeline owner is missing from YAML config.",
                    "severity": "medium",
                })

            if not artifact.get("quality_checks"):
                gaps.append({
                    "file_name": file_name,
                    "artifact_type": artifact_type,
                    "gap_type": "missing_quality_checks",
                    "description": "No quality checks are defined in YAML config.",
                    "severity": "medium",
                })

        elif artifact_type == "dag":
            if not artifact.get("schedule"):
                gaps.append({
                    "file_name": file_name,
                    "artifact_type": artifact_type,
                    "gap_type": "missing_schedule",
                    "description": "DAG schedule could not be detected.",
                    "severity": "medium",
                })

            if not artifact.get("dependencies"):
                gaps.append({
                    "file_name": file_name,
                    "artifact_type": artifact_type,
                    "gap_type": "missing_task_dependencies",
                    "description": "No DAG task dependencies were detected.",
                    "severity": "high",
                })

    output_path = Path(output_dir) / "gap_report.json"

    output_path.write_text(
        json.dumps(
            {
                "gap_count": len(gaps),
                "gaps": gaps,
            },
            indent=4,
        ),
        encoding="utf-8",
    )

    return output_path