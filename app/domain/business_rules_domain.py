import pandas as pd
import logging
from typing import Any
from app.utils.strings import normalize_alphanumeric_string

logger = logging.getLogger(__name__)

def map_partner_purchased_plan_id(input_str: str) -> str:
    """
    Business rule: Normalize and validate accountGuid as partnerPurchasedPlanID.
    """
    try:
        return normalize_alphanumeric_string(input_str, expected_length=32)
    except ValueError as e:
        logger.error("Invalid partnerPurchasedPlanID: %s", e)
        raise

def add_partner_purchased_plan_id_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Business rule: Add 'partnerPurchasedPlanID' column to DataFrame by mapping 'accountGuid'
    using the map_partner_purchased_plan_id rule.
    """
    if 'accountGuid' not in df.columns:
        logger.error("Column 'accountGuid' not found in DataFrame")
        raise ValueError("Column 'accountGuid' not found in DataFrame")
    try:
        df['partnerPurchasedPlanID'] = df['accountGuid'].map(map_partner_purchased_plan_id)
        logger.info("Added 'partnerPurchasedPlanID' column using 'accountGuid'")
        return df
    except Exception as e:
        logger.error("Failed to add 'partnerPurchasedPlanID' column: %s", e)
        raise