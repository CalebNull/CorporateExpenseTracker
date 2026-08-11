import pytest
from models.user import *
from models.expense_request import *

def make_request(amount=100.0):
    return ExpenseRequest("r1", "emp1", "Engineering", "Travel", amount, "Conference Trip")

def test_user_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        User("u1", "Test User", "test@example.com", "Engineering")

def test_get_profile_returns_expected_fields():
    employee = Employee("u1", "Caleb", "caleb@example.com", "Engineering")
    profile = employee.get_profile()
    assert profile == {
        "user_id": "u1",
        "name": "Caleb",
        "email": "caleb@example.com",
        "department": "Engineering",
    }

def test_properties_are_read_only():
    employee = Employee("u1", "Caleb", "caleb@example.com", "Engineering")
    with pytest.raises(AttributeError):
        employee.name = "Someone Else"

def test_employee_submit_request():
    employee = Employee("u1", "Caleb", "caleb@example.com", "Engineering")
    request = make_request()
    employee.submit_request(request)
    assert request.status == "submitted"

def test_employee_cannot_process_requests():
    employee = Employee("u1", "Caleb", "caleb@example.com", "Engineering")
    request = make_request()
    request.submit()
    with pytest.raises(PermissionError):
        employee.process(request)

def test_approver_approve():
    approver = Approver("a1", "Jaimie", "jaimie@example.com", "Engineering")
    request = make_request()
    request.submit()
    approver.process(request, "approve")
    assert request.status == "approved"
    assert request.approver_id == "a1"

def test_approver_process_reject():
    approver = Approver("a1", "Jaimie", "jaimie@example.com", "Engineering")
    request = make_request()
    request.submit()
    approver.process(request, "reject")
    assert request.status == "rejected"
    assert request.approver_id == "a1"

def test_approver_process_invalid_decision():
    approver = Approver("a1", "Jaimie", "jaimie@example.com", "Engineering")
    request = make_request()
    request.submit()
    with pytest.raises(ValueError):
        approver.process(request, "maybe")

def test_finance_staff_marks_paid():
    finance = FinanceStaff("f1", "Robin", "robin@example.com", "Finance")
    request = make_request()
    request.submit()
    request.approve("a1")
    finance.process(request)
    assert request.status == "paid"