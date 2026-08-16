import pytest
from models.audit_log import *

def test_record_returns_expected_dict():
    entry = AuditLogEntry(
        "audit1", "r1", "approved", "approver1",
        details="Approved by manager", timestamp="2026-08-11T12:00:00+00:00"
    )
    assert entry.record() == {
        "audit_id": "audit1",
        "request_id": "r1",
        "action": "approved",
        "performed_by": "approver1",
        "details": "Approved by manager",
        "timestamp": "2026-08-11T12:00:00+00:00",
    }

def test_timestamp_auto_generated_when_not_provided():
    entry = AuditLogEntry("audit1", "r1", "submitted", "emp1")
    assert entry.timestamp is not None
    assert isinstance(entry.timestamp, str)

def test_timestamp_uses_provided_value_when_given():
    entry = entry = AuditLogEntry("audit1", "r1", "submitted", "emp1", timestamp="2026-01-01T00:00:00+00:00")
    assert entry.timestamp == "2026-01-01T00:00:00+00:00"

def test_default_details_is_empty_string():
    entry = AuditLogEntry("audit1", "r1", "submitted", "emp1")
    assert entry.details == ""

def test_properties_are_read_only():
    entry = AuditLogEntry("audit1", "r1", "submitted", "emp1")
    with pytest.raises(AttributeError):
        entry.action = "tampered"