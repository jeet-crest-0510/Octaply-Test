from Utils.database_conn import *
import datetime
from bson.objectid import ObjectId
import logging
from Utils.constants import *
from Utils.format_resume import format_resume
logger = logging.getLogger(__name__)

def update_proxy_timestamp(proxy, status_code=""):
    if(type(status_code)==int):
        proxies_collection.update_one({"proxy": proxy}, {"$set": {"last_used": datetime.datetime.utcnow(), "status_code": status_code}}, upsert=False)
    else:
        proxies_collection.update_one({"proxy": proxy}, {"$set": {"last_used": datetime.datetime.utcnow()}}, upsert=False)


def update_job_status(resume_id, jobListingId):
    try:pending_applications=job_queue_collection.find_one({"resume_id": ObjectId(resume_id)}).get("pending_applications")
    except: pending_applications=[]
    temp=[]
    for record in pending_applications:
        temp_jobListingId=record.get("jobListingId")
        if(int(jobListingId)==int(temp_jobListingId)):
            if(record.get("bot_status")=="processed"):
                return True
            record.update({"bot_status": "processing"})
        temp.append(record)
def check_job_exists(resume_id, key, jobListingId):
    jobsApplied_list=jobapplieds.find_one({"key": key})
    if(jobsApplied_list==None):
        return False
    for x in jobsApplied_list.get("jobsApplied"):
        id=x.get("jobListingId")
        if(id!=None):
            if(int(jobListingId) == int(id)):
                return True
    # try:pending_applications=job_queue_collection.find_one({"resume_id": ObjectId(resume_id)}).get("pending_applications")
    # except: pending_applications=[]
    # temp=[]
    # for record in pending_applications:
    #     temp_jobListingId=record.get("jobListingId")
    #     if(int(jobListingId)==int(temp_jobListingId)):
    #         if(record.get("bot_status")=="processing"):
    #             return True
    #         record.update({"bot_status": "processing"})
    #     temp.append(record)
    # job_queue_collection.update_one({"resume_id": ObjectId(resume_id)}, {"$set": {"pending_applications": temp}})
    return False
    
def fetch_resume_data(resume_id):
    resume_id=ObjectId(resume_id)
    resume=resumedatas.find_one({"_id": resume_id})
    resume=format_resume(resume)
    return resume

def fetch_cover_letter(email=""):
    try: 
        cover_letter=coverletters.find_one({"email": email}).get("coverLetter")
    except:
        cover_letter='-'
   
    return cover_letter
def fetch_user_id(resume_id=""):
    resume_id=ObjectId(resume_id)
    try: 
        user_id=resumedatas.find_one({"_id": resume_id}).get("user_id")
    except: user_id=None
    return user_id

def get_job_url(jobListingId):
    record=job_listings_collection.find_one({"jobListingId": int(jobListingId)})
    if(record==None):
        raise Exception("Job Listing not found")
    else:
        return record
    

def get_job_skills(jobListingId):
    record=job_listings_collection.find_one({"jobListingId": int(jobListingId)})
    if(record==None):
        raise Exception("Job Listing not found")
    else:
        return record.get("skills")
    
def update_queue(resume_id, jobListingId):
    try:pending_applications=job_queue_collection.find_one({"resume_id": ObjectId(resume_id)}).get("pending_applications")
    except: pending_applications=[]
    temp=pending_applications
    for record in pending_applications:
        tempjobListingId=record.get("jobListingId")
        if(int(jobListingId)==int(tempjobListingId)):
            temp.remove(record)
            break
    job_queue_collection.update_one({"resume_id": ObjectId(resume_id)}, {"$set": {"pending_applications": temp}})
    
def update_applications(resume_id, jobListingId):
    jobListingId=int(jobListingId)
    key=resumedatas.find_one({"_id": ObjectId(resume_id)}).get("key")
    job_details=job_listings_collection.find_one({"jobListingId": int(jobListingId)})
    companyName=job_details.get("employerNameFromSearch")
    jobTitle=job_details.get("jobTitleText")
    dateApplied=datetime.datetime.utcnow()
    jobListingURL=job_details.get("seoJobLink")
    jobLocation=job_details.get("locationName")
    if(job_details.get("remoteWorkTypes") != None and job_details.get("remoteWorkTypes")[0] =="WORK_FROM_HOME"):
        jobLocation=f"Remote - {jobLocation}"
    temp=[{
        "companyName": companyName,
        "jobTitle": jobTitle,
        "dateApplied": dateApplied, 
        "jobListingURL": jobListingURL,
        "jobListingId": int(jobListingId),
        "jobLocation": jobLocation
    }]
    try:
        old_results=jobapplieds.find_one({"key": key}).get("jobsApplied")
        temp.extend(old_results)
    except:
        pass
    
    jobapplieds.update_one({"key": key}, {"$set": {"jobsApplied": temp, "datetime": datetime.datetime.utcnow()}}, upsert=True)
    update_queue(resume_id, jobListingId)

def check_user_validity(key):

    # frist check if email exist and check other conditions
    paymentCheck = payments_collection.find_one({"email": key})
    if(paymentCheck == None):
        return False

    if(paymentCheck.get("payment")==True):
        resume=resumedatas.find_one({"key":key}, {"key": 1, "botRunStatus": 1, "jobToSearch": 1})
        if(not resume or resume==None):
            return False
        elif(resume.get("botRunStatus")==True and resume.get('jobToSearch') not in ['', None]):
            return True
    return False


# Glassdoor login

def get_user(key):

    user = users.find_one({"email": key})
    if(user == None):
        return False

    return user

def get_user_by_name(name):

    user = users.find({
        'name': {'$regex': name, '$options': 'i'}
        })
    if(user == None):
        return False

    return user

def update_user_glassdooremail(key,glassdoorEmail,password):

    users.update_one({"email": key}, {"$set": {"glassdoorEmail": glassdoorEmail,"glassdoorPwd":password}}, upsert=True)
    return True

def update_user_resumefail(key):

    users.update_one({"email": key}, {"$set": {"resume_fail": True}}, upsert=True)
    return True