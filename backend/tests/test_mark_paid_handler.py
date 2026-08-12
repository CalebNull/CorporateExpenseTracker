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

from lambdas.mark_paid.handler import handler

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

def seed_request(status="approved", amount=500.0):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("ExpenseRequests")
    table.put_item(Item={
        "request_id": "r1",
        "employee_id": "emp1",
        "department": "Engineering",
        "category": "Travel",
        "amount": Decimal(str(amount)),
        "description": "Conference trip",
        "status": status,
        "date_submitted": "2026-08-01T00:00:00+00:00",
        "date_decided": "2026-08-02T00:00:00+00:00",
        "approver_id": "appr1",
    })

def make_event(request_id: str, finance_user_id: str):
    return {
        "pathParameters": {"request_id": request_id},
        "body": json.dumps({"finance_user_id": finance_user_id}),
    }

def test_mark_paid_success(dynamodb_tables):
    seed_request(status="approved")

    response = handler(make_event("r1", "fin1"), None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["status"] == "paid"

def test_mark_paid_writes_audit_log(dynamodb_tables):
    seed_request(status="approved")

    handler(make_event("r1", "fin1"), None)

    audit_table = boto3.resource("dynamodb", region_name="us-east-1").Table("AuditLog")
    items = audit_table.scan()["Items"]
    assert any(item["request_id"] == "r1" and item["action"] == "paid" for item in items)

def test_mark_paid_updates_dynamodb(dynamodb_tables):
    seed_request(status="approved")

    handler(make_event("r1", "fin1"), None)

    table = boto3.resource("dynamodb", region_name="us-east-1").Table("ExpenseRequests")
    item = table.get_item(Key={"request_id": "r1"})["Item"]
    assert item["status"] == "paid"


def test_mark_paid_rejects_submitted_request(dynamodb_tables):
    seed_request(status="submitted")

    response = handler(make_event("r1", "fin1"), None)

    assert response["statusCode"] == 400


def test_mark_paid_rejects_already_paid_request(dynamodb_tables):
    seed_request(status="paid")

    response = handler(make_event("r1", "fin1"), None)

    assert response["statusCode"] == 400


def test_mark_paid_request_not_found(dynamodb_tables):
    response = handler(make_event("nonexistent", "fin1"), None)

    assert response["statusCode"] == 404