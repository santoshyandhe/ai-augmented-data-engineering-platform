import ast
import re
from pathlib import Path
from typing import Any


def analyze_dag_file(file_path: str | Path) -> dict[str, Any]:
    dag_text = Path(file_path).read_text(encoding="utf-8")
    tree = ast.parse(dag_text)

    dag_id = None
    schedule = None
    tasks = []
    dependencies = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

        if isinstance(node, ast.Call):
            call_text = ast.unparse(node)

            if "DAG(" in call_text:
                dag_id_match = re.search(
                    r"dag_id=['\"]([^'\"]+)['\"]",
                    call_text,
                )
                schedule_match = re.search(
                    r"schedule_interval=['\"]([^'\"]+)['\"]",
                    call_text,
                )

                if dag_id_match:
                    dag_id = dag_id_match.group(1)

                if schedule_match:
                    schedule = schedule_match.group(1)

            if "PythonOperator(" in call_text:
                task_id_match = re.search(
                    r"task_id=['\"]([^'\"]+)['\"]",
                    call_text,
                )

                callable_match = re.search(
                    r"python_callable=(\w+)",
                    call_text,
                )

                tasks.append(
                    {
                        "task_id": task_id_match.group(1)
                        if task_id_match
                        else None,
                        "callable": callable_match.group(1)
                        if callable_match
                        else None,
                    }
                )

    dependency_matches = re.findall(
        r"(\w+)\s*>>\s*(\w+)",
        dag_text,
    )

    for upstream, downstream in dependency_matches:
        dependencies.append(
            {
                "upstream_task_variable": upstream,
                "downstream_task_variable": downstream,
            }
        )

    return {
        "artifact_type": "dag",
        "file_name": Path(file_path).name,
        "dag_id": dag_id,
        "schedule": schedule,
        "functions": functions,
        "tasks": tasks,
        "dependencies": dependencies,
        "confidence_score": 0.82,
        "parser": "python_ast_airflow_static",
    }