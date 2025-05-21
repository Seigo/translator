import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def require_env_var(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None or value.strip() == "":
        raise ValueError(f"Environment variable '{var_name}' is required but not set.")
    return value

OUTPUT_FILES_PATH = require_env_var("OUTPUT_FILES_PATH")
PARTNUMBER_TO_PRODUCT_MAP_FILEPATH = require_env_var("PARTNUMBER_TO_PRODUCT_MAP_FILEPATH")
USAGE_REPORT_FILEPATH = require_env_var("USAGE_REPORT_FILEPATH")
PARTNER_IDS_TO_SKIP = [int(x) for x in os.getenv("PARTNER_IDS_TO_SKIP", "26392").split(",")]
HEADERS = os.getenv("HEADERS", "PartnerID,accountGuid,domains,plan,PartNumber,itemCount").split(",")

try:
    ITEMCOUNT_TO_USAGE_REDUCTION_RULES = json.loads(
        os.getenv(
            "ITEMCOUNT_TO_USAGE_REDUCTION_RULES",
            '{"EA000001GB0O": 1000, "PMQ00005GB0R": 5000, "SSX006NR": 1000, "SPQ00001MB0R": 2000}'
        )
    )
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON for ITEMCOUNT_TO_USAGE_REDUCTION_RULES: {e}")