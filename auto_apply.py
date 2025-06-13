import asyncio
from Utils.automation_imports import *
from Utils.spawn_driver import start
from Utils.fill_basic_info import fill_basic_info
from Utils.continue_button import continue_button
from Utils.answer_questions import *
from Utils.get_pdf_path import get_pdf_path
from Utils.open_form import open_form
from Utils.database_queries import *
from Utils.proxy_auth import *
from Utils.verification_code import *
from Utils.clear_field import clear_field
from airtop_module.airtop_job_apply import run_airtop_automation
import os, socket, pyvirtualdisplay
import logging
import sys
from Utils.constants import *
from Alarms.publish_metric import publish_custom_metric
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.common.exceptions import TimeoutException
import traceback
from Utils.glassdoor_features import *
from dotenv import load_dotenv
import os
from datetime import datetime


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv(override=True)

ipID=None
job_record = []

# Insert Function
def insert_failed_job(data: dict, client):
    try:
        client = client['production']
        collection = client["failed_auto_jobs"]
        
        # Check for duplicates based on "resume_id" and "job_listing_id"
        existing_entry = collection.find_one({
            "resume_id": data["resume_id"],
            "job_listing_id": data["job_listing_id"]
        })
        
        if not existing_entry:
            result = collection.insert_one(data)
            logger.info(f"Inserted failed job with _id: {result.inserted_id}")
        else:
            logger.info("Duplicate entry detected. Failed job not inserted.")
    except Exception as e:
        logger.error(f"Error inserting failed job to database: {e}")

# Function to log failed job applications to MongoDB
def log_failed_job_to_db(resume_id, jobListingId, client, reason = '', retry_count=0):
    try:
        failed_job_data = {
            "resume_id": ObjectId(resume_id),
            "job_listing_id": jobListingId,
            "failure_reason": f'Airtop Failure - {reason}',
            "failure_timestamp": datetime.utcnow(),
            "retry_count": retry_count,
            "last_retry_timestamp": None,
            "resolved_timestamp": None,
            "status": "pending",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "__v": 0
        }
        insert_failed_job(failed_job_data, client)
    except Exception as e:
        logger.error(f"Error logging failed job to database: {e}")


def auto_apply(driver, jobListingId, resume, cover_letter=None,glassdoor_address=None,password=None):
    try:

        if(glassdoor_address == None):
            logger.info("Glassdoor email not found")
            delete_ip_auth(ipID)
            exit()

        if(password == None):
            logger.info("Glassdoor password not found")
            delete_ip_auth(ipID)
            exit()

        job_record =get_job_url(jobListingId)
        url = job_record.get("seoJobLink")
        # url = "https://whatismyipaddress.com/"

        skills=get_job_skills(jobListingId)
        logger.info(url)

        
        driver.get(url)
        # sleep(80)
        driver.save_screenshot(f"home.png")
        
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            sleep(random.uniform(1.1, 2.0))
        except TimeoutException:
            logger.warning("Page load timed out — body tag not found.")

        pdfpath=get_pdf_path(resume, skills)

        if(pdfpath==False):
            return "Resume Creation failed"
        logger.info("Application start")

        
        original_window = driver.current_window_handle
        
        
        result=open_form(driver,True,glassdoor_address,password) 
        all_windows = driver.window_handles


        if(result!=True):
            return result
        # try:
        #     sleep(5)
        #     WebDriverWait(driver, 10).until(lambda driver: len(driver.window_handles) > 1)
        #     new_tab = [window for window in all_windows if window != original_window][0]
        #     driver.switch_to.window(new_tab)
        # except TimeoutException:
        #     try:
        #         sleep(5)
        #         WebDriverWait(driver, 10).until(lambda driver: len(driver.window_handles) > 1)
        #         new_tab = [window for window in all_windows if window != original_window][0]
        #         driver.switch_to.window(new_tab)
        #     except Exception as e:
        #         logger.info(f"Error in auto_apply() function (TimeoutException):: {e}")
        #         exit()
        # except Exception as e:
        #     logger.info(f"Error in auto_apply() function (Exception):: {e}")
        #     exit()
        sleep(10)
        basic_res = fill_basic_info(driver, resume, glassdoor_address)
        if(basic_res == False):
            driver.save_screenshot(f"fillbasic.png")
            logger.info(f"Basic details filling error")
            delete_ip_auth(ipID)
            exit()

        continue_button(driver)
        driver.save_screenshot(f"continue111.png")
        
        if check_verification_form(driver):
            waiting_time = 20
            retries = 3
            while retries > 0:
                try:
                    sleep(waiting_time)
                    verification_code = get_verification_code(glassdoor_address)
                    fill_verification_form(driver, verification_code)
                    continue_button(driver)
                    sleep(2)
                    if check_invalid_code(driver) == False:
                        logger.info("Verification code accepted")
                        break
                    else:
                        clear_field(driver, driver.find_element(By.ID, "input-passcode"))
                        retries -= 1
                        waiting_time *= 3
                        logger.info(f"Invalid code, waiting {waiting_time} seconds")
                        if retries == 1:
                            waiting_time = 120
                except Exception as e:
                    clear_field(driver, driver.find_element(By.ID, "input-passcode"))
                    retries -= 1
                    waiting_time *= 3
                    logger.info(f"Error while filling verification code: {e}")
                    if retries == 1:
                            waiting_time = 120
                
        # resume_field(driver, pdfpath)
        # continue_button(driver)
        # logger.info("Resume submitted")

        question_list=[]
        isReview = False
        question_log = {}

        loop_run = 0
        
        sleep(3)
        while not isReview:

            loop_run = loop_run + 1
            logger.info(f"loop_run for {loop_run} times")

            current_url=driver.current_url.encode('utf-8').decode('utf-8')
            if("indeedapply/form/review" in current_url):
                res=continue_button(driver)

                if(res=="SUCCESS"):
                    logger.info("Application finished")
                    isReview = True
                    return res
            if("indeedapply/form/resume" in current_url):
                resume_field(driver, pdfpath)
                logger.info("Resume submitted")
                continue_button(driver)

            if("experience" in current_url):
                res=continue_button(driver)
                if(res == False):
                    continue_button_cust = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@data-test='continue-button']"))
                    )
                    continue_button_cust.click()


            questions=driver.find_elements(By.XPATH, xpaths.get("questions"))

            if(loop_run == 100 and len(questions) == 0):
                logger.info(f"Killing the process, URL: {current_url}")
                delete_ip_auth(ipID)
                exit();

            question_count=0
            for question in questions:
                try:
                    print(f"question: {question}")
                    res, question_id=answer_question(resume, question, question_list)
                    print(f"res: {res}, question_id: {question_id}")
                    sleep(random.uniform(2.0,3.5))

                    # Not going further even after answering a question 10 times, quite. Else process will execute forever.
                    if question_id in question_log:
                        question_log[question_id] += 1
                    else:
                        question_log[question_id] = 1

                    # if question_log[question_id] == 10:
                    #     print("baaa")
                    #     return 'indeed error'

                    if(res==True and question_id!=None and question_id not in question_list):
                        question_list.append(question_id)
                except Exception as e:

                    question=driver.find_elements(By.XPATH, xpaths.get("questions"))[question_count]
                    res, question_id=answer_question(resume, question, question_list)
                    if(res==True and question_id!=None and question_id not in question_list):
                        question_list.append(question_id)
                question_count+=1
            if(len(driver.find_elements(By.XPATH, xpaths.get("job_title_input")))):
                work_expierence_field(resume, driver)
            if(len(driver.find_elements(By.XPATH, xpaths.get("cover_letter_input")))):
                write_cover_letter(driver, resume, cover_letter,job_record)
            
            
            res=continue_button(driver)
            

            if(res=="SUCCESS"):
                logger.info("Application finished")
                return res
 
    except KeyboardInterrupt:
        if(ipID != None):
            delete_ip_auth(ipID)

    except Exception as e:

        if(ipID != None):
            delete_ip_auth(ipID)

        logger.info(f"Stacktrace: {traceback.print_exc()}")
        logger.error(f"Task Failed due to errors in auto apply. Job Listing ID: {jobListingId}")
        logger.error(e)
        return e

async def controller(resume_id=None, jobListingId=None, run_count=0, duplicacy_override=False):
    try:
        ipID=create_ip_auth()

        # make sure proxy is properly set
        if(ipID == None):
            delete_all_ip_auths()
            ipID=create_ip_auth()

        if(run_count>1):
            exit()
            # return
        if(os.getenv('environment') == 'prod'):
            display=pyvirtualdisplay.Display(visible=0, size=(1920, 1080))
            display.start()
        logger.info(f"Task start.")

        if(resume_id==None):
            resume_id=os.getenv('resume_id')
            jobListingId=int(os.getenv('jobListingId'))
            if(resume_id==None):
                logger.info(f'Resume_id not passed')
                exit()
                # return

        logger.info(f'Resume_id is: {resume_id}')
        logger.info(f'jobListingId is: {jobListingId}')

        resume=fetch_resume_data(resume_id)

        key=resume.get("key")
        cover_letter=fetch_cover_letter(key)

        if(check_user_validity(key)==False):
            logger.info(f"No payment,Resume_id: {resume_id}, jobListingId: {jobListingId}")

            # raise Exception()
            exit()
            # return
        if(check_job_exists(resume_id, key, jobListingId) and duplicacy_override==False):
            update_queue(resume_id, jobListingId)
            logger.info("Job already applied to.")
            exit()
            # return

        # Glassdoor login
        glassdoor_address, password = get_glassdoor_user_for_login(key)
        logger.info(f"Glassdoor email id: {glassdoor_address}, password: {password}")
        # Glassdoor login

        driver=start()
        res=auto_apply(driver, jobListingId, resume, cover_letter, glassdoor_address,password)

        if(res=="SUCCESS"):
            update_applications(resume_id, jobListingId)
        else:
            if(res==None):
                if(run_count==0):
                    return controller(resume_id, jobListingId, run_count+1)
                publish_custom_metric('GlassDoorBotErrors', 'SeleniumFailures', 1)
                logger.info("SeleniumFailures Trigger published")
            logger.info(f"res: {res}, jobListingId: {jobListingId}")
            update_queue(resume_id, jobListingId)
        delete_ip_auth(ipID)
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
        driver.quit()
        client.close()
        if(os.getenv('environment') == 'prod'):
            display.stop()
        logger.info("Task Finished")
        exit()
        # return
    except KeyboardInterrupt:
        if(ipID != None):
            delete_ip_auth(ipID)
    except Exception as e:

        # delete paroxy ID if any error occured
        if(ipID != None):
            delete_ip_auth(ipID)
        
        logger.info(f"Stacktrace controller : {traceback.print_exc()}")
        logger.info(f"Task Aborted. Error {e}")

        resume=fetch_resume_data(resume_id)

        personal = resume.get("personal_details", {})
        name = personal.get("name", {})
        email=resume.get("personal_details").get("contact").get("email")

        key=resume.get("key")
        glassdoor_address, password = get_glassdoor_user_for_login(key)

        # email = "ahdiuthayakumar@gmail.com"
        # glassdoor_address = "shanemurphy@octa-jobs.com"
        # password = "B0SGHIEv1gR7"
        # glassdoor_address = "wesiv22182@3dboxer.com"
        # password = "wesiv@2182"

        # data = {
        #     "user_email" : "archish.p@crestinfosystems.com",
        #     "email" : "yaxorow999@jio1.com",
        #     "password" : "yaxorow@999",
        #     "first_name" : "test",
        #     "last_name" : "test",
        # }

        # application_success = await run_airtop_automation(jobListingId, data['user_email'], data['email'], data['password'], data['first_name'], data['last_name'], resume)

        application_success, response = await run_airtop_automation(jobListingId, email, glassdoor_address, password, name.get("first"), name.get("last"), resume)

        print(f"application_success: {application_success}, response: {response}")

        if application_success:
            logger.info(f"Application submitted successfully via Airtop for jobListingId: {jobListingId}")
            update_applications(resume_id, jobListingId)
        else:
            logger.info(f"Application failed via Airtop for jobListingId: {jobListingId}")
            log_failed_job_to_db(resume_id, jobListingId, client, response)
            logger.info("AirtopFailures Trigger published")
            update_queue(resume_id, jobListingId)

        client.close()


if __name__ == "__main__":
    if(os.getenv('resume_id') == None and os.getenv('jobListingId') == None):
        ipID=create_ip_auth()
        # make sure proxy is properly set
        if(ipID == None):
            delete_all_ip_auths()
            ipID=create_ip_auth()

        if(os.getenv('environment') == 'prod'):
            display=pyvirtualdisplay.Display(visible=0, size=(1920, 1080))
            display.start()
            
        glassdoor_address, password = get_glassdoor_user_for_login(os.getenv('glassdooremail'))
        logger.info(f"Script generate Glassdoor email id: {glassdoor_address}, password: {password}")
        delete_ip_auth(ipID)
        print('run GlassDoorBotErrors',os.getenv('glassdooremail'))
        exit()
    else:
        asyncio.run(controller())