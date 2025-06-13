import socket
import os
from dotenv import load_dotenv

load_dotenv(override=True)

mongo_conn=os.getenv('mongo_conn')

logfolder=os.getenv('logfolder')
PDF_path=os.getenv('PDF_path')

MAX_COOKIE_COUNT=80
MAX_JOB_COUNT=20
MAX_WORKERS=20
FASTAPI_URL="localhost"

OPENAI_API_KEY="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"
DEFAULT_AUTO_APPLY_ID=410

AWS_ACCESS_KEY_ID="AKIA5CJSJLBQ2D2TRPU3"
AWS_SECRET_ACCESS_KEY="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"
WEBSHARE_API_KEY="8kiwthr3bqo6zy132l7vxwpanz0z0l7uiuuihwsz"