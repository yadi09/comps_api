# app/services/propstream.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import requests
import time
from bot.logger import setup_logger
from config import HEADLESS, LOGIN_URL, USERNAME, PASSWORD, MAX_RETRIES, RETRY_DELAY

logger = setup_logger(__name__)

TARGET_URL = "https://app.propstream.com/eqbackend/resource/auth/ps4/property/comparables"
AUTH_TOKEN_HEADER = "x-auth-token"

def get_property_id(address: str) -> str:
    params = {"q": address}
    resp = requests.get(
        "https://app.propstream.com/eqbackend/resource/auth/ps4/property/suggestionsnew",
        params=params,
    )
    logger.info(f"Requested suggestions for address: {address}, status: {resp.status_code}")
    if resp.status_code != 200:
        logger.error("Failed to fetch property suggestions")
        return None
    data = resp.json()
    # your original code expected exactly 1 result; adjust if desired
    if not data or len(data) != 1:
        logger.error(f"Unexpected suggestions length: {len(data)} for address {address}")
        return None
    return data[0]["id"]

def get_filter_data(address_id: str) -> dict:
    logger.info(f"Starting Playwright process for property id: {address_id}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context()
        page = context.new_page()

        auth_token = None
        payload = None
        raw_data = None

        def on_request(request):
            nonlocal auth_token, payload, raw_data
            try:
                if TARGET_URL in request.url:
                    logger.info(f"Captured request to {request.url}")
                    auth_token = request.headers.get(AUTH_TOKEN_HEADER)
                    try:
                        payload = request.post_data_json
                        logger.info("Captured JSON payload")
                    except Exception:
                        raw_data = request.post_data
                        logger.info("Captured raw payload")
            except Exception as e:
                logger.error(f"Error in on_request: {e}")

        page.on("request", on_request)

        # 1. go to login
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)

        # 2. fill and submit
        page.fill('input[type="text"], input[name="username"], input[type="email"]', USERNAME)
        page.fill('input[type="password"]', PASSWORD)
        page.keyboard.press("Enter")

        # 3. wait for a selector to indicate login success (may need tuning)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                page.wait_for_selector('.src-app-Search-Header-style__CXeKd__row', state='attached', timeout=10000)
                break
            except PlaywrightTimeoutError:
                logger.warning(f"Login wait attempt {attempt} failed - retrying in {RETRY_DELAY}s")
                time.sleep(RETRY_DELAY)

        # navigate to property search URL
        page.goto(f"https://app.propstream.com/search/{address_id}", wait_until="domcontentloaded", timeout=60000)

        # try to close popup if present
        try:
            page.get_by_role("button", name="Proceed").click()
        except Exception:
            pass

        # click comparables tab - adjust name if UI changes
        try:
            page.get_by_role("tab", name="Comparables & Nearby Listings").click()
        except Exception:
            logger.info("Comparables tab click failed (selector may have changed)")

        page.wait_for_load_state("networkidle", timeout=600000)

        # short pause to let the target request fire
        time.sleep(2)

        if not auth_token or (not payload and not raw_data):
            # reload and click again
            logger.info("Retrying to capture request data")
            page.reload(wait_until="domcontentloaded", timeout=90000)
            try:
                time.sleep(10)
                page.get_by_role("tab", name="Comparables & Nearby Listings").click()
            except Exception:
                logger.info("Comparables tab click failed on retry (selector may have changed)")
            page.wait_for_load_state("networkidle", timeout=600000)
            time.sleep(2)

        browser.close()

        if not auth_token:
            logger.error("Auth token not captured")
        if not payload and not raw_data:
            logger.error("Payload not captured")

        return {"Token": auth_token, "Payload": payload or raw_data}

def get_comps_for_address(address: str):
    logger.info(f"Getting comps for: {address}")
    address_id = get_property_id(address)
    if not address_id:
        logger.error("No address id found")
        return None

    data = get_filter_data(address_id)
    if not data or not data.get("Token") or not data.get("Payload"):
        logger.error("Missing token or payload from filter data")
        return None

    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://app.propstream.com',
        'referer': f'https://app.propstream.com/search/{address_id}',
        'user-agent': 'Mozilla/5.0',
        'x-auth-token': data['Token'],
    }

    resp = requests.post(TARGET_URL, headers=headers, json=data['Payload'])
    if resp.status_code == 200:
        return resp.json()
    else:
        logger.error(f"Comps request failed: {resp.status_code} {resp.text}")
        return None
