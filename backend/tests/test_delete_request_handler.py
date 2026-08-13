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

from lambdas.delete_request.handler import handler


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
        client.create_table(
            TableName="Users",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


def seed_request(request_id="r1", employee_id="emp1", status="submitted", amount=500.0):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("ExpenseRequests")
    table.put_item(Item={
        "request_id": request_id,
        "employee_id": employee_id,
        "department": "Engineering",
        "category": "Travel",
        "amount": Decimal(str(amount)),
        "description": "Conference trip",
        "status": status,
        "date_submitted": "2026-08-01T00:00:00+00:00",
        "date_decided": None,
        "approver_id": None,
    })


def seed_user(user_id="emp1", role="employee"):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("Users")
    table.put_item(Item={
        "user_id": user_id, "name": "Test User", "email": "test@example.com",
        "department": "Engineering", "role": role,
    })


def make_event(request_id, employee_id):
    return {
        "pathParameters": {"request_id": request_id},
        "body": json.dumps({"employee_id": employee_id}),
    }


def test_delete_success(dynamodb_tables):
    seed_request()
    seed_user()

    response = handler(make_event("r1", "emp1"), None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["deleted"] is True


def test_delete_removes_from_dynamodb(dynamodb_tables):
    seed_request()
    seed_user()

    handler(make_event("r1", "emp1"), None)

    table = boto3.resource("dynamodb", region_name="us-east-1").Table("ExpenseRequests")
    assert table.get_item(Key={"request_id": "r1"}).get("Item") is None


def test_delete_writes_audit_log(dynamodb_tables):
    seed_request()
    seed_user()

    handler(make_event("r1", "emp1"), None)

    audit_table = boto3.resource("dynamodb", region_name="us-east-1").Table("AuditLog")
    items = audit_table.scan()["Items"]
    assert any(item["request_id"] == "r1" and item["action"] == "deleted" for item in items)


def test_delete_rejects_non_owner(dynamodb_tables):
    seed_request(employee_id="emp1")
    seed_user(user_id="emp2", role="employee")

    response = handler(make_event("r1", "emp2"), None)

    assert response["statusCode"] == 403


def test_delete_rejects_non_employee_role(dynamodb_tables):
    seed_request(employee_id="appr1")
    seed_user(user_id="appr1", role="approver")

    response = handler(make_event("r1", "appr1"), None)

    assert response["statusCode"] == 403


def test_delete_rejects_non_submitted_request(dynamodb_tables):
    seed_request(status="approved")
    seed_user()

    response = handler(make_event("r1", "emp1"), None)

    assert response["statusCode"] == 400


def test_delete_request_not_found(dynamodb_tables):
    response = handler(make_event("nonexistent", "emp1"), None)

    assert response["statusCode"] == 404


def test_delete_missing_employee_id_returns_400(dynamodb_tables):
    event = {"pathParameters": {"request_id": "r1"}, "body": json.dumps({})}

    response = handler(event, None)

    assert response["statusCode"] == 400