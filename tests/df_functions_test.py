"""
Tests for the df_functions module.

This file covers:
- Loading and filtering DataFrames from CSV files.
- Mapping PartNumber to product.
- Applying usage reduction rules.
- Preparing domains DataFrame for SQL insertion.
- Adding processed columns to DataFrames.
- Normalizing alphanumeric strings.
- Error handling for missing columns and invalid inputs.
"""

import pandas as pd
import pytest
from app.domain.df_functions import (
    load_and_prepare_dataframe,
    apply_product_mapping,
    apply_usage_reduction,
    prepare_domains_df,
    add_processed_column,
    normalize_alphanumeric_string,
)

def test_load_and_prepare_dataframe(tmp_path):
    """Test loading and filtering DataFrame from CSV."""
    csv_content = "a,b,c\n1,2,3\n4,5,6"
    file = tmp_path / "test.csv"
    file.write_text(csv_content)
    df = load_and_prepare_dataframe(str(file), headers=["a", "b"])
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2

def test_load_and_prepare_dataframe_missing_column(tmp_path):
    """Test error when required columns are missing in CSV."""
    csv_content = "a,b\n1,2"
    file = tmp_path / "test.csv"
    file.write_text(csv_content)
    with pytest.raises(ValueError):
        load_and_prepare_dataframe(str(file), headers=["a", "b", "c"])

def test_apply_product_mapping():
    """Test mapping PartNumber to product."""
    df = pd.DataFrame({"PartNumber": ["X", "Y", "Z"]})
    mapping = {"X": "prod1", "Y": "prod2"}
    result = apply_product_mapping(df, mapping)
    assert "product" in result.columns
    assert set(result["product"]) == {"prod1", "prod2"}
    assert "Z" not in result["PartNumber"].values

def test_apply_product_mapping_missing_column():
    """Test error when PartNumber column is missing."""
    df = pd.DataFrame({"Other": [1, 2]})
    with pytest.raises(ValueError):
        apply_product_mapping(df, {"A": "B"})

def test_apply_usage_reduction():
    """Test applying usage reduction rules."""
    df = pd.DataFrame({"itemCount": [1000, 2000], "PartNumber": ["A", "B"]})
    rules = {"A": 100, "B": 1000}
    result = apply_usage_reduction(df, rules)
    assert "usage" in result.columns
    assert result.loc[0, "usage"] == 10
    assert result.loc[1, "usage"] == 2

def test_apply_usage_reduction_missing_columns():
    """Test error when required columns are missing for usage reduction."""
    df = pd.DataFrame({"foo": [1]})
    with pytest.raises(ValueError):
        apply_usage_reduction(df, {})

def test_apply_usage_reduction_invalid_rules():
    """Test error when usage reduction rules are not a dictionary."""
    df = pd.DataFrame({"itemCount": [1], "PartNumber": ["A"]})
    with pytest.raises(ValueError):
        apply_usage_reduction(df, [])

def test_prepare_domains_df():
    """Test preparing domains DataFrame for SQL insertion."""
    df = pd.DataFrame({
        "domains": ["a.com", "b.com", None, "a.com"],
        "partnerPurchasedPlanID": ["id1", "id2", "id3", None]
    })
    result = prepare_domains_df(df)
    assert "domains" in result.columns
    assert "partnerPurchasedPlanID" in result.columns
    assert result["domains"].isna().sum() == 0
    assert result["partnerPurchasedPlanID"].isna().sum() == 0
    assert result["domains"].duplicated().sum() == 0

def test_prepare_domains_df_missing_columns():
    """Test error when required columns are missing in domains DataFrame."""
    df = pd.DataFrame({"foo": [1]})
    with pytest.raises(ValueError):
        prepare_domains_df(df)

def test_add_processed_column():
    """Test adding a processed column to DataFrame."""
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = add_processed_column(df, "b", "a", lambda x: x * 2)
    assert "b" in result.columns
    assert all(result["b"] == df["a"] * 2)

def test_add_processed_column_missing_source():
    """Test error when source column is missing for processed column."""
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        add_processed_column(df, "b", "not_a", lambda x: x)

def test_normalize_alphanumeric_string():
    """Test normalization of alphanumeric strings."""
    assert normalize_alphanumeric_string("a-b_c.1", expected_length=4) == "abc1"
    assert normalize_alphanumeric_string("A!@#B$%^C123") == "ABC123"

def test_normalize_alphanumeric_string_invalid_length():
    """Test error when normalized string does not match expected length."""
    with pytest.raises(ValueError):
        normalize_alphanumeric_string("abc", expected_length=5)