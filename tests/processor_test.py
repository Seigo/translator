"""
Tests for the FileProcessor class from the processor module.

This file covers:
- Validation of required columns in DataFrames.
- Loading the partnumber-to-product mapping from a JSON file.
- Writing totals by Product and error logs to output files.
- Full processing flow, including generation of all expected output files.
"""

import os
import json
import pandas as pd
import pytest
from app.services.processor import FileProcessor

@pytest.fixture
def tmp_mapping_file(tmp_path):
    """Fixture to create a temporary mapping JSON file."""
    mapping = {"A": "ProductA", "B": "ProductB"}
    file_path = tmp_path / "mapping.json"
    with open(file_path, "w") as f:
        json.dump(mapping, f)
    return str(file_path)

@pytest.fixture
def processor(tmp_mapping_file, tmp_path):
    """Fixture to create a FileProcessor instance with temp paths."""
    return FileProcessor(
        output_files_path=str(tmp_path),
        partnumber_to_product_map_filepath=tmp_mapping_file
    )

@pytest.fixture
def sample_df():
    """Sample DataFrame for validation tests."""
    return pd.DataFrame({
        "PartnerID": [1, 2, 3],
        "accountGuid": [
            "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            "12345678901234567890123456789012",
            "abcdefabcdefabcdefabcdefabcdefab"
        ],
        "domains": ["a.com", "b.com", "c.com"],
        "plan": ["plan1", "plan2", "plan3"],
        "PartNumber": ["A", "B", "C"],
        "itemCount": [10, 20, 30]
    })

def test_validate_columns_ok(processor, sample_df):
    """Test that _validate_columns passes when all columns are present."""
    processor._validate_columns(sample_df, ["PartnerID", "accountGuid"])

def test_validate_columns_missing(processor, sample_df):
    """Test that _validate_columns raises ValueError when columns are missing."""
    with pytest.raises(ValueError):
        processor._validate_columns(sample_df, ["not_a_column"])

def test_load_partnumber_to_product_map(processor):
    """Test loading the partnumber-to-product mapping from JSON."""
    mapping = processor._load_partnumber_to_product_map()
    assert isinstance(mapping, dict)
    assert "A" in mapping

def test_write_totals_by_product_creates_file(processor, tmp_path):
    """Test that totals_by_product CSV file is created and contains expected columns."""
    df = pd.DataFrame({
        "product": ["A", "B", "A"],
        "itemCount": [10, 20, 30]
    })
    processor._write_totals_by_product(df)
    output_file = os.path.join(processor.output_files_path, "totals_by_product.csv")
    assert os.path.exists(output_file)
    out_df = pd.read_csv(output_file)
    assert "itemCount" in out_df.columns

def test_write_error_logs_creates_files(processor, tmp_path):
    """Test that error log CSV files are created."""
    df1 = pd.DataFrame({"a": [1]})
    df2 = pd.DataFrame({"b": [2]})
    processor._write_error_logs(df1, df2)
    assert os.path.exists(os.path.join(processor.output_files_path, "no_partnumber_error_df.csv"))
    assert os.path.exists(os.path.join(processor.output_files_path, "itemcount_nonpositive_error_df.csv"))

def test_process_full_flow(processor, tmp_path):
    """Test the full processing flow and check that all output files are generated."""
    # Prepare input CSV
    csv_path = tmp_path / "input.csv"
    df = pd.DataFrame({
        "PartnerID": [1, 2],
        "accountGuid": [
            "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            "12345678901234567890123456789012"
        ],
        "domains": ["a.com", "b.com"],
        "plan": ["plan1", "plan2"],
        "PartNumber": ["A", "B"],
        "itemCount": [10, 20]
    })
    df.to_csv(csv_path, index=False)
    processor.process(
        usage_report_filepath=str(csv_path),
        partner_ids_to_skip=[],
        itemcount_to_usage_reduction_rules={"A": 2, "B": 2},
        headers=["PartnerID", "accountGuid", "domains", "plan", "PartNumber", "itemCount"]
    )
    # Check if output files were created
    assert os.path.exists(os.path.join(processor.output_files_path, "totals_by_product.csv"))
    assert os.path.exists(os.path.join(processor.output_files_path, "insert_into_chargeable.sql"))
    assert os.path.exists(os.path.join(processor.output_files_path, "insert_into_domains.sql"))