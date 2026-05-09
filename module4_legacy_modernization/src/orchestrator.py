import asyncio
import json
from pathlib import Path

from src.artifact_scanner import scan_legacy_artifacts
from src.dbt_generator import generate_dbt_model
from src.llm_interpreter import interpret_legacy_metadata
from src.mermaid_writer import generate_mermaid_diagram
from src.gap_reporter import generate_gap_report
from src.migration_planner import generate_migration_plan


BASE_DIR = Path(__file__).resolve().parents[1]
LEGACY_DIR = BASE_DIR / "legacy_artifacts"
OUTPUTS_DIR = BASE_DIR / "outputs"


async def main():
    OUTPUTS_DIR.mkdir(exist_ok=True)

    analysis_results = scan_legacy_artifacts(
        LEGACY_DIR,
        OUTPUTS_DIR,
    )
    mermaid_path = generate_mermaid_diagram(
    analysis_results,
    OUTPUTS_DIR,
    )
    
    gap_report_path = generate_gap_report(
    analysis_results,
    OUTPUTS_DIR,
    )

    static_analysis_result = {
        "artifacts_analyzed": analysis_results
    }

    interpretation_result = await interpret_legacy_metadata(
        static_analysis_result
    )

    sql_artifacts = [
        artifact
        for artifact in analysis_results
        if artifact["artifact_type"] == "sql"
    ]

    dbt_results = []

    for sql_artifact in sql_artifacts:
        dbt_result = generate_dbt_model(
            sql_artifact,
            OUTPUTS_DIR,
        )

        dbt_results.append(dbt_result)

        migration_plan_path = generate_migration_plan(
            analysis_results,
            interpretation_result,
            dbt_results,
            OUTPUTS_DIR,
            )


    final_result = {
        "static_analysis": static_analysis_result,
        "llm_interpretation": interpretation_result,
        "dbt_generation": dbt_results,
        "generated_artifacts": {
        "mermaid_diagram": str(mermaid_path),
        "gap_report": str(gap_report_path),
        "migration_plan": str(migration_plan_path),
    },
    }

    output_path = OUTPUTS_DIR / "legacy_analysis_result.json"

    output_path.write_text(
        json.dumps(final_result, indent=4),
        encoding="utf-8",
    )

    print(json.dumps(final_result, indent=4))


if __name__ == "__main__":
    asyncio.run(main())