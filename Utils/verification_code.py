import os
import requests
import re
import logging
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

load_dotenv()

logger = logging.getLogger(__name__)

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY") or os.getenv("api_key")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN") or os.getenv("email_domain")


def find_code_from_email(email_text: str):
    code_match = re.search(r"(?i)verification code\s*([\d]{6})", email_text)
    return code_match.group(1) if code_match else None


def get_verification_code(target_email: str) -> str | None:
    """Check the latest 20 emails and return body-plain of the one matching target_email."""
    logging.info(f"Finding code for {target_email}")
    events_url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/events"
    params = {
        "to": target_email,
        "event": "stored",
        "limit": 20,
        "ascending": "no"
    }

    response = requests.get(events_url, auth=HTTPBasicAuth("api", MAILGUN_API_KEY), params=params)
    print(response)
    if response.status_code != 200:
        return None

    items = response.json().get("items", [])
    if not items:
        return None

    for item in items:
        raw_recipient = item.get("message", {}).get("headers", {}).get("to", "")
        recipient = raw_recipient.replace("<", "").replace(">", "").strip().lower()
        if recipient != target_email.strip().lower():
            continue

        storage_url = item.get("storage", {}).get("url")
        if not storage_url:
            continue

        message_response = requests.get(
            storage_url,
            auth=HTTPBasicAuth("api", MAILGUN_API_KEY)
        )
        if message_response.status_code != 200:
            continue
        
        body = message_response.json().get("body-plain")
        if not body:
            continue
        
        code = find_code_from_email(body)
        logging.info(f"Found code: {code}")
        return code

    return None


def check_verification_form(driver):
    input_element = driver.find_element(By.ID, "input-passcode")
    return input_element.is_displayed()


def fill_verification_form(driver, code):
    input_element = driver.find_element(By.ID, "input-passcode")
    input_element.send_keys(code)


def check_invalid_code(driver):
    try:
        error_element = driver.find_element(By.XPATH, "//div[contains(@id, 'ifl-InputFormField-errorTextId')]")
        if error_element is None:
            return False
        return error_element.is_displayed()
    except NoSuchElementException:
        return False


if __name__ == "__main__":
    code = get_verification_code("jeannierose@octa-jobs.com") #For testing purposes
    print(code)