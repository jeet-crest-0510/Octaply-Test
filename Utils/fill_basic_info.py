from Utils.automation_imports import *
from Utils.clear_field import clear_field
from Utils.xpaths import xpaths
import unicodedata
import re

import random
from time import sleep

import traceback

def fill_phone_number(driver, country, phone_number):   
    try:
        phone_code_xpath = xpaths.get("phone_num_code")
        phone_field_xpath = xpaths.get("phone_num_field")

        phone_num_code = driver.find_elements(by=By.XPATH, value=phone_code_xpath)
        if not phone_num_code:
            return True

        phone_num_code[0].click()
        sleep(random.uniform(1.4, 1.7))
        phone_num_code[0].send_keys(country.replace('US', 'United States (+1)'))

        phone_num_field = driver.find_elements(by=By.XPATH, value=phone_field_xpath)
        if phone_num_field:
            sleep(random.uniform(0.4, 0.7))
            clear_field(driver, phone_num_field[0])
            # type_string(phone_num_field[0], phone_number[:10])
            type_string(phone_num_field[0], "2345678900")
            return True

    except Exception as e:
        print(f"fill_phone_number error: {e}")
        return False
    
    
# def fill_basic_text_field(driver, field_name, text):
#     try:
#         ele_xpath = f'//input[@data-testid="{field_name}"]'
#         element = driver.find_element(by=By.XPATH, value=ele_xpath)
#         if clear_field(driver, element):
#             type_string(element, text)
#             sleep(random.uniform(0.3, 0.6))  # Added delay after typing
#             return True
#     except Exception as e:
#         print(f"fill_basic_text_field error: {e}")
#         return False

def clean_string(value):
    if not value:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    elif not isinstance(value, str):
        value = str(value)

    # Normalize Unicode (NFKC) and remove weird characters
    normalized = unicodedata.normalize('NFKC', value)
    
    # Remove non-ASCII characters
    cleaned = re.sub(r'[^\x20-\x7E]', '', normalized)
    
    return cleaned.strip()


def debug_string(label, value):
    print(f"{label}:")
    print(f"  Raw: {value}")
    print(f"  Repr: {repr(value)}")
    print(f"  Bytes: {list(value.encode('utf-8', errors='ignore'))}")


def fill_basic_text_field(driver, field_id, value):
    try:
        field = driver.find_element(By.ID, field_id)
        field.clear()
        debug_string(f"[{field_id}] cleaned input", value)

        field.send_keys(value)
        return True
    except Exception as e:
        print(f"Failed to fill {field_id}: {e}")
        return False


def fill_basic_info(driver, resume, glassdoor_address):
    personal = resume.get("personal_details", {})
    name = personal.get("name", {})
    contact = personal.get("contact", {})

    basic_data = {
        "input-firstName": clean_string(name.get("first")),
        "input-lastName": clean_string(name.get("last")),
        "phoneNumber": clean_string(contact.get("phone")),
        "input-email": clean_string(glassdoor_address),
        "country": clean_string(contact.get("phone_number_country")),
    }

    print("Cleaned first name:", basic_data["input-firstName"])
    print("Cleaned last name:", basic_data["input-lastName"])
    print("Cleaned email:", basic_data["input-email"])
    print("Cleaned phone:", basic_data["phoneNumber"])

    fields_to_fill = ["input-firstName", "input-lastName", "phoneNumber", "input-email"]

    for attempt in range(10):
        try:
            print(f"Attempt {attempt + 1}/10 to fill basic info...")

            for field in fields_to_fill:
                if field == "phoneNumber":
                    if not fill_phone_number(driver, basic_data["country"], basic_data["phoneNumber"]):
                        raise Exception("Failed to fill phone number")
                else:
                    if not fill_basic_text_field(driver, field, basic_data.get(field)):
                        raise Exception(f"Failed to fill {field}")
                sleep(random.uniform(0.3, 0.8))  # Small delay to simulate real typing

            return True
        except Exception as e:
            print(f"fill_basic_info retry error: {e}")
            sleep(random.uniform(0.8, 1.2))  # Delay before retry
    return False