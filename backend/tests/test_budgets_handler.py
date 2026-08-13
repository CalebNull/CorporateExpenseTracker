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

from lambdas.budgets.handler import handler


@pytest.fixture
def dynamodb_tables():
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName="Budgets",
            KeySchema=[
                {"AttributeName": "department", "KeyType": "HASH"},
                {"AttributeName": "category", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "department", "AttributeType": "S"},
                {"AttributeName": "category", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield


def seed_budget(department="Engineering", category="Travel", allocated=1000.0, spent=200.0, fiscal_period="2026-Q3"):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("Budgets")
    table.put_item(Item={
        "department": department,
        "category": category,
        "allocated_amount": Decimal(str(allocated)),
        "spent_amount": Decimal(str(spent)),
        "fiscal_period": fiscal_period,
    })


def make_get_event(department=None, category=None, query_department=None):
    path_params = None
    if department and category:
        path_params = {"department": department, "category": category}
    return {
        "httpMethod": "GET",
        "pathParameters": path_params,
        "queryStringParameters": {"department": query_department} if query_department else None,
    }


def make_put_event(department, category, allocated_amount, fiscal_period):
    return {
        "httpMethod": "PUT",
        "pathParameters": {"department": department, "category": category},
        "body": json.dumps({"allocated_amount": allocated_amount, "fiscal_period": fiscal_period}),
    }


def test_get_single_budget_success(dynamodb_tables):
    seed_budget()

    response = handler(make_get_event(department="Engineering", category="Travel"), None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["allocated_amount"] == 1000.0
    assert body["spent_amount"] == 200.0


def test_get_single_budget_not_found(dynamodb_tables):
    response = handler(make_get_event(department="Engineering", category="Travel"), None)

    assert response["statusCode"] == 404


def test_get_list_by_department(dynamodb_tables):
    seed_budget(department="Engineering", category="Travel")
    seed_budget(department="Engineering", category="Supplies")
    seed_budget(department="Sales", category="Travel")

    response = handler(make_get_event(query_department="Engineering"), None)

    assert response["statusCode"] == 200
    items = json.loads(response["body"])
    assert len(items) == 2
    assert {item["category"] for item in items} == {"Travel", "Supplies"}


def test_get_list_missing_department_returns_400(dynamodb_tables):
    response = handler(make_get_event(), None)

    assert response["statusCode"] == 400


def test_put_creates_new_budget(dynamodb_tables):
    response = handler(make_put_event("Engineering", "Travel", 1500.0, "2026-Q4"), None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["allocated_amount"] == 1500.0
    assert body["spent_amount"] == 0.0


def test_put_updates_existing_budget_preserves_spent_amount(dynamodb_tables):
    seed_budget(department="Engineering", category="Travel", allocated=1000.0, spent=400.0)

    response = handler(make_put_event("Engineering", "Travel", 2000.0, "2026-Q4"), None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["allocated_amount"] == 2000.0
    assert body["spent_amount"] == 400.0


def test_put_missing_field_returns_400(dynamodb_tables):
    event = {
        "httpMethod": "PUT",
        "pathParameters": {"department": "Engineering", "category": "Travel"},
        "body": json.dumps({"fiscal_period": "2026-Q4"}),  # missing allocated_amount
    }

    response = handler(event, None)

    assert response["statusCode"] == 400


def test_unsupported_method_returns_405(dynamodb_tables):
    response = handler({"httpMethod": "POST"}, None)

    assert response["statusCode"] == 405