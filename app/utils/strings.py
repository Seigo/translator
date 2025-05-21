from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

def escape_sql_value(value: Any) -> str:
    """
    Escapes a value for safe inclusion in SQL statements.
    - Strings have single quotes escaped and are wrapped in single quotes.
    - None is converted to NULL.
    - Other types are converted to string as-is.
    """
    if value is None:
        return "NULL"
    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    return str(value)

def normalize_alphanumeric_string(input_str: str, expected_length: Optional[int] = None) -> str:
    """
    Normalize a string by removing all non-alphanumeric characters.
    Optionally validates the resulting string length.
    """
    result = ''.join(char for char in str(input_str) if char.isalnum())
    if expected_length is not None and len(result) != expected_length:
        logger.error(
            "Normalized string does not match expected length: expected %d, got '%s' (%d chars)",
            expected_length, result, len(result)
        )
        raise ValueError(f'Normalized string must have {expected_length} characters. Found: {result}')
    return result