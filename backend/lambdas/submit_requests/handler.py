import json
import uuid
from decimal import Decimal

import boto3

from models.audit_log import *
from models.expense_request import *

dynamodb = boto3.resource("dynamodb")
requests_table = dynamodb.Table("ExpenseRequests")
audit_table = dynamodb.Table("AuditLog")

def handler(event, context):
    body = json.loads(event["body"])

    try:
        request = ExpenseRequest(
            request_id=str(uuid.uuid4()),
            employee_id=body["employee_id"],
            department=body["department"],
            category=body["category"],
            amount=float(body["amount"]),
            description=body.get("description", ""),
        )
        request.submit()
    except (ValueError, KeyError) as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)}),
        }

    requests_table.put_item(Item={
        "request_id": request.request_id,
        "employee_id": request.employee_id,
        "department": request.department,
        "category": request.category,
        "amount": Decimal(str(request.amount)),
        "description": request.description,
        "status": request.status,
        "date_submitted": request.date_submitted,
    })

    audit_entry = AuditLogEntry(
        audit_id=str(uuid.uuid4()),
        request_id=request.request_id,
        action="submitted",
        performed_by=request.employee_id,
        details=f"Request submitted for {request.amount} in {request.category}",
    )
    audit_table.put_item(Item=audit_entry.record())

    return {
        "statusCode": 201,
        "body": json.dumps({
            "request_id": request.request_id,
            "status": request.status,
            "date_submitted": request.date_submitted,
        })
    }