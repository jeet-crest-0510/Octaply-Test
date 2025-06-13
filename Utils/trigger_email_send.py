import requests
from dotenv import load_dotenv
import os
from Utils.email_json import email_template,email_sub

load_dotenv(override=True)

url = "https://api.mailgun.net/v3/" + os.getenv('email_domain') + "/messages"

def trigger_email(toemail,trigger,username):
    
    data = {
        "from": "Octaply <triggers@octaply.ai>",
        "to": toemail,
        "subject": email_sub[trigger],
        "html": email_template[trigger].replace('{username}',username)
        }

    headers = {"Content-Type": "multipart/form-data"}

    response = requests.post(url, data=data, auth=('api',os.getenv('api_key')))

    data = response.json()