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

from lambdas.approve_reject.handler import handler


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
            TableName="Budgets",
            KeySchema=[
                {"AttributeName": "department", "KeyType": "HASH"},
                {"AttributeName": "category", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "department", "AttributeType": "S"},
                {"AttributeName": "category", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        client.create_table(
            TableName="AuditLog",
            KeySchema=[{"AttributeName": "audit_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "audit_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        client.create_table(
            TableName="Users",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield

def seed_request(status="submitted", department="Engineering", category="Travel", amount=500.0):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("ExpenseRequests")
    table.put_item(Item={
        "request_id": "r1",
        "employee_id": "e1",
        "department": department,
        "category": category,
        "amount": Decimal(str(amount)),
        "description": "Conference trip",
        "status": status,
        "date_submitted": "2026-08-01T00:00:00+00:00",
        "date_decided": None,
        "approver_id": None,
    })

def seed_budget(department="Engineering", category="Travel", allocated=1000.0, spent=0.0):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("Budgets")
    table.put_item(Item={
        "department": department,
        "category": category,
        "allocated_amount": Decimal(str(allocated)),
        "spent_amount": Decimal(str(spent)),
        "fiscal_period": "2026-Q3",
    })

def seed_approver(user_id="appr1"):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("Users")
    table.put_item(Item={
        "user_id": user_id, "name": "Approver", "email": "appr@example.com",
        "department": "Engineering", "role": "approver",
    })

def make_event(request_id: str, approver_id: str, decision: str):
    return {
        "pathParameters": {"request_id": request_id},
        "body": json.dumps({"approver_id": approver_id, "decision": decision}),
    }

def test_approve_success(dynamodb_tables):
    seed_request()
    seed_budget()
    seed_approver()

    response = handler(make_event("r1", "appr1", "approve"), None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "approved"
    assert body["approver_id"] == "appr1"

def test_approve_deducts_budget(dynamodb_tables):
    seed_request(amount = 300.0)
    seed_budget(allocated=1000.0, spent=200.0)
    seed_approver()

    handler(make_event("r1", "appr1", "approve"), None)

    budget_table = boto3.resource("dynamodb", region_name="us-east-1").Table("Budgets")
    item = budget_table.get_item(Key={"department": "Engineering", "category": "Travel"})["Item"]
    assert item["spent_amount"] == Decimal("500.0")

def test_approve_writes_audit_log(dynamodb_tables):
    seed_request()
    seed_budget()
    seed_approver()

    handler(make_event("r1", "appr1", "approve"), None)

    audit_table = boto3.resource("dynamodb", region_name="us-east-1").Table("AuditLog")
    items = audit_table.scan()["Items"]
    assert any(item["request_id"] == "r1" and item["action"] == "approved" for item in items)

def test_reject_success(dynamodb_tables):
    seed_request()
    seed_approver()

    response = handler(make_event("r1", "appr1", "reject"), None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["status"] == "rejected"

def test_reject_does_not_touch_budget(dynamodb_tables):
    seed_request()
    seed_budget(spent=0.0)
    seed_approver()

    handler(make_event("r1", "appr1", "reject"), None)

    budget_table = boto3.resource("dynamodb", region_name="us-east-1").Table("Budgets")
    item = budget_table.get_item(Key={"department": "Engineering", "category": "Travel"})["Item"]
    assert item["spent_amount"] == Decimal("0.0")

def test_approve_insufficient_budget_returns_400(dynamodb_tables):
    seed_request(amount=900.0)
    seed_budget(allocated=1000.0, spent=800.0) # only 200.0 remaining
    seed_approver()

    response = handler(make_event("r1", "appr1", "approve"), None)

    assert response["statusCode"] == 400

def test_approve_missing_budget_returns_404(dynamodb_tables):
    seed_request()
    seed_approver()
    # no budget seeded

    response = handler(make_event("r1", "appr1", "approve"), None)

    assert response["statusCode"] == 404


def test_unknown_decision_returns_400(dynamodb_tables):
    seed_request()
    seed_approver()

    response = handler(make_event("r1", "appr1", "maybe"), None)

    assert response["statusCode"] == 400


def test_request_not_found_returns_404(dynamodb_tables):
    response = handler(make_event("nonexistent", "appr1", "approve"), None)

    assert response["statusCode"] == 404


def test_cannot_approve_already_approved_request(dynamodb_tables):
    seed_request(status="approved")
    seed_budget()
    seed_approver()

    response = handler(make_event("r1", "appr1", "approve"), None)

    assert response["statusCode"] == 400