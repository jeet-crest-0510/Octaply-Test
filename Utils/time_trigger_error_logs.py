from Utils.database_conn import *
from datetime import datetime, timedelta

def time_trigger_error_logs(error_type,errordetail):

    errorlogs = timetriggererrors_collection.find_one({"error_type":error_type,"issolved":False})
    if(errorlogs == None):
        error = [errordetail]
        timetriggererrors_collection.insert_one({
            "error_type": error_type,
            "issolved": False,
            "sendall": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "errordetails": error
            })
    else:
        error = errorlogs.get('errordetails')
        error.append(errordetail)

        timetriggererrors_collection.update_one({"error_type": error_type,"issolved":False},{"$set":{
            "updated_at": datetime.utcnow(),
            "errordetails": error
            }}, upsert=False)
