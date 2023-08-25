import os
import sys

# Check if we're running as a bundled application
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS  # type: ignore
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Resource paths
RESOURCE_PATH = os.path.join(BASE_DIR, "resources")
ICON_PATH = os.path.join(RESOURCE_PATH, "icons")
CSS_PATH = os.path.join(RESOURCE_PATH, "styles.css")
FONT_PATH = os.path.join(RESOURCE_PATH, "fonts")

# Database configuration
DB_FILENAME = os.path.join(BASE_DIR, "app_data.db")
