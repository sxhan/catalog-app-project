import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Secret key for signing cookies
SECRET_KEY = "secret"

DB_STRING = 'sqlite:///categoryapp.db'

FB_CLIENT_SECRETS = {
    "web": {
        "app_id": "1293669250698238",
        "app_secret": "d56adf9a6e289490202f3edf4ff4e5b0"
    }
}
