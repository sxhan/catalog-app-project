import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Secret key for signing cookies
SECRET_KEY = "secret"

DB_STRING = 'sqlite:///categoryapp.db'

FB_CLIENT_SECRETS = None

# This is used for the config loading system
REQUIRED_CUSTOM_CONFIGS = ("FB_CLIENT_SECRETS", )
