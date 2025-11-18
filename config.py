# config.py
import os

USERNAME = os.getenv("USERNAME", "shad@reicb.com")
PASSWORD = os.getenv("PASSWORD", "x1FmA8hvaQcN9T@")
LOGIN_URL = os.getenv("LOGIN_URL", "https://app.propstream.com/login")
HEADLESS = os.getenv("HEADLESS", "0") in ("1", "true", "True")

# Playwright timeouts and retry config
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))
