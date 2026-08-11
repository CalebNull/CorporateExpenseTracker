import pytest
from models.budget import Budget

def make_budget(allocated=1000.0, spent=0.0):
    return Budget("Engineering", "Travel", allocated, "2026-Q3", spent)

def test_remaining_with_no_spend():
    budget = make_budget(allocated=1000.0)
    assert budget.remaining() == 1000.0

def test_remaining_after_prior_spend():
    budget = make_budget(allocated=1000.0, spent=300.0)
    assert budget.remaining() == 700.0

def test_deduct_reduces_remaining():
    budget = make_budget(allocated=1000.0)
    budget.deduct(250.0)
    assert budget.spent_amount == 250.0
    assert budget.remaining() == 750.0

def test_deduct_accumulates_across_multiple_calls():
    budget = make_budget(allocated=1000.0)
    budget.deduct(100.0)
    budget.deduct(250.0)
    assert budget.spent_amount == 350.0
    assert budget.remaining() == 650.0

def test_deduct_rejects_zero_amount():
    budget = make_budget(allocated=1000.0)
    with pytest.raises(ValueError):
        budget.deduct(0.0)

def test_deduct_rejects_negative_amount():
    budget = make_budget(allocated=1000.0)
    with pytest.raises(ValueError):
        budget.deduct(-100.0)

def test_deduct_rejects_amount_exceeding_remaining():
    budget = make_budget(allocated=1000.0, spent=900.0)
    with pytest.raises(ValueError):
        budget.deduct(250.0)

def test_deduct_exact_remaining_succeeds():
    budget = make_budget(allocated=1000.0, spent=900.0)
    budget.deduct(100.0) # exactly what's remaining
    assert budget.remaining() == 0.0