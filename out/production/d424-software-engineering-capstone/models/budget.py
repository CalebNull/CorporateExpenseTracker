class Budget:
    def __init__(self, department: str, category: str, allocated_amount: float, fiscal_period: str, spent_amount: float = 0.0):
        self._department = department
        self._category = category
        self._allocated_amount = allocated_amount
        self._spent_amount = spent_amount
        self._fiscal_period = fiscal_period


    @property
    def department(self) -> str:
        return self._department

    @property
    def category(self) -> str:
        return self._category

    @property
    def allocated_amount(self) -> float:
        return self._allocated_amount

    @property
    def spent_amount(self) -> float:
        return self._spent_amount

    @property
    def fiscal_period(self) -> str:
        return self._fiscal_period

    def remaining(self) -> float:
        return self._allocated_amount - self._spent_amount

    def deduct(self, amount: float):
        if amount <= 0:
            raise ValueError("Deduction must be greater than 0")
        if amount > self.remaining():
            raise ValueError(f"Insufficient budget: {amount}, remaining: {self.remaining()}")

        self._spent_amount += amount