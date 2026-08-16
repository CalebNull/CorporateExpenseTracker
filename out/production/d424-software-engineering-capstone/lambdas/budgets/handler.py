import json
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

from models.budget import Budget

dynamodb = boto3.resource("dynamodb")
budgets_table = dynamodb.Table("Budgets")


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def handler(event, context):
    method = event.get("httpMethod")

    if method == "GET":
        return _handle_get(event)
    elif method == "PUT":
        return _handle_put(event)

    return {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}

def _handle_get(event):
    path_params = event.get("pathParameters") or {}
    department = path_params.get("department")
    category = path_params.get("category")

    if department and category:
        item = budgets_table.get_item(Key={"department": department, "category": category}).get("Item")

        if item is None:
            return {"statusCode": 404, "body": json.dumps({"error": "Budget not found"})}
        return {"statusCode": 200, "body": json.dumps(item, cls=DecimalEncoder)}

    query_params = event.get("queryStringParameters") or {}
    department = query_params.get("department")
    if not department:
        return {"statusCode": 400, "body": json.dumps({"error": "Department required"})}

    response = budgets_table.query(
        KeyConditionExpression=Key("department").eq(department),
    )
    return {"statusCode": 200, "body": json.dumps(response.get("Items", []), cls=DecimalEncoder)}

def _handle_put(event):
    path_params = event.get("pathParameters") or {}
    department = path_params.get("department")
    category = path_params.get("category")
    body = json.loads(event["body"])

    try:
        allocated_amount = float(body["allocated_amount"])
        fiscal_period = body["fiscal_period"]
    except (KeyError, ValueError) as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}

    existing = budgets_table.get_item(Key={"department": department, "category": category}).get("Item")
    spent_amount = float(existing["spent_amount"]) if existing else 0

    budget = Budget(department, category, allocated_amount, fiscal_period, spent_amount)

    budgets_table.put_item(Item={
        "department": budget.department,
        "category": budget.category,
        "allocated_amount": Decimal(str(budget.allocated_amount)),
        "spent_amount": Decimal(str(budget.spent_amount)),
        "fiscal_period": budget.fiscal_period,
    })

    return {
        "statusCode": 200,
        "body": json.dumps({
            "department": budget.department,
            "category": budget.category,
            "allocated_amount": budget.allocated_amount,
            "spent_amount": budget.spent_amount,
            "fiscal_period": budget.fiscal_period,
        })
    }