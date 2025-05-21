"""
Tests for the business_rules_domain module.

This file covers:
- Normalization and validation of accountGuid as partnerPurchasedPlanID.
- Adding the partnerPurchasedPlanID column to a DataFrame.
- Error handling for invalid or missing accountGuid values.
"""

import pandas as pd
import pytest
from app.domain.business_rules_domain import (
    map_partner_purchased_plan_id,
    add_partner_purchased_plan_id_column,
)

def test_map_partner_purchased_plan_id_valid():
    """Test normalization of a valid accountGuid."""
    guid = "a1b2-c3d4_e5f6g7h8i9j0k1l2m3n4o5p6"
    normalized = map_partner_purchased_plan_id(guid)
    assert isinstance(normalized, str)
    assert len(normalized) == 32
    assert normalized.isalnum()

def test_map_partner_purchased_plan_id_invalid_length():
    """Test error for accountGuid with invalid length."""
    guid = "short-guid"
    with pytest.raises(ValueError):
        map_partner_purchased_plan_id(guid)

def test_add_partner_purchased_plan_id_column_success():
    """Test successful addition of partnerPurchasedPlanID column."""
    df = pd.DataFrame({
        "accountGuid": ["a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6", "12345678901234567890123456789012"]
    })
    result = add_partner_purchased_plan_id_column(df.copy())
    assert "partnerPurchasedPlanID" in result.columns
    assert all(result["partnerPurchasedPlanID"].apply(lambda x: isinstance(x, str) and len(x) == 32))

def test_add_partner_purchased_plan_id_column_missing_accountGuid():
    """Test error when accountGuid column is missing."""
    df = pd.DataFrame({"other": ["foo", "bar"]})
    with pytest.raises(ValueError):
        add_partner_purchased_plan_id_column(df)

def test_add_partner_purchased_plan_id_column_invalid_guid():
    """Test error when all accountGuid values are invalid."""
    df = pd.DataFrame({"accountGuid": ["short-guid", "another-short"]})
    with pytest.raises(ValueError):
        add_partner_purchased_plan_id_column(df)