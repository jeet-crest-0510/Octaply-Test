from Utils.constants import PDF_path
import logging
from Utils.get_resume import get_resume
logger = logging.getLogger(__name__)

import os
def get_pdf_path(resume, skills):
    first_name=resume.get("personal_details").get("name").get("first")
    last_name=resume.get("personal_details").get("name").get("last")
    email=resume.get("personal_details").get("contact").get("email")
    file_name=f"{first_name}_{last_name}_Resume.pdf"

    # set path separator correctly based on OS
    res = get_resume(skills, os.path.join(os.getcwd(), file_name), email)

    if(res == False):
        return False

    return os.path.join(os.getcwd(), file_name)