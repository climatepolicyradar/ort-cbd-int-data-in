import csv
from datetime import datetime
from io import StringIO
from pathlib import Path
import pycountry
import pytest
import requests

from prefect import flow, task
from prefect_aws import AwsCredentials, S3Bucket
from prefect.assets import materialize
from prefect.testing.utilities import prefect_test_harness

from .cpr_models import CPRDocument, CPREvent, CPRFamily, DBState, DBStateEntry
from .csv_api import OrtCbdIntCsv
import boto3


Path(".data_cache").mkdir(exist_ok=True)


@materialize("s3://cpr-cache/pipelines/ort-cbd-int-data-in/source-data.csv")
def extract_source_data():
    source_url = (
        "https://api.cbd.int/api/v2022/documents/schemas/nationalTarget7/download"
    )
    # This was taken from the POST request that the website makes
    source_query = {
        "query": {
            "df": "text_EN_txt",
            "fq": ["_state_s:public", "realm_ss:ort"],
            "q": "(schema_s : (nationalTarget7))",
            "sort": "updatedDate_dt desc",
            "fl": "id, recDate:updatedDate_dt, recCreationDate:createdDate_dt, identifier_s, uniqueIdentifier_s, url_ss, government_s, schema_s,schema_EN_s, government_EN_s, schemaSort_i, sort1_i, sort2_i, sort3_i, sort4_i, _revision_i,recCountryName:government_EN_t, recTitle:title_EN_t, recSummary:summary_t, recType:type_EN_t, recMeta1:meta1_EN_txt, recMeta2:meta2_EN_txt, recMeta3:meta3_EN_txt,recMeta4:meta4_EN_txt,recMeta5:meta5_EN_txt,globalTargetAlignment_ss,globalGoalOrTarget_s,globalGoalAlignment_ss,globalTargetAlignment_ss,globalGoalOrTarget_s,globalGoalAlignment_ss,globalTargetAlignment_ss,globalGoalOrTarget_s,globalGoalAlignment_ss",
            "wt": "json",
            "start": 0,
            "rows": 10000,
        },
        "fields": {
            "publishedOn": "Published on",
            "recordUrl": "url",
            "uniqueId": "Unique Id",
            "government": "Government",
            "title": "National target title",
            "description": "Description",
            "mainPolicyOfMeasureOrActionInfo": "Main policy measures",
            "globalGoalAlignmentIds": "Global Goals",
            "globalTargetAlignmentIds": "Global targets",
            "globalTargetAndDegreeOfAlignment": "Degree of Alignment by target",
            "degreeOfAlignmentInfo": "Aspects of the goal or target are covered",
            "gbfTargetConsideration": "Considerations for implementation from Section C",
            "implementingConsiderationsInfo": "Explain considerations",
            "headlineIndicators": "Headline indicators",
            "binaryIndicators": "Binary indicators",
            "componentIndicators": "Component indicators",
            "complementaryIndicators": "Complementary indicators",
            "otherNationalIndicators": "otherNationalIndicators",
            "nonStateActorCommitmentInfo": "Non-state commitments",
            "hasNonStateActors": "Overlaps or links",
            "nonStateActorsInfo": "Commitment(s) and actor(s)",
            "additionalImplementation": "Means of implementation",
            "additionalImplementationCustomValue": "Please explain (means of implementation)",
            "additionalImplementationInfo": "additionalExplanation",
            "additionalInformation": "Any other information",
        },
        "newRowForArrayValues": False,
    }

    response = requests.post(
        source_url,
        json=source_query,
        headers={
            "accept": "text/csv",
            "accept-encoding": "gzip, deflate, br, zstd",
            "content-type": "application/json",
            "realm": "ORT",
        },
    )
    response.raise_for_status()
    response.encoding = "utf-8-sig"

    source_data_path = Path(".data_cache/source-data.csv")
    with source_data_path.open("w", encoding="utf-8") as f:
        f.write(response.text)

    aws_credentials = AwsCredentials.load("aws-credentials-block-prod")
    s3_bucket = S3Bucket(bucket_name="cpr-cache", credentials=aws_credentials)
    s3_bucket.upload_from_path(
        source_data_path, to_path="pipelines/ort-cbd-int-data-in/source-data.csv"
    )

    return response.text


pycountry.countries.add_entry(
    alpha_2="EU",
    alpha_3="EUR",
    name="European Union",
    numeric="",
)


def get_geography(name: str):
    geography_name = None
    if name == "Netherlands (Kingdom of the)":
        geography_name = "Netherlands"
    elif name == "United Republic of Tanzania":
        geography_name = "Tanzania, United Republic of"
    elif name == "Iran (Islamic Republic of)":
        geography_name = "Iran, Islamic Republic of"
    elif name == "Bolivia (Plurinational State of)":
        geography_name = "Bolivia, Plurinational State of"
    elif name == "Venezuela (Bolivarian Republic of)":
        geography_name = "Venezuela, Bolivarian Republic of"
    elif name == "Democratic Republic of the Congo":
        geography_name = "Congo, The Democratic Republic of the"
    elif name == "Türkiye":
        geography_name = "Türkiye"
    elif name == "United Kingdom of Great Britain and Northern Ireland":
        geography_name = "United Kingdom"
    elif name == "Republic of Korea":
        geography_name = "Korea, Democratic People's Republic of"
    elif name == "Republic of Moldova":
        geography_name = "Moldova, Republic of"
    else:
        geography_name = name

    geography = pycountry.countries.get(name=geography_name)

    return geography


def get_latest_target_for_government(government: str):
    with open(".data_cache/source-data.csv", "r", encoding="utf-8") as f:
        source_data = f.read()
    reader = csv.DictReader(StringIO(source_data))
    models = []
    for row in reader:
        model = OrtCbdIntCsv(**row)
        if model.government != government:
            continue
        models.append(model)

    return max(models, key=lambda x: x.published_on)


@task()
def transform_governments(governments_subset: list[str] = []):
    with open(".data_cache/source-data.csv", "r", encoding="utf-8") as f:
        source_data = f.read()

    reader = csv.DictReader(StringIO(source_data))
    models = []
    for row in reader:
        model = OrtCbdIntCsv(**row)
        models.append(model)

    governments = governments_subset or list(set(model.government for model in models))

    db_state_entries = []
    for government in governments:
        geography = get_geography(government)

        family_import_id = f"UNCDB.family.{geography.alpha_3}.n0000"
        document_import_id = f"UNCDB.document.{geography.alpha_3}.n0000"
        event_import_id = f"UNCDB.event.{geography.alpha_3}.n0000"

        last_modified = (
            datetime.strptime(
                get_latest_target_for_government(government).published_on,
                "%d-%b-%Y %H:%M",
            )
            .date()
            .isoformat()
        )

        db_state_entry = DBStateEntry(
            family=CPRFamily(
                import_id=family_import_id,
                title=f"{government} National Targets. GBF-NT",
                summary=f"The CBD National Targets Submitted by {government}",
                geographies=[geography.alpha_3],
                metadata={
                    "external_id": [
                        f"https://ort.cbd.int/national-targets?recordTypes=nationalTarget7&countries={geography.alpha_2.lower()}"
                    ],
                    "author_type": ["Party"],
                    "author": [geography.name],
                },
                collections=[],
                category="UNFCCC",
                concepts=[],
                last_modified=last_modified,
            ),
            document=CPRDocument(
                import_id=document_import_id,
                family_import_id=family_import_id,
                metadata={
                    "role": ["MAIN"],
                    "type": ["National Target (NT)"],
                },
                title=f"{government} National Targets. GBF-NT",
                source_url=f"https://cdn.climatepolicyradar.org/pdfs/ort-cbd-int/{government}.pdf",
                variant_name=None,
            ),
            event=CPREvent(
                import_id=event_import_id,
                family_import_id=family_import_id,
                family_document_import_id=document_import_id,
                event_title="Submitted",
                event_type_value="Passed/Approved",
                date=last_modified,
                metadata={
                    "event_type": ["Passed/Approved"],
                    "datetime_event_name": ["Passed/Approved"],
                },
            ),
            collection=None,
        )
        db_state_entries.append(db_state_entry)
    return db_state_entries


@materialize("s3://cpr-cache/pipelines/ort-cbd-int-data-in/db-state.json")
def transform_db_state_entries(db_state_entries: list[DBStateEntry]):
    db_state = DBState(
        families=[entry.family for entry in db_state_entries],
        documents=[entry.document for entry in db_state_entries],
        events=[entry.event for entry in db_state_entries],
        collections=[],
    )

    db_state_path = Path(".data_cache/db-state.json")
    with db_state_path.open("w", encoding="utf-8") as f:
        f.write(db_state.model_dump_json())

    aws_credentials = AwsCredentials.load("aws-credentials-block-prod")
    s3_bucket = S3Bucket(bucket_name="cpr-cache", credentials=aws_credentials)
    s3_bucket.upload_from_path(
        db_state_path, to_path="pipelines/ort-cbd-int-data-in/db-state.json"
    )
    return db_state


@flow(log_prints=True)
def etl_pipeline(governments_subset: list[str] = []):
    extract_source_data()
    db_state_entries = transform_governments(governments_subset=governments_subset)
    db_state = transform_db_state_entries(db_state_entries)
    return db_state


@flow(log_prints=True)
def bulk_import():
    ssm_client = boto3.client("ssm", region_name="eu-west-1")
    email = ssm_client.get_parameter(
        Name="/Backend/API/SuperUser/Email", WithDecryption=True
    )["Parameter"]["Value"]
    password = ssm_client.get_parameter(
        Name="/Backend/API/SuperUser/Password", WithDecryption=True
    )["Parameter"]["Value"]

    token_response = requests.post(
        "https://admin.staging.climatepolicyradar.org/api/tokens",
        timeout=1,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": email,
            "password": password,
        },
    )
    token = token_response.json()["access_token"]

    bulk_import_response = requests.post(
        "https://admin.staging.climatepolicyradar.org/api/v1/bulk-import/UN.corpus.UNCBD.n0000",
        headers={"Authorization": f"Bearer {token}"},
        files={"data": open(".data_cache/db-state.json", "rb")},
        timeout=10,
    )

    bulk_import_response.raise_for_status()
    return bulk_import_response


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield


def test_etl_pipeline():
    etl_pipeline()
