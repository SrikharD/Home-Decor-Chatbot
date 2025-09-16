"""
Configuration settings for Home Decor Chatbot
"""
import os
from dotenv import load_dotenv

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'home-decor-chatbot')

# Bedrock Configuration
BEDROCK_MODEL_ID = "meta.llama3-70b-instruct-v1:0"
BEDROCK_REGION = AWS_REGION

# Application Configuration
APP_TITLE = "Home Decor Assistant"
APP_ICON = "🏠"
DEFAULT_PORT = 8501

# Response Configuration
MAX_RESPONSE_LENGTH = 1000
RESPONSE_TEMPERATURE = 0.7
RESPONSE_TOP_P = 0.9
RESPONSE_DELAY_SECONDS = 7

# Search Configuration
MAX_SEARCH_RESULTS = 5
SEARCH_BOOST_CATEGORY = 10
SEARCH_BOOST_ROOM = 8
