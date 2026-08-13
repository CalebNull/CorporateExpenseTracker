import json
import os

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")

import boto3
import pytest
from moto import mock_aws

from lambdas.get_audit_trail.handler import handler


@pytest.fixture
def dynamodb_tables():
    with mock_aws():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName="AuditLog",
            KeySchema=[{"AttributeName": "audit_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "audit_id", "AttributeType": "S"},
                {"AttributeName": "request_id", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "request_id-index",
                    "KeySchema": [{"AttributeName": "request_id", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield

def seed_audit_entry(audit_id, request_id, action, timestamp):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("AuditLog")
    table.put_item(Item={
        "audit_id": audit_id,
        "request_id": request_id,
        "action": action,
        "performed_by": "u1",
        "details": f"Request {action}",
        "timestamp": timestamp,
    })

def make_event(request_id=None):
    return {
        "pathParameters": {"request_id": request_id} if request_id else None,
    }

def test_get_audit_trail_success(dynamodb_tables):
    seed_audit_entry("a1", "r1", "submitted", "2026-08-01T00:00:00+00:00")
    seed_audit_entry("a2", "r1", "approved", "2026-08-02T00:00:00+00:00")

    response = handler(make_event(request_id="r1"), None)

    assert response["statusCode"] == 200
    items = json.loads(response["body"])
    assert len(items) == 2

def test_get_audit_trail_only_returns_matching_request(dynamodb_tables):
    seed_audit_entry("a1", "r1", "submitted", "2026-08-01T00:00:00+00:00")
    seed_audit_entry("a2", "r2", "submitted", "2026-08-01T00:00:00+00:00")

    response = handler(make_event("r1"), None)

    items = json.loads(response["body"])
    assert len(items) == 1
    assert items[0]["request_id"] == "r1"

def test_get_audit_trail_sorted_chronologically(dynamodb_tables):
    seed_audit_entry("a1", "r1", "approved", "2026-08-02T00:00:00+00:00")
    seed_audit_entry("a2", "r1", "submitted", "2026-08-01T00:00:00+00:00")
    seed_audit_entry("a3", "r1", "paid", "2026-08-03T00:00:00+00:00")

    response = handler(make_event("r1"), None)

    items = json.loads(response["body"])
    actions = [item["action"] for item in items]
    assert actions == ["submitted", "approved", "paid"]


def test_get_audit_trail_empty_when_no_entries(dynamodb_tables):
    response = handler(make_event("r1"), None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == []


def test_get_audit_trail_missing_request_id_returns_400(dynamodb_tables):
    response = handler(make_event(), None)

    assert response["statusCode"] == 400