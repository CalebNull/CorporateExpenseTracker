import json
import uuid
from decimal import Decimal

import boto3

from models import Approver, Budget
from models.audit_log import AuditLogEntry
from models.expense_request import ExpenseRequest
from auth import *

dynamodb = boto3.resource("dynamodb")
requests_table = dynamodb.Table("ExpenseRequests")
budgets_table = dynamodb.Table("Budgets")
audit_table = dynamodb.Table("AuditLog")

def handler(event, context):
    request_id = event["pathParameters"]["request_id"]
    body = json.loads(event["body"])
    approver_id = body["approver_id"]
    decision = body["decision"] # 'approve' or 'reject'

    item = requests_table.get_item(Key={"request_id": request_id}).get("Item")
    if item is None:
        return {"statusCode": 404, "body": json.dumps({"error": "Request not found"})}

    request = ExpenseRequest.from_item(item)
    try:
        verify_role(approver_id, "approver")
    except UnauthorizedError as e:
        return {"statusCode": 403, "body": json.dumps({"error": str(e)})}
    approver = Approver(approver_id, "", "", request.department)

    try:
        if decision == "approve":
            budget_item = budgets_table.get_item(Key={"department": request.department, "category": request.category}).get("Item")
            if budget_item is None:
                return {"statusCode": 404, "body": json.dumps({"error": "Budget not found"})}

            budget = Budget(
                budget_item["department"],
                budget_item["category"],
                float(budget_item["allocated_amount"]),
                budget_item["fiscal_period"],
                float(budget_item["spent_amount"]),
            )

            approver.process(request, "approve")
            budget.deduct(request.amount)

            budgets_table.update_item(
                Key={"department": budget.department, "category": budget.category},
                UpdateExpression="SET spent_amount = :s",
                ExpressionAttributeValues={":s": Decimal(str(budget.spent_amount))},
            )
        elif decision == "reject":
            approver.process(request, "reject")
        else:
            return {"statusCode": 400, "body": json.dumps({"error": f"Unknown decision: {decision}"})}
    except ValueError as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}

    requests_table.update_item(
        Key={"request_id": request_id},
        UpdateExpression= "SET #s = :status, approver_id = :approver_id, date_decided= :date_decided",
        ExpressionAttributeNames = {"#s": "status"},
        ExpressionAttributeValues = {
            ":status": request.status,
            ":approver_id": request.approver_id,
            ":date_decided": request.date_decided,
        }
    )

    audit_entry = AuditLogEntry(
        audit_id=str(uuid.uuid4()),
        request_id=request.request_id,
        action=request.status,
        performed_by=approver_id,
        details=f"Request {request.status} by {approver_id}",
    )
    audit_table.put_item(Item=audit_entry.record())

    return {
        "statusCode": 200,
        "body": json.dumps({
            "request_id": request.request_id,
            "status": request.status,
            "approver_id": request.approver_id,
        })
    }