from Utils.automation_imports import *
import logging

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import traceback
from time import sleep

logger = logging.getLogger(__name__)

def open_form(driver, retry=True,glassdoor_address=None,password=None):  
    sleep(8) 
    
    error_count=0
    while error_count<1:
        try:
            if(len(driver.find_elements(by=By.XPATH, value="//span[@id='expired-job-notice_Description']"))):
                if("no longer available" in driver.find_element(by=By.XPATH, value="//span[@id='expired-job-notice_Description']").text):
                    print(driver.find_element(by=By.XPATH, value="//span[@id='expired-job-notice_Description']").text)
                    return "Job listing has expired"
            
            try:
                apply_button=driver.find_element(by=By.XPATH, value='//*[@id="app-navigation"]/div[3]/div/div[1]/div/div[1]/div/header/div[1]/div[2]/div[2]/div/div/button')
            except NoSuchElementException:
                driver.save_screenshot(f"debug_screenshot_{error_count}.png")
                return "Easy Apply option unavailable"

            apply_button.click()

            # Add auto login functionality for "Easy apply" feature
            email_input = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="modalUserEmail"]'))
                )
            logger.info(f"glassdoor_address in open_form: {glassdoor_address}")
            email_input.send_keys(glassdoor_address)
            driver.save_screenshot(f"em.png")
            email_continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-test='continue-with-email-modal']"))
            )
            email_continue_button.click()
            
            password_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@data-test='passwordInput-input']"))
            )
            print("password",password)
            ppassword=password
            sleep(2)
            driver.save_screenshot(f"ps1.png")
            password_element.send_keys(ppassword)
            driver.save_screenshot(f"ps.png")

            sign_in_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//form[@name='authEmailForm']//div[contains(@class, 'emailButton')]//button"))
                )
            driver.save_screenshot(f"sign_in_button.png")
            sign_in_button.click()
            driver.save_screenshot(f"click.png")
            error_count+=1
            
            sleep(5)
            
            if len(driver.window_handles) > 1:
                driver.save_screenshot("click1.png")
                
                # Store window handles
                all_windows = driver.window_handles
                first_window = all_windows[0]
                last_window = all_windows[-1]
                
                # Switch to first window and take screenshot
                driver.switch_to.window(first_window)
                driver.save_screenshot("click2.png")
                
                # Switch to last window and take screenshot
                driver.switch_to.window(last_window)
                driver.save_screenshot("click4.png")
                
                # # Close the first window (we're currently on the last window)
                # driver.switch_to.window(first_window)
                # driver.close()
                
                # # Switch back to the remaining window and take final screenshot
                # remaining_windows = driver.window_handles
                # if remaining_windows:
                #     driver.switch_to.window(remaining_windows[0])
                #     driver.save_screenshot("click3.png")
                
            return True
        except Exception as e:
            logger.info(f"Error in open_form: {e}")
            sleep(1)
            error_count+=1
    if(retry==True):
        try:
            driver.refresh()
            return open_form(driver, False,glassdoor_address,password)
        except Exception as e:
            logger.info(f"Error in open_form (driver.refresh): {e}")
    return True
            