import json
import uuid

import boto3

from models.audit_log import AuditLogEntry
from models.expense_request import ExpenseRequest
from models.user import FinanceStaff

dynamodb = boto3.resource("dynamodb")
requests_table = dynamodb.Table("ExpenseRequests")
audit_table = dynamodb.Table("AuditLog")

def handler(event, context):
    request_id = event["pathParameters"]["request_id"]
    body = json.loads(event["body"])
    finance_user_id = body["finance_user_id"]

    item = requests_table.get_item(Key={"request_id": request_id}).get("Item")
    if item is None:
        return {"statusCode": 404, "body": json.dumps({"error": "Request not found"})}

    request = ExpenseRequest.from_item(item)
    finance_staff = FinanceStaff(finance_user_id, "", "", request.department)

    try:
        finance_staff.process(request)
    except ValueError as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}

    requests_table.update_item(
        Key={"request_id": request.request_id},
        UpdateExpression="SET #s = :status",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":status": request.status},
    )

    audit_entry = AuditLogEntry(
        audit_id=str(uuid.uuid4()),
        request_id=request.request_id,
        action="paid",
        performed_by=finance_user_id,
        details=f"Request marked paid by {finance_user_id}",
    )
    audit_table.put_item(Item=audit_entry.record())

    return {
        "statusCode": 200,
        "body": json.dumps({
            "request_id": request.request_id,
            "status": request.status,
        })
    }