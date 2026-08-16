import json
import os

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")

import boto3
import pytest
from moto import mock_aws

from lambdas.submit_requests.handler import *

@pytest.fixture
def dynamodb_tables():
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName="ExpenseRequests",
            KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "request_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        client.create_table(
            TableName="AuditLog",
            KeySchema=[{"AttributeName": "audit_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "audit_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield

def make_event(body: dict):
    return {"body": json.dumps(body)}

def test_submit_request_success(dynamodb_tables):
    event = make_event({
        "employee_id": "emp1",
        "department": "Engineering",
        "category": "Travel",
        "amount": 1000.0,
        "description": "Conference trip",
    })
    response = handler(event, None)

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["status"] == "submitted"
    assert "request_id" in body

def test_submit_request_writes_to_dynamodb(dynamodb_tables):
    event = make_event({
        "employee_id": "emp1",
        "department": "Engineering",
        "category": "Travel",
        "amount": 1000.0,
        "description": "Conference trip",
    })

    response = handler(event, None)
    request_id = json.loads(response["body"])["request_id"]

    table = boto3.resource("dynamodb", region_name="us-east-1").Table("ExpenseRequests")
    item = table.get_item(Key={"request_id": request_id})["Item"]
    assert item["status"] == "submitted"
    assert item["employee_id"] == "emp1"

def test_submitted_request_writes_audit_log(dynamodb_tables):
    event = make_event({
        "employee_id": "emp1",
        "department": "Engineering",
        "category": "Travel",
        "amount": 1000.0,
        "description": "Conference trip",
    })

    response = handler(event, None)
    request_id = json.loads(response["body"])["request_id"]

    audit_table = boto3.resource("dynamodb", region_name="us-east-1").Table("AuditLog")
    items = audit_table.scan()["Items"]
    assert any(
        item["request_id"] == request_id and item["action"] == "submitted"
        for item in items
    )

def test_submitted_request_rejects_invalid_amount(dynamodb_tables):
    event = make_event({
        "employee_id": "emp1",
        "department": "Engineering",
        "category": "Travel",
        "amount": -250.0,
        "description": "Conference trip",
    })

    assert handler(event, None)["statusCode"] == 400

def test_submite_request_rejects_missing_field(dynamodb_tables):
    event = make_event({
        "employee_id": "emp1",
        "department": "Engineering",
        "amount": 100.0,
    })

    assert handler(event, None)["statusCode"] == 400
























