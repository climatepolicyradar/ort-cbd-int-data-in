from typing import Annotated, Final, Literal, Never, Union

from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    source: Never


class IdentifiedDocument(BaseModel):
    state = Final[Literal["identified"]]
    id: str


class TransformedDocument(BaseModel):
    state = Final[Literal["transformed"]]
    id: str
    title: str
    labels: list[str]


class LinkedDocument(BaseModel):
    state = Final[Literal["linked"]]
    id: str
    documents: list["LinkedDocument"]
    title: str
    labels: list[str]


def identify_document(source_document: SourceDocument) -> IdentifiedDocument: ...


def transform_document(
    identified_document: IdentifiedDocument,
) -> TransformedDocument: ...


def link_document(transformed_document: TransformedDocument) -> LinkedDocument: ...


Document = Annotated[
    Union[IdentifiedDocument, TransformedDocument, LinkedDocument],
    Field(discriminator="state"),
]
