from pathlib import Path
from typing import Any


def generate_mermaid_diagram(
    analysis_results: list[dict[str, Any]],
    output_dir: str | Path,
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    mermaid_lines = [
        "flowchart LR",
    ]

    for artifact in analysis_results:
        artifact_type = artifact.get("artifact_type")

        if artifact_type == "sql":
            target_table = artifact.get("target_table", {}).get("table_name")

            for source in artifact.get("source_tables", []):
                source_table = source.get("table_name")

                if source_table and target_table:
                    mermaid_lines.append(
                        f'    "{source_table}" --> "{target_table}"'
                    )

        elif artifact_type == "python_etl":
            for source in artifact.get("sources", []):
                for target in artifact.get("targets", []):
                    mermaid_lines.append(
                        f'    "{source}" --> "{target}"'
                    )

        elif artifact_type == "yaml":
            target = artifact.get("target")

            for source in artifact.get("sources", []):
                if source and target:
                    mermaid_lines.append(
                        f'    "{source}" --> "{target}"'
                    )

        elif artifact_type == "dag":
            for dependency in artifact.get("dependencies", []):
                upstream = dependency.get("upstream_task_variable")
                downstream = dependency.get("downstream_task_variable")

                if upstream and downstream:
                    mermaid_lines.append(
                        f'    "{upstream}" --> "{downstream}"'
                    )

    diagram_text = "\n".join(mermaid_lines)

    diagram_path = output_path / "data_flow.mmd"
    diagram_path.write_text(
        diagram_text,
        encoding="utf-8",
    )

    return diagram_path