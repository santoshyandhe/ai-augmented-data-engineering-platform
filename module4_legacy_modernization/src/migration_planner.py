from pathlib import Path
from typing import Any


def generate_migration_plan(
    analysis_results: list[dict[str, Any]],
    interpretation_result: dict[str, Any],
    dbt_results: list[dict[str, str]],
    output_dir: str | Path,
) -> Path:
    output_path = Path(output_dir) / "migration_plan.md"

    lines = [
        "# Legacy Pipeline Migration Plan",
        "",
        "## 1. Current State Summary",
        "",
        interpretation_result.get(
            "business_summary",
            "Business summary was not available.",
        ),
        "",
        "## 2. Technical Summary",
        "",
        interpretation_result.get(
            "technical_summary",
            "Technical summary was not available.",
        ),
        "",
        "## 3. Artifacts Analyzed",
        "",
    ]

    for artifact in analysis_results:
        lines.append(
            f"- **{artifact.get('artifact_type')}**: "
            f"{artifact.get('file_name')} "
            f"(confidence: {artifact.get('confidence_score')})"
        )

    lines.extend(
        [
            "",
            "## 4. Recommended Target State",
            "",
            "- Move transformation logic into version-controlled dbt models.",
            "- Use modern lakehouse or warehouse platform such as Databricks, Snowflake, or BigQuery.",
            "- Store source definitions and tests in dbt `schema.yml` files.",
            "- Add automated data quality tests for primary keys, null checks, and revenue metrics.",
            "- Use orchestration through Airflow, Prefect, Dagster, or Databricks Workflows.",
            "",
            "## 5. Generated dbt Artifacts",
            "",
        ]
    )

    if dbt_results:
        for dbt_result in dbt_results:
            lines.append(f"- dbt model: `{dbt_result.get('dbt_model_path')}`")
            lines.append(f"- dbt schema: `{dbt_result.get('dbt_schema_path')}`")
    else:
        lines.append("- No dbt artifacts generated.")

    lines.extend(
        [
            "",
            "## 6. Migration Recommendations",
            "",
        ]
    )

    for recommendation in interpretation_result.get(
        "migration_recommendations",
        [],
    ):
        lines.append(f"- {recommendation}")

    lines.extend(
        [
            "",
            "## 7. Risks and Gaps",
            "",
        ]
    )

    for risk in interpretation_result.get("risks_and_gaps", []):
        lines.append(f"- {risk}")

    lines.extend(
        [
            "",
            "## 8. Human Review Required",
            "",
        ]
    )

    for item in interpretation_result.get(
        "human_review_required",
        [],
    ):
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 9. Confidence Explanation",
            "",
            interpretation_result.get(
                "confidence_explanation",
                "Confidence explanation was not available.",
            ),
            "",
        ]
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_path