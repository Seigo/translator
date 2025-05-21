"""
Tests for the strings utility functions.

This file covers:
- Escaping values for safe SQL inclusion.
- Normalizing alphanumeric strings.
- Error handling for invalid normalization length.
"""

import pytest
from app.utils.strings import escape_sql_value, normalize_alphanumeric_string

def test_escape_sql_value_none():
    """Test escaping None returns SQL NULL."""
    assert escape_sql_value(None) == "NULL"

def test_escape_sql_value_str():
    """Test escaping strings, including single quotes."""
    assert escape_sql_value("O'Reilly") == "'O''Reilly'"
    assert escape_sql_value("simple") == "'simple'"

def test_escape_sql_value_int_float():
    """Test escaping integers and floats returns string representation."""
    assert escape_sql_value(123) == "123"
    assert escape_sql_value(45.67) == "45.67"

def test_escape_sql_value_empty_string():
    """Test escaping an empty string."""
    assert escape_sql_value("") == "''"

def test_normalize_alphanumeric_string_basic():
    """Test normalization removes non-alphanumeric characters."""
    assert normalize_alphanumeric_string("a-b_c.1") == "abc1"
    assert normalize_alphanumeric_string("A!@#B$%^C123") == "ABC123"

def test_normalize_alphanumeric_string_expected_length_ok():
    """Test normalization with correct expected length."""
    assert normalize_alphanumeric_string("a1b2c3d4", expected_length=8) == "a1b2c3d4"

def test_normalize_alphanumeric_string_expected_length_fail():
    """Test error when normalized string does not match expected length."""
    with pytest.raises(ValueError):
        normalize_alphanumeric_string("abc", expected_length=5)

def test_normalize_alphanumeric_string_empty():
    """Test normalization of an empty string returns empty string."""
    assert normalize_alphanumeric_string("") == ""

def test_normalize_alphanumeric_string_only_specials():
    """Test normalization of a string with only special characters returns empty string."""
    assert normalize_alphanumeric_string("!@#$%^&*()") == ""