import pandas as pd
import json
import logging
from typing import List, Dict, Any
from app.domain.df_functions import (
    load_and_prepare_dataframe,
    add_processed_column,
    apply_product_mapping,
    apply_usage_reduction,
    prepare_domains_df,
)
from app.domain.business_rules_chargeable import filter_chargeable_df
from app.domain.business_rules_domain import map_partner_purchased_plan_id
from app.services.sql_generator import SQLGenerator

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(
        self,
        output_files_path: str,
        partnumber_to_product_map_filepath: str
    ):
        self.output_files_path = output_files_path
        self.partnumber_to_product_map_filepath = partnumber_to_product_map_filepath
        self.partnumber_to_product_map = self._load_partnumber_to_product_map()

    def process(
        self,
        usage_report_filepath: str,
        partner_ids_to_skip: List[int],
        itemcount_to_usage_reduction_rules: Dict[str, Any],
        headers: List[str]
    ) -> None:
        """
        Main entry point to process the usage report and generate outputs.
        """
        logger.info("Loading and preparing DataFrame from %s", usage_report_filepath)
        df = load_and_prepare_dataframe(usage_report_filepath, headers)
        self._validate_columns(df, ['accountGuid'])
        df = add_processed_column(df, 'partnerPurchasedPlanID', 'accountGuid', map_partner_purchased_plan_id)

        # CHARGEABLE processing
        self._process_chargeable(df, partner_ids_to_skip, itemcount_to_usage_reduction_rules)

        # DOMAINS processing
        self._process_domains(df)

    def _process_chargeable(
        self,
        df: pd.DataFrame,
        partner_ids_to_skip: List[int],
        itemcount_to_usage_reduction_rules: Dict[str, Any]
    ) -> None:
        """Process and output chargeable data and logs."""
        self._validate_columns(df, ['PartNumber', 'itemCount', 'PartnerID'])
        chargeable_df, no_partnumber_error_df, itemcount_nonpositive_error_df = filter_chargeable_df(df, partner_ids_to_skip)
        chargeable_df = apply_product_mapping(chargeable_df, self.partnumber_to_product_map)
        chargeable_df = apply_usage_reduction(chargeable_df, itemcount_to_usage_reduction_rules)
        self._write_totals_by_product(chargeable_df)
        SQLGenerator.write_chargeable_sql(chargeable_df, self.output_files_path)
        self._write_error_logs(no_partnumber_error_df, itemcount_nonpositive_error_df)

    def _process_domains(self, df: pd.DataFrame) -> None:
        """Process and output domains data."""
        self._validate_columns(df, ['domains', 'partnerPurchasedPlanID'])
        domains_df = prepare_domains_df(df)
        SQLGenerator.write_domains_sql(domains_df, self.output_files_path)

    def _load_partnumber_to_product_map(self) -> Dict[str, str]:
        """Load the partnumber to product mapping from a JSON file."""
        try:
            with open(self.partnumber_to_product_map_filepath, 'r') as f:
                mapping = json.load(f)
            if not isinstance(mapping, dict):
                raise ValueError("PARTNUMBER_TO_PRODUCT_MAP_FILEPATH is not a dictionary")
            return mapping
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error("Failed to load mapping: %s", e)
            raise RuntimeError(f"Failed to load mapping: {e}")

    def _write_totals_by_product(self, chargeable_df: pd.DataFrame) -> None:
        """
            Write running totals of itemCount per product to CSV.

            Note: the concept of "Running totals" don't match well with the stated problem
            so I took the liberty of changing it to "Totals grouped by Product"
        """
        try:
            totals_by_product_df = chargeable_df[['product', 'itemCount']].copy()
            totals_by_product_df = totals_by_product_df.groupby('product')['itemCount'].sum()
            totals_by_product_df.to_csv(f'{self.output_files_path}/totals_by_product.csv', index=True)

            logger.info("Totals by Product written to %s/totals_by_product.csv", self.output_files_path)
        except Exception as e:
            logger.error("Failed to write totals_by_product: %s", e)
            raise

    def _write_error_logs(
        self,
        no_partnumber_error_df: pd.DataFrame,
        itemcount_nonpositive_error_df: pd.DataFrame
    ) -> None:
        """Write error logs to CSV files."""
        try:
            no_partnumber_error_df.to_csv(f'{self.output_files_path}/no_partnumber_error_df.csv', index=False)
            itemcount_nonpositive_error_df.to_csv(f'{self.output_files_path}/itemcount_nonpositive_error_df.csv', index=False)
            logger.info("Error logs written to %s", self.output_files_path)
        except Exception as e:
            logger.error("Failed to write error logs: %s", e)
            raise

    def _validate_columns(self, df: pd.DataFrame, columns: List[str]) -> None:
        """Validate that required columns exist in the DataFrame."""
        missing = [col for col in columns if col not in df.columns]
        if missing:
            logger.error("Missing required columns: %s", missing)
            raise ValueError(f"Missing required columns: {missing}")