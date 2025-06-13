# from Utils.automation_imports import *
# def clear_field(element):
#     try:
#         element.click()
#         element.send_keys(Keys.CONTROL + "a")
#         element.send_keys(Keys.DELETE)
#         return True
#     except:
#         return False

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

def clear_field(driver, element, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))
        ActionChains(driver).move_to_element(element).click().perform()
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.DELETE)
        sleep(0.1)  # Allow JavaScript to register the deletion
        return True
    except Exception as e:
        print(f"Failed to clear field: {e}")
        return False
