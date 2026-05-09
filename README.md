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

# Module 1 — AI-Powered SQL Generator

## Overview

Module 1 implements a **metadata-aware** and **database-aware** SQL generation system that converts natural language requests into validated SQL queries.

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

---
##  Technologies Used
Python
OpenAI GPT
sqlglot
DuckDB
Pydantic
Streamlit
Jinja2
