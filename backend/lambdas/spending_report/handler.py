import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
requests_table = dynamodb.Table("ExpenseRequests")


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def handler(event, context):
    query_params = event.get("queryStringParameters") or {}
    department = query_params.get("department")
    start = query_params.get("start")
    end = query_params.get("end")

    if not department or not start or not end:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "department, start and end cannot be empty"}),
        }

    response = requests_table.query(
        IndexName="department-index",
        KeyConditionExpression=Key("department").eq(department),
    )

    items = [
        item for item in response.get("Items", [])
        if item.get("date_submitted") and start <= item["date_submitted"] <= end
    ]
    items.sort(key=lambda item: item["date_submitted"])

    rows = [
        {
            "date": item["date_submitted"],
            "employee_id": item["employee_id"],
            "category": item["category"],
            "amount": item["amount"],
            "status": item["status"],
        }
        for item in items
    ]

    report = {
        "title": f"Spending Report - {department} ({start} to {end})",
        "columns": ["date", "employee_id", "category", "amount", "status"],
        "rows": rows,
    }

    return {
        "statusCode": 200,
        "body": json.dumps(report, cls=DecimalEncoder),
    }