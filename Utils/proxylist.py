import datetime
from Utils.database_queries import update_proxy_timestamp
from Utils.database_conn import *

def get_proxy():
    pipeline = [
        {"$sample": {"size": 1}}
    ]

    random_record = list(proxies_collection.aggregate(pipeline))[0]
    dt=random_record.get("last_used")
    one_minute_ago = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    ten_hours_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=10)
    status_code=random_record.get("status_code")
    if(status_code==None or status_code<400):
        pass
    elif(status_code>=400 and dt> ten_hours_ago):
        return get_proxy()
    if(dt!=None and dt> one_minute_ago):
        return get_proxy()
    else:
        proxy=random_record.get("proxy")
        update_proxy_timestamp(proxy)
        return proxy