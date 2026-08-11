from abc import ABC, abstractmethod

class User(ABC):
    def __init__(self, user_id: str, name: str, email: str, department: str):
        self._user_id = user_id
        self._name = name
        self._email = email
        self._department = department

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def department(self) -> str:
        return self._department

    def get_profile(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "department": self.department
        }

    @abstractmethod
    def process(self, request):
        raise NotImplementedError

class Employee(User):
    def submit_request(self, request):
        request.submit()
        return request

    def process(self, request):
        raise PermissionError("Employees cannot process requests")


class Approver(User):
    def process(self, request, decision: str):
        if decision == "approve":
            request.approve(self.user_id)
        elif decision == "reject":
            request.reject(self.user_id)
        else:
            raise ValueError(f"Unknown decision: {decision}")
        return request

class FinanceStaff(User):
    def process(self, request):
        request.mark_paid()
        return request

    def generate_report(self, requests: list) -> dict:
        raise NotImplementedError