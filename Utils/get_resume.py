import requests
import json
from Alarms.publish_metric import publish_custom_metric
from Utils.database_queries import *
from Utils.time_trigger_error_logs import *

from dotenv import load_dotenv
import os

load_dotenv(override=True)

resume_url = os.getenv('resume_url')
def get_resume(skills, filename, email):
    payload = json.dumps({
    "email": email,
    "skills": skills
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.post(resume_url, headers=headers, data=payload)

    print(payload)
    print(response.text)

    # correctly handle response
    if response.status_code >= 500:
        update_user_resumefail(email)
        time_trigger_error_logs("resume_fail",{
            "email":email,
            "description":"Issue detected in the resume generation API: resumes were not generated for one or more users.",
            "created_at": datetime.utcnow()
            })
        publish_custom_metric('GlassDoorBotErrors', 'ResumeCreateFailure', 1)
        return False
    elif response.status_code >= 400:
        update_user_resumefail(email)
        time_trigger_error_logs("resume_fail",{
            "email":email,
            "description":"Issue detected in the resume generation API: resumes were not generated for one or more users.",
            "created_at": datetime.utcnow()
            })
        publish_custom_metric('GlassDoorBotErrors', 'ResumeCreateFailure', 1)
        return False
    elif response.status_code >= 300:
        update_user_resumefail(email)
        time_trigger_error_logs("resume_fail",{
            "email":email,
            "description":"Issue detected in the resume generation API: resumes were not generated for one or more users.",
            "created_at": datetime.utcnow()
            })
        publish_custom_metric('GlassDoorBotErrors', 'ResumeCreateFailure', 1)
        return False
    elif response.status_code >= 200:
        print("Resume create Success:")
    print("filename",filename)
    print("Current working directory:", os.getcwd())
    print("Files in directory:", os.listdir())
    print("Resume exists?", os.path.exists(filename))

    with open(filename, "wb+") as file:

        file.write(response.content)
    