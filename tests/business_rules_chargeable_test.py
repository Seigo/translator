"""
Tests for the filter_chargeable_df function from business_rules_chargeable.

This file covers:
- Removing rows without PartNumber.
- Removing rows with negative itemCount.
- Removing rows with PartnerID in the skip list.
- Behavior when multiple filters apply.
- Error when required columns are missing.
"""

import pandas as pd
import pytest
from app.domain.business_rules_chargeable import filter_chargeable_df

@pytest.fixture
def sample_df():
    """Sample DataFrame for tests."""
    return pd.DataFrame({
        'PartNumber': ['A', None, 'B', 'C', 'D'],
        'itemCount': [10, 5, -2, 20, 30],
        'PartnerID': [1, 2, 3, 4, 5]
    })

def test_filter_chargeable_df_removes_no_partnumber(sample_df):
    """Test removal of rows without PartNumber."""
    filtered, no_partnumber, itemcount_negative = filter_chargeable_df(sample_df, partner_ids_to_skip=[])
    assert len(no_partnumber) == 1
    assert no_partnumber.iloc[0]['PartnerID'] == 2
    assert 2 not in filtered['PartnerID'].values

def test_filter_chargeable_df_removes_negative_itemcount(sample_df):
    """Test removal of rows with negative itemCount."""
    filtered, no_partnumber, itemcount_negative = filter_chargeable_df(sample_df, partner_ids_to_skip=[])
    assert len(itemcount_negative) == 1
    assert itemcount_negative.iloc[0]['PartnerID'] == 3
    assert 3 not in filtered['PartnerID'].values

def test_filter_chargeable_df_removes_partner_ids_to_skip(sample_df):
    """Test removal of rows with PartnerID in skip list."""
    filtered, no_partnumber, itemcount_negative = filter_chargeable_df(sample_df, partner_ids_to_skip=[4, 5])
    assert 4 not in filtered['PartnerID'].values
    assert 5 not in filtered['PartnerID'].values

def test_filter_chargeable_df_all_filters(sample_df):
    """Test applying all filters together."""
    filtered, no_partnumber, itemcount_negative = filter_chargeable_df(sample_df, partner_ids_to_skip=[1])
    assert list(filtered['PartnerID']) == [4, 5]

def test_filter_chargeable_df_missing_columns():
    """Test error when required columns are missing."""
    df = pd.DataFrame({'foo': [1], 'bar': [2]})
    with pytest.raises(ValueError):
        filter_chargeable_df(df, partner_ids_to_skip=[])