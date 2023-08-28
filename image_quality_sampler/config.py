import os
import sys

# For determining user-specific data directory
import appdirs

# Check if we're running as a bundled application
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS  # type: ignore
    # Determine user-specific data directory for the bundled app
    APP_NAME = "AMS Capture"
    APP_AUTHOR = "Quality Control Module"
    USER_DATA_DIR = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    USER_DATA_DIR = BASE_DIR

# Ensure that the user-specific data directory exists
os.makedirs(USER_DATA_DIR, exist_ok=True)

# Resource paths
RESOURCE_PATH = os.path.join(BASE_DIR, "resources")
ICON_PATH = os.path.join(RESOURCE_PATH, "icons")
CSS_PATH = os.path.join(RESOURCE_PATH, "styles.css")
FONT_PATH = os.path.join(RESOURCE_PATH, "fonts")

# Database configuration
DB_FILENAME = os.path.join(USER_DATA_DIR, "app_data.db")
