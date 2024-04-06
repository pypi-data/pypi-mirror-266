##Path C:\Users\jamig\OneDrive\Desktop\botwrap\openaiwrapper\config.py

import os
from dotenv import load_dotenv

# Load environment variables from a .env file for local development
# This line is optional if you're setting environment variables through other means in production
load_dotenv()

# Base configuration
class Config:
    API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = "https://api.openai.com/v1"
    TOOLS = {
        "code_interpreter": {
            "enabled": True,
            "config_key": "example_value"
        }
    }

# Development configuration
class DevelopmentConfig(Config):
    DEBUG = True
    # Development specific configurations can go here

# Production configuration
class ProductionConfig(Config):
    DEBUG = False
    # Production specific configurations can go here

# Staging configuration
class StagingConfig(Config):
    DEBUG = False
    # Staging specific configurations can go here

# Determine which configuration to use based on an environment variable
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development').lower()
if ENVIRONMENT == 'production':
    CurrentConfig = ProductionConfig
elif ENVIRONMENT == 'staging':
    CurrentConfig = StagingConfig
else:
    CurrentConfig = DevelopmentConfig

# Usage example in your application
# from config import CurrentConfig
# api_key = CurrentConfig.API_KEY

