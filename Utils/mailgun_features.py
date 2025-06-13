import requests
import json
from dotenv import load_dotenv
import os
from requests.auth import HTTPBasicAuth

import logging

logger = logging.getLogger(__name__)

load_dotenv(override=True)

def generate_mailing_list(list_address):

	url = f'https://api.mailgun.net/v3/lists'

	# Prepare the data to be sent
	data = {
	    'address': list_address,
	    'description': 'glassdoor user list'
	}

	# Send the POST request
	response = requests.post(url, auth=HTTPBasicAuth('api', os.getenv('api_key')), data=data)

	# Print the response
	if(response.status_code == 400):
		logger.info(f"glassdoor error, Status code: {response.status_code} Response {response.json()}")
		return response.json()['message']
	
	if(response.status_code == 200):
		return response.json()['list']['address']
	else:
		logger.info(f"glassdoor error, Status code: {response.status_code} Response {response.json()}")
		return False