import ast
from pathlib import Path
from typing import Any


def analyze_python_file(file_path: str | Path) -> dict[str, Any]:
    python_text = Path(file_path).read_text(encoding="utf-8")
    tree = ast.parse(python_text)

    functions = []
    read_sources = []
    write_targets = []
    transformations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

        if isinstance(node, ast.Call):
            call_text = ast.unparse(node)

            if "read_csv" in call_text:
                read_sources.append(call_text)

            if "to_csv" in call_text:
                write_targets.append(call_text)

            if ".merge(" in call_text:
                transformations.append("merge/join")

            if ".groupby(" in call_text:
                transformations.append("group_by")

            if ".agg(" in call_text:
                transformations.append("aggregation")

    return {
        "artifact_type": "python_etl",
        "file_name": Path(file_path).name,
        "functions": functions,
        "sources": read_sources,
        "targets": write_targets,
        "transformations": sorted(set(transformations)),
        "dependencies": read_sources,
        "confidence_score": 0.78,
        "parser": "python_ast",
    }