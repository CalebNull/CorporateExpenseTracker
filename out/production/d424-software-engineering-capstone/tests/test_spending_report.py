import json
import os
from decimal import Decimal

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")

import boto3
import pytest
from moto import mock_aws

from lambdas.spending_report.handler import handler


@pytest.fixture
def dynamodb_tables():
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName="ExpenseRequests",
            KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "request_id", "AttributeType": "S"},
                {"AttributeName": "department", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "department-index",
                    "KeySchema": [{"AttributeName": "department", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


def seed_request(request_id, department="Engineering", category="Travel",
                 employee_id="emp1", amount=500.0, status="approved",
                 date_submitted="2026-08-05T00:00:00+00:00"):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("ExpenseRequests")
    table.put_item(Item={
        "request_id": request_id,
        "employee_id": employee_id,
        "department": department,
        "category": category,
        "amount": Decimal(str(amount)),
        "description": "Conference trip",
        "status": status,
        "date_submitted": date_submitted,
        "date_decided": None,
        "approver_id": None,
    })


def make_event(department=None, start=None, end=None):
    query_params = {}
    if department:
        query_params["department"] = department
    if start:
        query_params["start"] = start
    if end:
        query_params["end"] = end
    return {"queryStringParameters": query_params or None}


def test_report_returns_title_and_columns(dynamodb_tables):
    seed_request("r1")

    response = handler(make_event("Engineering", "2026-08-01", "2026-08-31"), None)

    assert response["statusCode"] == 200
    report = json.loads(response["body"])
    assert "Engineering" in report["title"]
    assert report["columns"] == ["date", "employee_id", "category", "amount", "status"]


def test_report_includes_matching_rows(dynamodb_tables):
    seed_request("r1", amount=500.0)
    seed_request("r2", amount=300.0)

    response = handler(make_event("Engineering", "2026-08-01", "2026-08-31"), None)

    report = json.loads(response["body"])
    assert len(report["rows"]) == 2
    amounts = {row["amount"] for row in report["rows"]}
    assert amounts == {500.0, 300.0}


def test_report_excludes_other_departments(dynamodb_tables):
    seed_request("r1", department="Engineering")
    seed_request("r2", department="Sales")

    response = handler(make_event("Engineering", "2026-08-01", "2026-08-31"), None)

    report = json.loads(response["body"])
    assert len(report["rows"]) == 1
    assert report["rows"][0]["date"] is not None


def test_report_excludes_dates_outside_range(dynamodb_tables):
    seed_request("r1", date_submitted="2026-07-15T00:00:00+00:00")  # before range
    seed_request("r2", date_submitted="2026-08-15T00:00:00+00:00")  # in range
    seed_request("r3", date_submitted="2026-09-15T00:00:00+00:00")  # after range

    response = handler(make_event("Engineering", "2026-08-01", "2026-08-31"), None)

    report = json.loads(response["body"])
    assert len(report["rows"]) == 1


def test_report_rows_sorted_chronologically(dynamodb_tables):
    seed_request("r1", date_submitted="2026-08-20T00:00:00+00:00")
    seed_request("r2", date_submitted="2026-08-05T00:00:00+00:00")
    seed_request("r3", date_submitted="2026-08-15T00:00:00+00:00")

    response = handler(make_event("Engineering", "2026-08-01", "2026-08-31"), None)

    report = json.loads(response["body"])
    dates = [row["date"] for row in report["rows"]]
    assert dates == sorted(dates)


def test_report_missing_params_returns_400(dynamodb_tables):
    response = handler(make_event("Engineering"), None)  # missing start/end

    assert response["statusCode"] == 400