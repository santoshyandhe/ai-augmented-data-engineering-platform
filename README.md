# AI-Augmented Data Engineering Platform

## Overview

This repository contains a production-oriented platform demonstrating how Artificial Intelligence can be integrated into modern data engineering workflows.

The platform showcases:

- AI-assisted SQL generation
- Intelligent CSV reconciliation
- Multi-agent engineering workflows
- Legacy pipeline modernization
- Metadata-aware static analysis
- LLM-assisted interpretation
- dbt migration generation
- Enterprise-style modular architecture

---

# Repository Overview

| Module | Description | Status |
|---|---|---|
| Module 1 | AI-Powered SQL Generator | ✅ Completed |
| Module 2 | AI CSV Reconciliation Engine | ✅ Completed |
| Module 3 | Multi-Agent Engineering Workflow | ✅ Completed |
| Module 4 | Legacy Pipeline Modernization System | ✅ Completed |
| Module 5 | Databricks AI Engineering Copilot | 🚧 Planned |

---

# Module 1 — AI-Powered SQL Generator

## Overview

Module 1 implements a metadata-aware and database-aware SQL generation system that converts natural language requests into validated SQL queries.

The system supports:

- Schema-aware SQL generation
- UDF-aware query generation
- Structured reasoning traces
- Static SQL validation
- Database EXPLAIN / dry-run validation
- Streamlit UI integration
- Modular enterprise-style architecture

---

## Workflow

```text
User Prompt
    ↓
Catalog Loader
    ↓
Schema/UDF Retriever
    ↓
Prompt Builder
    ↓
LLM SQL Generator
    ↓
Static SQL Validator
    ↓
Database EXPLAIN / Dry Run
    ↓
Final SQL + Validation Report
```

---

## Technologies Used

| Purpose | Technology |
|---|---|
| Language | Python |
| LLM | OpenAI GPT |
| SQL Parsing | sqlglot |
| Database | DuckDB |
| Validation | Pydantic |
| UI | Streamlit |
| Prompting | Jinja2 |

---

## Run Module 1

```bash
streamlit run module1_sql_generator/app.py
```

---

# Module 2 — AI CSV Reconciliation Engine

## Overview

Module 2 implements an intelligent CSV reconciliation engine for comparing source and target datasets.

The system supports:

- Automatic CSV loading
- Intelligent column matching
- Automatic key detection
- Row-level comparison
- Missing/new record detection
- Value mismatch detection
- Downloadable reconciliation reports
- JSON-based comparison outputs

---

## Workflow

```text
Source CSV + Target CSV
            ↓
DataFrame Loading
            ↓
Column Matching
            ↓
Key Detection
            ↓
Row-Level Comparison
            ↓
Difference Report Generation
```

---

## Technologies Used

| Purpose | Technology |
|---|---|
| Language | Python |
| Data Processing | Pandas |
| UI | Streamlit |
| Reporting | JSON |
| File Handling | CSV |

---

## Run Module 2

```bash
python module2_csv_comparison/app.py
```

---

# Module 3 — Multi-Agent Engineering Workflow

## Overview

Module 3 implements a multi-agent AI workflow for automated software engineering orchestration.

The system demonstrates:

- Multi-agent collaboration
- Workflow orchestration
- Retry feedback loops
- Structured JSON outputs
- Automated review pipelines
- AI-assisted code generation
- AI-assisted testing
- AI-assisted review workflows

---

## Agents

| Agent | Responsibility |
|---|---|
| Developer Agent | Generates implementation |
| Tester Agent | Generates tests |
| Reviewer Agent | Reviews implementation quality |

---

## Workflow

```text
User Request
    ↓
Developer Agent
    ↓
Tester Agent
    ↓
Reviewer Agent
    ↓
Approval / Retry Loop
```

---

## Technologies Used

| Purpose | Technology |
|---|---|
| LLM Framework | OpenAI Agents SDK |
| Model | GPT-4.1-mini |
| Language | Python |
| Workflow | Async orchestration |
| Output Format | JSON |

---

## Example Prompt

```text
Create a PySpark pipeline that ingests Kafka events into Delta Lake bronze/silver tables with watermarking and deduplication.
```

---

## Run Module 3

```bash
python module3_agent_personas/src/orchestrator.py
```

---

# Module 4 — Legacy Pipeline Modernization System

## Overview

Module 4 implements an AI-assisted modernization system for legacy data engineering pipelines.

The platform automatically analyzes legacy artifacts and generates modernization insights and migration outputs.

Supported artifacts include:

- SQL scripts
- Python ETL files
- YAML configs
- DAG definitions

The system supports:

- Automatic artifact discovery
- Static analysis
- LLM-assisted interpretation
- Metadata extraction
- Gap analysis
- Mermaid lineage generation
- dbt model generation
- Migration plan generation
- Enterprise modernization workflows

---

## Workflow

```text
Legacy Artifacts
        ↓
Artifact Scanner
        ↓
Static Analyzers
        ├── SQL Analyzer
        ├── Python ETL Analyzer
        ├── YAML Analyzer
        └── DAG Analyzer
        ↓
Structured Metadata Inventory
        ↓
LLM-Assisted Interpretation
        ↓
Gap Analysis
        ↓
Mermaid Lineage Generation
        ↓
dbt Model Generation
        ↓
Migration Plan Generation
```

---

## Generated Outputs

```text
outputs/
├── sql/
├── python_etl/
├── yaml/
├── dag/
├── dbt/
├── combined_inventory.json
├── gap_report.json
├── migration_plan.md
└── data_flow.mmd
```

---

## Technologies Used

| Purpose | Technology |
|---|---|
| SQL Parsing | sqlglot |
| Python Parsing | Python AST |
| YAML Parsing | PyYAML |
| LLM Framework | OpenAI Agents SDK |
| UI | Streamlit |
| Visualization | Mermaid |
| Migration | dbt generation |

---

## Run Module 4

```bash
streamlit run module4_legacy_modernization/app.py
```

---

# Design Principles

The platform emphasizes:

- Metadata-driven engineering
- AI-assisted workflows
- Explainability
- Structured outputs
- Human-in-the-loop validation
- Modular architecture
- Enterprise-style engineering practices
- Extensibility and maintainability

---

# Future Roadmap

## Module 5 — Databricks AI Engineering Copilot

Planned capabilities include:

- Databricks SDK integration
- Notebook generation
- DLT pipeline generation
- Unity Catalog awareness
- AI-assisted optimization
- Cluster/job orchestration
- Governance-aware engineering workflows

---

# Conclusion

This repository demonstrates practical applications of Artificial Intelligence in data engineering through:

- metadata-aware SQL generation
- intelligent reconciliation
- multi-agent orchestration
- legacy modernization automation
- migration acceleration
- lineage and governance analysis

The platform combines:

- static analysis
- LLM reasoning
- workflow orchestration
- validation layers
- modernization tooling

to simulate real-world enterprise AI engineering systems.
