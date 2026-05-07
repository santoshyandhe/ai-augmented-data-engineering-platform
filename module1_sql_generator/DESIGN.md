# Module 1 — Intelligent SQL Generator

## Overview

This module implements a metadata-aware and database-aware SQL generation system that converts natural language requests into validated PostgreSQL SQL queries.

The system is designed to:
- Understand enterprise database schema metadata
- Discover and reuse existing UDFs
- Generate structured SQL using an LLM
- Validate generated SQL syntactically and semantically
- Execute database-level EXPLAIN / dry-run validation
- Return structured reasoning traces

The implementation emphasizes:
- accuracy
- explainability
- reusability
- validation
- modular architecture

---

# High-Level Architecture

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
Final SQL + Reasoning + Validation Report


Component Breakdown
1. Catalog Layer
Files
catalog/schema.yaml
catalog/udfs.yaml
Purpose

The catalog layer acts as the source of truth for:

database schema metadata
table definitions
column definitions
relationships
reusable UDFs
business descriptions
Why YAML?

YAML provides:

readability
portability
version control friendliness
easy extension

In production, these catalogs can be synchronized from:

PostgreSQL information_schema
Databricks Unity Catalog
Snowflake metadata
enterprise metadata systems
2. Pydantic Models
File
src/models.py
Purpose

Pydantic models provide:

strong typing
schema validation
structured contracts between components

This prevents malformed metadata and ensures consistency across the system.

3. Retrieval Layer
File
src/retriever.py
Purpose

The retrieval layer identifies relevant:

tables
columns
UDFs

for a user request.

Current Approach

The prototype uses keyword-based scoring against:

table names
column names
UDF descriptions
UDF tags
business domains
Future Improvements

The retriever can later be upgraded to:

vector embeddings
hybrid search
semantic ranking
metadata-aware RAG pipelines
4. Prompt Builder
File
src/prompt_builder.py
Purpose

The prompt builder constructs a controlled LLM prompt containing:

user request
schema context
UDF context
SQL generation rules
output formatting instructions
Why Controlled Prompting?

This reduces:

hallucination
invented tables
invented columns
unsafe SQL

and improves deterministic behavior.

5. LLM SQL Generator
File
src/llm_client.py
Purpose

Responsible for:

communicating with the LLM
requesting structured JSON output
parsing responses safely
Output Structure

The LLM returns:

SQL query
reasoning steps
tables used
UDFs used
assumptions
warnings

This improves explainability and auditability.

6. Validation Layer
File
src/validator.py
Purpose

The validator performs static SQL validation before database execution.

Validation Checks

Implemented checks:

SQL syntax validation
unsafe SQL detection
SELECT * prevention
JOIN validation
schema validation
column validation
UDF existence validation
UDF argument count validation
SQL Parser

Validation uses:

sqlglot

for dialect-aware SQL parsing.

7. Database Dry Run Layer
File
src/database_adapter.py
Purpose

Performs database-level:

EXPLAIN validation
dry-run query planning
Why This Matters

Static validation alone cannot guarantee database compatibility.

Database EXPLAIN validation confirms:

query plan generation
parser acceptance
execution feasibility
Current Implementation

Prototype implementation uses:

DuckDB

with:

in-memory schema creation
lightweight demo UDF registration
Production Extension

The adapter pattern supports future:

PostgreSQL adapters
Snowflake adapters
Databricks adapters
8. CLI Interface
File
src/cli.py
Purpose

Provides an end-to-end runnable demo.

Example:

python -m module1_sql_generator.src.cli "show top 10 customers by lifetime value"

The CLI displays:

generated SQL
reasoning trace
validation results
EXPLAIN output
Quality Dimension Coverage
Accuracy

Accuracy is addressed using:

schema-aware generation
sqlglot syntax parsing
table validation
column validation
UDF validation
database EXPLAIN validation

The system never trusts raw LLM output directly.

Reusability

Reusable business logic is externalized into:

catalog/udfs.yaml

The retriever dynamically selects relevant UDFs and injects them into the generation context.

This avoids duplicating business logic inline.

Validation

Validation occurs in multiple layers:

Static Validation
SQL syntax
schema checks
UDF checks
SQL best practices
Database Validation
EXPLAIN / dry-run query planning
Reasoning

The LLM returns structured reasoning traces including:

selected tables
selected UDFs
assumptions
generation rationale

This improves explainability and auditability.

Data Freshness

The prototype uses YAML catalogs with:

source system metadata
catalog versioning
last refreshed timestamps

Production implementation would use scheduled metadata synchronization from:

information_schema
Unity Catalog
enterprise metadata platforms
Future Improvements

Potential enhancements include:

embedding-based retrieval
hybrid semantic search
lineage-aware SQL generation
cost-based query optimization
automatic join inference
SQL execution benchmarking
policy-aware governance enforcement
row-level security awareness
query caching
multi-database dialect support
Technologies Used
Purpose	Technology
Language	Python
LLM	OpenAI GPT
SQL Parsing	sqlglot
Validation	Pydantic
Local Database	DuckDB
Prompt Templating	Jinja2
CLI	Typer
Console UI	Rich
Testing	Pytest
Conclusion

This module demonstrates a production-oriented approach to AI-assisted SQL generation by combining:

metadata grounding
reusable business logic
controlled prompting
static validation
database dry-run validation
structured reasoning

The architecture prioritizes reliability, modularity, explainability, and extensibility over naive direct LLM generation.