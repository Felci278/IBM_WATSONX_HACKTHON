import os
from dotenv import load_dotenv
load_dotenv()

class cfg:
    IBM_API_KEY = os.getenv("IBM_API_KEY")
    IBM_PROJECT_ID = os.getenv("IBM_PROJECT_ID")
    IBM_BASE_URL = os.getenv("IBM_BASE_URL", "https://us-south.ml.cloud.ibm.com")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CALENDAR_CREDENTIALS = os.getenv("GOOGLE_CALENDAR_ID", "credentials.json")

    DB_PATH = os.getenv("", "")
    IMAGE_DIR = os.getenv("data", "data/images")
