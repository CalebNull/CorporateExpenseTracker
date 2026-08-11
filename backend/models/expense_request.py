from datetime import datetime, timezone

class ExpenseRequest:
    VALID_TRANSITIONS = {
        None: {"submitted"},
        "submitted": {"approved", "rejected"},
        "approved": {"paid"},
        "rejected": set(),
        "paid": set(),
    }

    def __init__(self, request_id: str, employee_id: str, department: str, category: str, amount: float, description: str):
        self._request_id = request_id
        self._employee_id = employee_id
        self._department = department
        self._category = category
        self._amount = amount
        self._description = description
        self._status = None
        self._date_submitted = None
        self._date_decided = None
        self._approver_id = None

    @property
    def request_id(self) -> str:
        return self._request_id

    @property
    def employee_id(self) -> str:
        return self._employee_id

    @property
    def department(self) -> str:
        return self._department

    @property
    def category(self) -> str:
        return self._category

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def description(self) -> str:
        return self._description

    @property
    def status(self) -> str:
        return self._status

    @property
    def date_submitted(self) -> str:
        return self._date_submitted

    @property
    def date_decided(self) -> str:
        return self._date_decided

    @property
    def approver_id(self) -> str:
        return self._approver_id

    def validate(self) -> bool:
        if self._amount is None or self._amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if not self._department or not self._category:
            raise ValueError("Department and category are required")
        return True

    def _transition(self, new_status: str):
        allowed = self.VALID_TRANSITIONS.get(self._status, set())
        if new_status not in allowed:
            raise ValueError(f"Cannot transition from {self._status} to {new_status}")
        self._status = new_status

    def submit(self):
        self.validate()
        self._transition("submitted")
        self._date_submitted = datetime.now(timezone.utc).isoformat()

    def approve(self, approver_id: str):
        self._transition("approved")
        self._approver_id = approver_id
        self._date_decided = datetime.now(timezone.utc).isoformat()

    def reject(self, approver_id: str):
        self._transition("rejected")
        self._approver_id = approver_id
        self._date_decided = datetime.now(timezone.utc).isoformat()

    def mark_paid(self):
        self._transition("paid")