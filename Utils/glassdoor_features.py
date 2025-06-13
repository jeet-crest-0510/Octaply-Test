import os
from dotenv import load_dotenv
from Utils.database_queries import *
from Utils.mailgun_features import *
from random import randint
from Utils.spawn_driver import start
from Utils.automation_imports import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import random
import string
import re


logger = logging.getLogger(__name__)
load_dotenv(override=True)


import traceback

def get_random_string(length=12, allowed_chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(allowed_chars) for _ in range(length))


def get_glassdoor_user_for_login(key):

	user_detail =  get_user(key)

	if(user_detail != False):

		if(user_detail.get("glassdoorEmail") == None):

			name_count = 0
			names = get_user_by_name(user_detail.get("name"))

			for name in names:
				if(name.get('glassdoorEmail') is not None):
					name_count+=1

			custom_name = re.sub(r'[^A-Za-z]', '', user_detail.get("name"))

			if(name_count == 0):

				list_address = f'{custom_name}@{os.getenv("glassdoor_domain")}'
				glassdoor_address = generate_mailing_list(list_address)

			else:

				list_address = f'{custom_name}{name_count+1}@{os.getenv("glassdoor_domain")}'
				glassdoor_address = generate_mailing_list(list_address)

			if(glassdoor_address == 'Duplicate object'):

				sleep(5)
				check_email = get_user(key)
				if(check_email.get("glassdoorEmail") == None):

					logger.info(f"Duplicate email object found for key:{key}, custom email: {list_address}")
					
					list_address = f'{custom_name}{get_random_string(5)}@{os.getenv("glassdoor_domain")}'
					glassdoor_address = generate_mailing_list(list_address)

					logger.info(f"New email for key:{key}, custom email: {list_address}")

				else:
					return check_email.get("glassdoorEmail"),check_email.get("glassdoorPwd")
					
			password = get_random_string()

			resister_to_glassdoor(glassdoor_address,password)

			update_user_glassdooremail(key,glassdoor_address,password)
			print("NEWWWWW USERRRR")
			return glassdoor_address, password
		else:
			print("User FOUND")
			return user_detail.get("glassdoorEmail"),user_detail.get("glassdoorPwd")
	else:
		logger.info(f"user not found for glassdoor key: {key}")
		return None, None
		
  	
def resister_to_glassdoor(glassdoor_address,password):
	
	galssdoordriver=start()
	galssdoordriver.get('https://www.glassdoor.com/index.htm')

	glassdoor_element("//input[@data-test='emailInput-input']",glassdoor_address,'input',True,galssdoordriver)
	glassdoor_element("//button[@data-test='email-form-button']",None,'button',True,galssdoordriver)
	glassdoor_element("//input[@data-test='passwordInput-input']",password,'input',True,galssdoordriver)
	glassdoor_element("//button[@data-role-variant='primary' and @data-display-social-icon='false' and @aria-live='polite']",None,'button',True,galssdoordriver)

	sleep(5)

	galssdoordriver.quit()


def glassdoor_element(elementpath,elementvalue,elementtype,retry,glassdrive):

	try:
		glassdoorelement = WebDriverWait(glassdrive, 10).until(
			EC.visibility_of_element_located((By.XPATH, elementpath))
			)

		if (elementtype != 'button'):
			glassdoorelement.send_keys(elementvalue)
		else:
			glassdoorelement.click()
			
	except TimeoutException:
		logger.info(f"Retrying for element:: {elementpath}")
		if(retry == True):
			sleep(5)
			glassdoor_element(elementpath,elementvalue,elementtype,False,glassdrive)
		else:
			logger.info(f"Exit from retry")
			exit()
	except Exception as e:
		logger.info(f"Stacktrace: {traceback.print_exc()}")
		logger.info(f"Error in glassdoor_element function:: {e}")
		exit()
