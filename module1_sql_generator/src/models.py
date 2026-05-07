from typing import List, Optional
from pydantic import BaseModel, Field


class Column(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class Table(BaseModel):
    name: str
    description: Optional[str] = None
    primary_key: Optional[str] = None
    columns: List[Column]


class Relationship(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str


class DatabaseMetadata(BaseModel):
    name: str
    dialect: str = "postgres"
    version: Optional[str] = None


class SchemaCatalog(BaseModel):
    database: DatabaseMetadata
    tables: List[Table]
    relationships: List[Relationship] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class UDF(BaseModel):
    name: str
    signature: str
    return_type: str
    description: str
    example_usage: str
    tags: List[str] = Field(default_factory=list)
    business_domain: Optional[str] = None
    last_refreshed_at: Optional[str] = None


class UDFCatalog(BaseModel):
    udfs: List[UDF]
    metadata: dict = Field(default_factory=dict)


class RetrievedContext(BaseModel):
    relevant_tables: List[Table]
    relevant_udfs: List[UDF]


class SQLGenerationResult(BaseModel):
    sql: str
    reasoning_steps: List[str] = Field(default_factory=list)
    tables_used: List[str] = Field(default_factory=list)
    udfs_used: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    severity: str  # ERROR, WARNING, INFO
    message: str


class ValidationReport(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue] = Field(default_factory=list)