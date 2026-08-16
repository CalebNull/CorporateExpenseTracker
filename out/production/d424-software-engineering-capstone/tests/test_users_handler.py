import json
import os

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")

import boto3
import pytest
from moto import mock_aws

from lambdas.users.handler import handler


@pytest.fixture
def dynamodb_tables():
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName="Users",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield

def seed_user(user_id="u1", name="Caleb", email="caleb@example.com", department="Engineering", role="employee"):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("Users")
    table.put_item(Item={
        "user_id": user_id,
        "name": name,
        "email": email,
        "department": department,
        "role": role,
    })

def make_get_event(user_id=None):
    return {
        "httpMethod": "GET",
        "pathParameters": {"user_id": user_id} if user_id else None,
    }

def make_post_event(body: dict):
    return {"httpMethod": "POST", "body": json.dumps(body)}

def test_get_user_success(dynamodb_tables):
    seed_user()

    response = handler(make_get_event("u1"), None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["user_id"] == "u1"
    assert body["name"] == "Caleb"

def test_get_user_missing_id_returns_400(dynamodb_tables):
    response = handler(make_get_event(), None)

    assert response["statusCode"] == 400

def test_get_user_not_found_returns_404(dynamodb_tables):
    response = handler(make_get_event("nonexistent"), None)

    assert response["statusCode"] == 404

def test_post_creates_employee(dynamodb_tables):
    response = handler(make_post_event({
        "role": "employee",
        "name": "Jaimie",
        "email": "jaimie@example.com",
        "department": "Sales",
    }), None)

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["role"] == "employee"
    assert body["name"] == "Jaimie"
    assert "user_id" in body

def test_post_creates_approver(dynamodb_tables):
    response = handler(make_post_event({
        "role": "approver",
        "name": "Robin",
        "email": "robin@example.com",
        "department": "Finance",
    }), None)

    assert response["statusCode"] == 201
    assert json.loads(response["body"])["role"] == "approver"

def test_post_persists_to_dynamodb(dynamodb_tables):
    response = handler(make_post_event({
        "role": "finance",
        "name": "Alex",
        "email": "alex@example.com",
        "department": "Finance",
    }), None)

    user_id = json.loads(response["body"])["user_id"]

    table = boto3.resource("dynamodb", region_name="us-east-1").Table("Users")
    item = table.get_item(Key={"user_id": user_id}).get("Item")
    assert item is not None
    assert item["name"] == "Alex"

def test_post_rejects_invalid_role(dynamodb_tables):
    response = handler(make_post_event({
        "role": "admin", # invalid role
        "name": "Robin",
        "email": "robin@example.com",
        "department": "Finance",
    }), None)

    assert response["statusCode"] == 400

def test_post_rejects_missing_role(dynamodb_tables):
    response = handler(make_post_event({
        "role": "employee",
        "name": "Jaimie",
        # missing role
        "department": "Sales",
    }), None)

    assert response["statusCode"] == 400

def test_unsupported_method_retturns_405(dynamodb_tables):
    response = handler({"httpMethod": "DELETE"}, None)

    assert response["statusCode"] == 405