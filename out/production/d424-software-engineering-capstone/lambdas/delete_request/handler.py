import json
import uuid

import boto3

from models.audit_log import AuditLogEntry
from models.expense_request import ExpenseRequest
from auth import verify_role, UnauthorizedError

dynamodb = boto3.resource("dynamodb")
requests_table = dynamodb.Table("ExpenseRequests")
audit_table = dynamodb.Table("AuditLog")


def handler(event, context):
    path_params = event.get("pathParameters") or {}
    request_id = path_params.get("request_id")
    body = json.loads(event.get("body") or "{}")
    employee_id = body.get("employee_id")

    if not request_id or not employee_id:
        return {"statusCode": 400, "body": json.dumps({"error": "request_id and employee_id are required"})}

    item = requests_table.get_item(Key={"request_id": request_id}).get("Item")
    if item is None:
        return {"statusCode": 404, "body": json.dumps({"error": "Request not found"})}

    request = ExpenseRequest.from_item(item)

    try:
        verify_role(employee_id, "employee")
    except UnauthorizedError as e:
        return {"statusCode": 403, "body": json.dumps({"error": str(e)})}

    if request.employee_id != employee_id:
        return {"statusCode": 403, "body": json.dumps({"error": "You may only delete your own requests"})}

    if request.status != "submitted":
        return {"statusCode": 400, "body": json.dumps({"error": "Only submitted requests can be deleted"})}

    requests_table.delete_item(Key={"request_id": request_id})

    audit_entry = AuditLogEntry(
        audit_id=str(uuid.uuid4()),
        request_id=request_id,
        action="deleted",
        performed_by=employee_id,
        details="Request withdrawn by employee before approval",
    )
    audit_table.put_item(Item=audit_entry.record())

    return {"statusCode": 200, "body": json.dumps({"request_id": request_id, "deleted": True})}