import pytest

from generated_module import factorial


def test_factorial_of_zero_returns_one():
    assert factorial(0) == 1


def test_factorial_of_one_returns_one():
    assert factorial(1) == 1


def test_factorial_of_positive_integer():
    assert factorial(5) == 120


def test_factorial_of_larger_integer():
    assert factorial(8) == 40320


def test_factorial_rejects_negative_integer():
    with pytest.raises(ValueError, match="n must be non-negative"):
        factorial(-1)


def test_factorial_rejects_non_integer_float():
    with pytest.raises(TypeError, match="n must be an integer"):
        factorial(3.5)


def test_factorial_rejects_string():
    with pytest.raises(TypeError, match="n must be an integer"):
        factorial("5")
