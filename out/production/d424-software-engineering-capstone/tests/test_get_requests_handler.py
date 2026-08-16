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

from lambdas.get_requests.handler import handler

@pytest.fixture
def dynamodb_tables():
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName="ExpenseRequests",
            KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "request_id", "AttributeType": "S"},
                {"AttributeName": "employee_id", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
                {"AttributeName": "department", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "employee_id-index",
                    "KeySchema": [{"AttributeName": "employee_id", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "status-index",
                    "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "department-index",
                    "KeySchema": [{"AttributeName": "department", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield

def seed_request(request_id, employee_id="emp1", department="Engineering", category="Travel",
                 amount=500.0, status="submitted"):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("ExpenseRequests")
    table.put_item(Item={
        "request_id": request_id,
        "employee_id": employee_id,
        "department": department,
        "category": category,
        "amount": Decimal(str(amount)),
        "description": "Conference trip",
        "status": status,
        "date_submitted": "2026-08-01T00:00:00+00:00",
        "date_decided": None,
        "approver_id": None,
    })


def make_event(request_id=None, query_params=None):
    return {
        "pathParameters": {"request_id": request_id} if request_id else None,
        "queryStringParameters": query_params,
    }

def test_get_single_request_success(dynamodb_tables):
    seed_request("r1")

    response = handler(make_event(request_id="r1"), None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["request_id"] == "r1"

def test_get_single_request_not_found(dynamodb_tables):
    response = handler(make_event(request_id="nonexistent"), None)

    assert response["statusCode"] == 404

def test_search_by_employee_id(dynamodb_tables):
    seed_request("r1", employee_id="emp1")
    seed_request("r2", employee_id="emp1")
    seed_request("r3", employee_id="emp3")

    response = handler(make_event(query_params={"employee_id": "emp1"}), None)

    assert response["statusCode"] == 200
    items = json.loads(response["body"])
    assert len(items) == 2
    assert {item["request_id"] for item in items} == {"r1", "r2"}

def test_search_by_status(dynamodb_tables):
    seed_request("r1", status="submitted")
    seed_request("r2", status="approved")
    seed_request("r3", status="submitted")

    response = handler(make_event(query_params={"status": "submitted"}), None)

    items = json.loads(response["body"])
    assert len(items) == 2
    assert {item["request_id"] for item in items} == {"r1", "r3"}

def test_search_by_department(dynamodb_tables):
    seed_request("r1", department="Engineering")
    seed_request("r2", department="Sales")
    seed_request("r3", department="Engineering")

    response = handler(make_event(query_params={"department": "Engineering"}), None)

    items = json.loads(response["body"])
    assert len(items) == 2
    assert {item["request_id"] for item in items} == {"r1", "r3"}

def test_missing_params_returns_400(dynamodb_tables):
    response = handler(make_event(), None)

    assert response["statusCode"] == 400