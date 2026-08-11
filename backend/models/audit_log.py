from datetime import datetime, timezone

class AuditLogEntry:
    def __init__(self, audit_id: str, request_id: str, action: str, performed_by: str, details: str = "", timestamp: str = None):
        self._audit_id = audit_id
        self._request_id = request_id
        self._action = action
        self._performed_by = performed_by
        self._details = details
        self._timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    @property
    def audit_id(self) -> str:
        return self._audit_id

    @property
    def request_id(self) -> str:
        return self._request_id

    @property
    def action(self) -> str:
        return self._action

    @property
    def performed_by(self) -> str:
        return self._performed_by

    @property
    def details(self) -> str:
        return self._details

    @property
    def timestamp(self) -> str:
        return self._timestamp

    def record(self) -> dict:
        return {
            "audit_id": self._audit_id,
            "request_id": self._request_id,
            "action": self._action,
            "performed_by": self._performed_by,
            "details": self._details,
            "timestamp": self._timestamp,
        }