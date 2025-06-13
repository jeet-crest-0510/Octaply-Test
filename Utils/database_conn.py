from pymongo import MongoClient, UpdateOne
from Utils.constants import mongo_conn
client = MongoClient(mongo_conn)
mydatabase = client['production']

resumedatas=mydatabase['resumedatas']
users=mydatabase['users']
jobapplieds=mydatabase['jobapplieds']
payments=mydatabase['ispayments']
testjobprod=mydatabase['testjobprod']
joblinks=mydatabase['joblinks']
coverletters=mydatabase['coverletters']
glassdoorcache=mydatabase['glassdoorcache']
cookies_collection=mydatabase['cookies']
gd_csrf_token_collection=mydatabase['gd_csrf_tokens']
proxies_collection=mydatabase['proxies']
job_listings_collection=mydatabase['job_listings']
job_queue_collection=mydatabase['job_queues']
payments_collection=mydatabase['ispayments']
triggeremail_collection=mydatabase['triggeremaillogs']
triggercornsetting_collection=mydatabase['triggercornsetting']
timetriggererrors_collection=mydatabase['timetriggererrors']