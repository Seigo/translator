import pandas as pd
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

def filter_chargeable_df(
    df: pd.DataFrame,
    partner_ids_to_skip: List[int]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Business rule: Apply all chargeable-specific filters and return filtered DataFrame and error DataFrames.
    - Remove rows without PartNumber (log error)
    - Remove rows with itemCount <= 0 (log error)
    - Remove rows with PartnerID in skip list
    Returns:
        Tuple of (filtered_df, no_partnumber_error_df, itemcount_nonpositive_error_df)
    """
    required_cols = ['PartNumber', 'itemCount', 'PartnerID']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        logger.error("Missing required columns for chargeable: %s", missing)
        raise ValueError(f"Missing required columns for chargeable: {missing}")

    chargeable_df = df.copy()

    # Log and filter rows without PartNumber
    no_partnumber_error_df = chargeable_df[chargeable_df['PartNumber'].isna()].copy()
    if not no_partnumber_error_df.empty:
        logger.warning("Found %d rows without PartNumber", len(no_partnumber_error_df))
    chargeable_df = chargeable_df[chargeable_df['PartNumber'].notna()]

    # Log and filter rows with non-positive itemCount (<= 0)
    itemcount_nonpositive_error_df = chargeable_df[chargeable_df['itemCount'] <= 0].copy()
    if not itemcount_nonpositive_error_df.empty:
        logger.warning("Found %d rows with non-positive itemCount", len(itemcount_nonpositive_error_df))
    chargeable_df = chargeable_df[chargeable_df['itemCount'] > 0]

    # Filter out rows with PartnerID in skip list
    before = len(chargeable_df)
    chargeable_df = chargeable_df[~chargeable_df['PartnerID'].isin(partner_ids_to_skip)]
    after = len(chargeable_df)
    if before != after:
        logger.info("Filtered out %d rows with PartnerID in skip list", before - after)

    return chargeable_df, no_partnumber_error_df, itemcount_nonpositive_error_df
