from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CPRFamily(BaseModel):
    import_id: str
    title: str
    summary: str
    geographies: list[str]
    metadata: dict[str, list[str]]
    collections: list[str]
    category: str
    concepts: list[dict[str, Any]]
    last_modified: datetime


class CPRDocument(BaseModel):
    import_id: str
    family_import_id: str
    metadata: dict[str, list[str]]
    title: str
    source_url: str
    variant_name: str


class CPREvent(BaseModel):
    import_id: str
    family_import_id: str
    family_document_import_id: str
    event_title: str
    event_type_value: str
    date: str
    metadata: dict[str, list[str]]


class DBStateEntry(BaseModel):
    family: CPRFamily
    document: CPRDocument
    event: CPREvent
    collection: Any


class DBState(BaseModel):
    families: list[CPRFamily] = Field(default_factory=list)
    documents: list[CPRDocument] = Field(default_factory=list)
    events: list[CPREvent] = Field(default_factory=list)
    collections: list[Any] = Field(default_factory=list)
