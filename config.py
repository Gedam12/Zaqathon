import os
from dotenv import load_dotenv  # Fixed: was "ditenv"

load_dotenv()

# API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # Fixed: missing =

# File paths
CATALOG_PATH = "data/catalog.csv"
SAMPLE_EMAILS_PATH = "data/sample_emails/"

# Processing setup
CONFIDENCE_THRESHOLD = 0.7
MAX_SUGGESTIONS = 3
FUZZY_MATCH_THRESHOLD = 0.8

# Order processing rules
BUNDLE_THRESHOLD_DAYS = 7
DEFAULT_DELIVERY_DAYS = 5