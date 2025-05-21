import pandas as pd
import logging
from typing import List, Dict, Callable, Any, Optional

logger = logging.getLogger(__name__)

def load_and_prepare_dataframe(filepath: str, headers: List[str]) -> pd.DataFrame:
    """Load and filter the main DataFrame based on provided headers."""
    try:
        df = pd.read_csv(filepath)
        logger.info("Loaded DataFrame from %s with %d rows", filepath, len(df))
        missing = [col for col in headers if col not in df.columns]
        if missing:
            logger.error("Missing required columns in CSV: %s", missing)
            raise ValueError(f"Missing required columns in CSV: {missing}")
        df = df[headers].copy()
        return df
    except Exception as e:
        logger.error("Failed to load or prepare DataFrame: %s", e)
        raise

def apply_product_mapping(df: pd.DataFrame, partnumber_to_product_map: Dict[str, str]) -> pd.DataFrame:
    """Map 'PartNumber' to 'product' using the provided mapping."""
    if 'PartNumber' not in df.columns:
        logger.error("Column 'PartNumber' not found in DataFrame")
        raise ValueError("Column 'PartNumber' not found in DataFrame")
    df['product'] = df['PartNumber'].map(partnumber_to_product_map)
    before = len(df)
    df = df[df['product'].notna()]
    logger.info("Filtered products: %d -> %d rows", before, len(df))
    return df

def apply_usage_reduction(df: pd.DataFrame, itemcount_to_usage_reduction_rules: Dict[str, Any]) -> pd.DataFrame:
    """Map 'itemCount' to 'usage' using reduction rules."""
    if not isinstance(itemcount_to_usage_reduction_rules, dict):
        logger.error("ITEMCOUNT_TO_USAGE_REDUCTION_RULES is not a dictionary")
        raise ValueError("ITEMCOUNT_TO_USAGE_REDUCTION_RULES is not a dictionary")
    if 'itemCount' not in df.columns or 'PartNumber' not in df.columns:
        logger.error("Required columns 'itemCount' or 'PartNumber' not found in DataFrame")
        raise ValueError("Required columns 'itemCount' or 'PartNumber' not found in DataFrame")
    def map_itemcount_to_usage(row: pd.Series) -> Any:
        result = row['itemCount']
        key = row['PartNumber']
        if key in itemcount_to_usage_reduction_rules:
            result = result / itemcount_to_usage_reduction_rules[key]
        return result
    df['usage'] = df.apply(map_itemcount_to_usage, axis=1)
    logger.info("Applied usage reduction to DataFrame")
    return df

def prepare_domains_df(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the domains DataFrame for SQL insertion."""
    required_cols = ['domains', 'partnerPurchasedPlanID']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        logger.error("Missing required columns for domains: %s", missing)
        raise ValueError(f"Missing required columns for domains: {missing}")
    domains_df = df[required_cols].copy()
    before = len(domains_df)
    domains_df = domains_df[domains_df['partnerPurchasedPlanID'].notna()]
    domains_df = domains_df[domains_df['domains'].notna()]
    domains_df = domains_df.drop_duplicates(keep='first', subset=['domains'])
    logger.info("Prepared domains DataFrame: %d -> %d rows", before, len(domains_df))
    return domains_df

def add_processed_column(
    df: pd.DataFrame,
    new_column: str,
    source_column: str,
    processing_func: Callable[[Any], Any]
) -> pd.DataFrame:
    """
    Adds a new column to the DataFrame by applying a processing function to the source column.
    """
    if source_column not in df.columns:
        logger.error("Source column '%s' not found in DataFrame", source_column)
        raise ValueError(f"Source column '{source_column}' not found in DataFrame")
    df[new_column] = df[source_column].map(processing_func)
    logger.info("Added processed column '%s' from '%s'", new_column, source_column)
    return df

def normalize_alphanumeric_string(input_str: str, expected_length: Optional[int] = None) -> str:
    """
    Normalize a string by removing all non-alphanumeric characters.
    Optionally validates the resulting string length.

    Args:
        input_str (str): The string to normalize.
        expected_length (int, optional): If provided, validates the normalized string length.

    Returns:
        str: The normalized alphanumeric string.

    Raises:
        ValueError: If expected_length is set and the normalized string does not match it.
    """
    result = ''.join(char for char in str(input_str) if char.isalnum())
    if expected_length is not None and len(result) != expected_length:
        raise ValueError(f'Normalized string must have {expected_length} characters. Found: {result}')
    return result