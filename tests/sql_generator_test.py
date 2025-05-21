"""
Tests for the SQLGenerator class from the sql_generator module.

This file covers:
- Generating SQL insert statements for the chargeable table.
- Generating SQL insert statements for the domains table.
- Verifying that the output SQL files are created and contain the expected content.
"""

import os
import pandas as pd
from app.services.sql_generator import SQLGenerator

def test_write_chargeable_sql(tmp_path):
    """Test that the chargeable SQL file is created and contains expected content."""
    df = pd.DataFrame({
        "PartnerID": [1, 2],
        "product": ["prodA", "prodB"],
        "partnerPurchasedPlanID": ["idA", "idB"],
        "plan": ["planA", "planB"],
        "usage": [10, 20]
    })
    output_dir = tmp_path
    SQLGenerator.write_chargeable_sql(df, str(output_dir))
    output_file = output_dir / "insert_into_chargeable.sql"
    assert output_file.exists()
    content = output_file.read_text()
    assert "INSERT INTO chargeable" in content
    assert '"partnerID"' in content
    assert "(1, 'prodA', 'idA', 'planA', 10)" in content or "(1,'prodA','idA','planA',10)" in content

def test_write_domains_sql(tmp_path):
    """Test that the domains SQL file is created and contains expected content."""
    df = pd.DataFrame({
        "partnerPurchasedPlanID": ["idA", "idB"],
        "domains": ["a.com", "b.com"]
    })
    output_dir = tmp_path
    SQLGenerator.write_domains_sql(df, str(output_dir))
    output_file = output_dir / "insert_into_domains.sql"
    assert output_file.exists()
    content = output_file.read_text()
    assert "INSERT INTO domains" in content
    assert '"partnerPurchasedPlanID"' in content
    assert "(\'idA\', \'a.com\')" in content or "(\"idA\", \"a.com\")" in content