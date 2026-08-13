import os

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")

import boto3
import pytest
from moto import mock_aws

from auth import verify_role, UnauthorizedError


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

def seed_users(user_id="u1", role="approver"):
    table = boto3.resource("dynamodb", region_name="us-east-1").Table("Users")
    table.put_item(Item={
        "user_id": user_id,
        "name": "Test User",
        "email": "test@example.com",
        "role": role,
    })

def test_verify_role_success(dynamodb_tables):
    seed_users(user_id="u1", role="approver")

    result = verify_role("u1", "approver")

    assert result["user_id"] == "u1"
    assert result["role"] == "approver"

def test_verify_wrong_role_raises(dynamodb_tables):
    seed_users(user_id="u1", role="employee")

    with pytest.raises(UnauthorizedError):
        verify_role("u1", "approver")

def test_verify_role_missing_user_raises(dynamodb_tables):
    with pytest.raises(UnauthorizedError):
        verify_role("nonexistent", "approver")