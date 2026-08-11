# API Design

This document defines the REST API exposed via AWS API Gateway, backed by Lambda functions and the DynamoDB tables
defined in `schema.md`. Each route maps to one Lambda function.

## Expense Requests

|Method|Path|Description|Role|
|---|----|---|-------|
|POST|`/requests`|Submit a new expense request. Body: `employee_id, department, category, amount, description`|Employee|
|GET|`/requests/{request_id}`|Get a single request by ID|Any authenticated user|
|GET|`/requests?employee_id=X`|List all requests for one employee (search)|Employee|
|GET|`/requests?status=X`|List requests by status, e.g. an approver's pending queue (search)|Approver|
|GET|`/requests?department=X`|List requests by department (search)|Finance|
|GET|`/requests/{request_id}/approve`|Approve a request. Body: `approver_id`|Approver|
|GET|`/requests/{request_id}/reject`|Reject a request. Body: `approver_id`|Approver|
|GET|`/requests/{request_id}/pay`|Mark an approved request as paid|Finance|

## Budgets

|Method| Path |Description|Role|
|---|---|---|---|
|GET|`/budgets?department`|List budgets for a department (search)|Approver, Finance|
|GET|`/budgets/{department}/{category}`|Get on budget's remaining/spent amounts|Approver, Finance|
|PUT|`/budgets/{department}/{category}`|Create/update a budget's allocated amount|Finance|

## Users

|Method|Path|Description|Role|
|---|---|---|---|
|GET|`/users/{user_id}`|Get a user's profile|Any authenticated user|
|POST|`/users`|Create a user record. Body: `name, email, role, department`|Finance/Admin|

## Audit & Reports

|Method| Path                                        |Description|Role|
|---|---|---|---|
|GET|`/requests/{request_id}/audit`|Full audit trail for one request|Finance|
|GET|`/reports/spending?department=X&start=Y&end=Z`|Spending report - title, columns (date, employee, category, amount, status), rows across the date range|Finance|

## Notes

- All routes sit behind API Gateway, each mapped to one Lambda function.
- The `GET /requests?...` query-param routes satisfy the "search functionality with multiple rows" requirement. Each returns a list, not a single item.
- Role restrictions are not enforced by API Gateway directly; each Lambda checks the caller's `role` (via the `Users` table) before acting, tying back into the `Employee`/`Approver`/`FinanceStaff` classes.