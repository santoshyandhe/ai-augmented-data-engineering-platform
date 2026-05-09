from pathlib import Path
from typing import Any

import yaml


def analyze_yaml_file(file_path: str | Path) -> dict[str, Any]:
    yaml_text = Path(file_path).read_text(encoding="utf-8")
    parsed_yaml = yaml.safe_load(yaml_text)

    return {
        "artifact_type": "yaml",
        "file_name": Path(file_path).name,
        "pipeline_name": parsed_yaml.get("pipeline_name"),
        "schedule": parsed_yaml.get("schedule"),
        "owner": parsed_yaml.get("owner"),
        "sources": parsed_yaml.get("sources", []),
        "target": parsed_yaml.get("target"),
        "quality_checks": parsed_yaml.get("quality_checks", []),
        "dependencies": parsed_yaml.get("sources", []),
        "confidence_score": 0.90,
        "parser": "pyyaml",
    }