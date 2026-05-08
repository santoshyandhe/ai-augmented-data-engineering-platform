import json


def write_report(results, output_path="reports/report.json"):
    with open(output_path, "w") as file:
        json.dump(results, file, indent=4)

    return output_path