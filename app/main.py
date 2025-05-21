import logging

from app.services.processor import FileProcessor
from app.config.config import (
    OUTPUT_FILES_PATH,
    PARTNUMBER_TO_PRODUCT_MAP_FILEPATH,
    USAGE_REPORT_FILEPATH,
    PARTNER_IDS_TO_SKIP,
    ITEMCOUNT_TO_USAGE_REDUCTION_RULES,
    HEADERS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_processor = FileProcessor(
    output_files_path=OUTPUT_FILES_PATH,
    partnumber_to_product_map_filepath=PARTNUMBER_TO_PRODUCT_MAP_FILEPATH
)

def main() -> None:
    """
    Entry point for the CSV parser and translator.
    """
    logger.info('Initializing the Translator')
    try:
        file_processor.process(
            usage_report_filepath=USAGE_REPORT_FILEPATH,
            partner_ids_to_skip=PARTNER_IDS_TO_SKIP,
            itemcount_to_usage_reduction_rules=ITEMCOUNT_TO_USAGE_REDUCTION_RULES,
            headers=HEADERS
        )
        logger.info('Translation completed successfully.')
    except Exception as e:
        logger.error("Failed to complete translation: %s", e)
        raise

if __name__ == "__main__":
    main()
