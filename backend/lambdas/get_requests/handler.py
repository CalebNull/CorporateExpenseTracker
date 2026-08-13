import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
requests_table = dynamodb.Table("ExpenseRequests")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def handler(event, context):
    path_params = event.get("pathParameters") or {}
    request_id = path_params.get("request_id")

    if request_id:
        item = requests_table.get_item(Key={"request_id": request_id}).get("Item")
        if item is None:
            return {"statusCode": 404, "body": json.dumps({"error": "Request not found"})}
        return {"statusCode": 200, "body": json.dumps(item, cls=DecimalEncoder)}

    queryParams = event.get("queryStringParameters") or {}

    if "employee_id" in queryParams:
        response = requests_table.query(
            IndexName = "employee_id-index",
            KeyConditionExpression=Key("employee_id").eq(queryParams["employee_id"]),
        )
    elif "status" in queryParams:
        response = requests_table.query(
            IndexName = "status-index",
            KeyConditionExpression=Key("status").eq(queryParams["status"]),
        )
    elif "department" in queryParams:
        response = requests_table.query(
            IndexName = "department-index",
            KeyConditionExpression=Key("department").eq(queryParams["department"]),
        )
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Provide request_id path parameter, or employee_id/status/department query parameter"}),
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response.get("Items", []), cls=DecimalEncoder),
    }