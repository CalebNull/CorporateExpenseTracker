import json
import uuid

import boto3

from models.user import *

dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

ROLE_CLASSES = {
    "employee": Employee,
    "approver": Approver,
    "finance": FinanceStaff,
}

def handler(event, context):
    method = event.get("httpMethod")

    if method == "GET":
        return _handle_get(event)
    elif method == "POST":
        return _handle_post(event)

    return {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}

def _handle_get(event):
    path_params = event.get("pathParameters") or {}
    user_id = path_params.get("user_id")
    if not user_id:
        return {"statusCode": 400, "body": json.dumps({"error": "user_id is required"})}

    item = users_table.get_item(Key={"user_id": user_id}).get("Item")
    if item is None:
        return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}

    return {"statusCode": 200, "body": json.dumps(item)}

def _handle_post(event):
    body = json.loads(event["body"])

    try:
        role = body["role"]
        user_class = ROLE_CLASSES[role]
        user = user_class(
            user_id=str(uuid.uuid4()),
            name=body["name"],
            email=body["email"],
            department=body["department"],
        )
    except KeyError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Missing or invalid field: {e}"})
        }

    profile = user.get_profile()
    profile["role"] = role

    users_table.put_item(Item=profile)

    return {"statusCode": 201, "body": json.dumps(profile)}