from Utils.automation_imports import *
def continue_button(driver):
    success_messages = [
        "Your application has been submitted!",
        "To finish your application, the employer asks",
        "Your application was sent"
    ]
    if any(message in driver.page_source for message in success_messages):
        sleep(1)
        driver.find_element(by=By.TAG_NAME, value="body").send_keys(Keys.ESCAPE)
        return "SUCCESS"
    errorcount=0
    while errorcount<3:
        try:
            continue_buttons = driver.find_elements(By.XPATH, xpaths.get("continue_button"))
            for element in continue_buttons:
                try:
                    # Check if the element is visible and enabled
                    element_text=element.text
                    element.click()
                    break
                except:
                    pass

            if("Submit your application" in element_text):
                sleep(2)
                return "SUCCESS"
            sleep(2)
            return True
        except:
            errorcount+=1
    return False