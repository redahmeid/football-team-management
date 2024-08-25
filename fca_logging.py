import exceptions

from secrets_util import getEmailFromToken, lambda_handler
import api_helper

from user_homepage_backend import getUserInfoFromDBV2,getUserInfoFromDB
import functools
import time
import asyncio
import hashlib
import json
import firebase_admin
from firebase_admin import credentials, firestore
from etag_manager import isEtaggged,setEtag
from fcatimer import fcatimer


@fcatimer
async def log(event,context):
    await lambda_handler(event,context)

    email = getEmailFromToken(event,context)
    headers = event["headers"]
    device_token = headers.get('x-device-token',None)
    device_id = headers.get('x-device-id',None)
    version = headers.get('x-football-app',None)
    body =json.loads(event["body"])
    action = event["pathParameters"]["event"]
    print(f"##################{email} - {action} #######################")
    print(f"DEVICE ID: {device_id} VERSION: {version}")
    print(body)
    print(f"##################{email} - {action} #######################")


@fcatimer
async def error(event,context):
    await lambda_handler(event,context)

    email = getEmailFromToken(event,context)
    headers = event["headers"]
    device_token = headers.get('x-device-token',None)
    device_id = headers.get('x-device-id',None)
    version = headers.get('x-football-app',None)
    body =json.loads(event["body"])
    action = event["pathParameters"]["event"]
    print(f"##################{email} - {action} #######################")
    print(f"DEVICE ID: {device_id} VERSION: {version}")
    print(body)
    print(f"##################{email} - {action} #######################")