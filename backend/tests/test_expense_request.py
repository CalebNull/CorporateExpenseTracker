import pytest
from models.expense_request import ExpenseRequest

def make_request(amount = 100.0, department = "Engineering", category = "Travel",):
    return ExpenseRequest("r1", "emp1", department, category, amount, "Conference Trip")

def test_submit_sets_status_and_timestamp():
    req = make_request()
    req.submit()
    assert req.status == "submitted"
    assert req.date_submitted is not None

def test_validate_rejects_zero_amount():
    req = make_request(amount=0)
    with pytest.raises(ValueError):
        req.validate()

def test_validate_rejects_missing_category():
    req = make_request(category="")
    with pytest.raises(ValueError):
        req.validate()

def test_approve_from_submitted_succeeds():
    req = make_request()
    req.submit()
    req.approve("approver1")
    assert req.status == "approved"
    assert req.approver_id == "approver1"

def test_approve_without_submit_fails():
    req = make_request()
    with pytest.raises(ValueError):
        req.approve("approver1")

def test_reject_then_approve_fails():
    req = make_request()
    req.submit()
    req.reject("approver1")
    with pytest.raises(ValueError):
        req.approve("approver1")

def test_mark_paid_requires_approved_status():
    req = make_request()
    req.submit()
    with pytest.raises(ValueError):
        req.mark_paid()

def test_from_item_reconstructs_state():
    item = {
        "request_id": "r1",
        "employee_id": "emp1",
        "department": "Engineering",
        "category": "Travel",
        "amount": 500.0,
        "description": "Trip",
        "status": "submitted",
        "date_submitted": "2026-08-01T00:00:00+00:00",
        "date_decided": None,
        "approver_id": None,
    }
    request = ExpenseRequest.from_item(item)
    assert request.status == "submitted"
    assert request.request_id == "r1"
    assert request.date_submitted == "2026-08-01T00:00:00+00:00"