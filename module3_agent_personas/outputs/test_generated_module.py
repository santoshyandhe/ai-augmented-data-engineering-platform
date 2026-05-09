import pytest

from generated_module import is_palindrome


def test_is_palindrome_basic_true():
    assert is_palindrome("Racecar") is True


def test_is_palindrome_ignores_case_and_punctuation():
    assert is_palindrome("A man, a plan, a canal: Panama") is True


def test_is_palindrome_false_for_non_palindrome():
    assert is_palindrome("hello") is False


def test_is_palindrome_empty_string_is_true():
    assert is_palindrome("") is True


def test_is_palindrome_only_non_alphanumeric_is_true():
    assert is_palindrome("!!!   ,,,") is True


def test_is_palindrome_numeric_palindrome_is_true():
    assert is_palindrome("12321") is True


def test_is_palindrome_numeric_non_palindrome_is_false():
    assert is_palindrome("12345") is False


def test_is_palindrome_raises_type_error_for_none():
    with pytest.raises(TypeError):
        is_palindrome(None)
