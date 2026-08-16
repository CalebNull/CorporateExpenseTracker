import json

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
audit_table = dynamodb.Table('AuditLog')

def handler(event, context):
    path_params = event.get("pathParameters") or {}
    request_id = path_params.get("request_id")

    if not request_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing request id"})
        }

    response = audit_table.query(
        IndexName="request_id-index",
        KeyConditionExpression=Key("request_id").eq(request_id),
    )

    items = response.get("Items", [])
    items.sort(key=lambda item: item.get("timestamp", ""))

    return {
        "statusCode": 200,
        "body": json.dumps(items)
    }