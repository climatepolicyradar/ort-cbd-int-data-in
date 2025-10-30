from datetime import datetime
from typing import Dict

from pydantic import BaseModel

LanguageId = str
WithMultilingualText = Dict[LanguageId, str]


class WithIdentifier(BaseModel):
    identifier: str


class WithEnglishText(BaseModel):
    en: str


class Metadata(BaseModel):
    government: str
    userID: str
    schema: str


class Header(WithIdentifier):
    schema: str
    languages: list[str]


class GlobalTargetAlignment(WithIdentifier):
    degreeOfAlignment: WithIdentifier


class OtherNationalIndicator(WithIdentifier):
    value: WithMultilingualText


class AdditionalImplementation(WithIdentifier):
    customValue: str


class User(BaseModel):
    userID: int
    firstName: str
    lastName: str
    email: str


class Body(BaseModel):
    header: Header
    government: WithIdentifier
    title: WithMultilingualText
    description: WithMultilingualText
    sequence: int
    globalGoalAlignment: list[WithIdentifier]
    globalTargetAlignment: list[GlobalTargetAlignment]
    mainPolicyOfMeasureOrActionInfo: WithMultilingualText
    headlineIndicators: list[WithIdentifier]
    binaryIndicators: list[WithIdentifier]
    complementaryIndicators: list[WithIdentifier]
    otherNationalIndicators: list[OtherNationalIndicator]
    nonStateActorCommitmentInfo: WithMultilingualText
    hasNonStateActors: bool
    additionalImplementation: AdditionalImplementation
    additionalImplementationInfo: WithMultilingualText


class OrtCbdIntModel(BaseModel):
    metadata: Metadata
    body: Body
    Realm: str
    identifier: str
    documentID: int
    createdOn: datetime
    createdBy: User
    updatedOn: datetime
    updatedBy: User
    submittedOn: datetime
    submittedBy: User
    type: str
    owner: str
    revision: int
    size: int
    charset: str
    title: WithMultilingualText
    summary: WithMultilingualText
    realm: str
    latestRevision: int
    isRequest: bool
