import sys
import logging
from app.main import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.basicConfig(level=logging.ERROR)
        logging.error("An error occurred during execution: %s", e)
        sys.exit(1)