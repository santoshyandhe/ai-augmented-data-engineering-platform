import pytest

from generated_module import factorial, run_factorial_examples, validate_factorial_behavior


def test_factorial_happy_path_small_values():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120


def test_factorial_larger_value():
    assert factorial(7) == 5040


def test_factorial_negative_raises_value_error():
    with pytest.raises(ValueError, match="factorial\(\) is not defined for negative values"):
        factorial(-1)


def test_factorial_non_integer_raises_type_error_for_float():
    with pytest.raises(TypeError, match="factorial\(\) argument must be an integer"):
        factorial(2.5)


def test_factorial_bool_raises_type_error():
    with pytest.raises(TypeError, match="factorial\(\) argument must be an integer"):
        factorial(True)


def test_run_factorial_examples_returns_expected_mapping():
    assert run_factorial_examples() == {"0": 1, "1": 1, "3": 6, "5": 120}


def test_validate_factorial_behavior_reports_expected_errors():
    assert validate_factorial_behavior() == {
        "negative_input": "factorial() is not defined for negative values",
        "float_input": "factorial() argument must be an integer",
        "bool_input": "factorial() argument must be an integer",
    }
