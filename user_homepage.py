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
def timeit(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def custom_sort(item):
    return int(item["AgeGroup"][1:])

@timeit
async def enter_screen(event, context):
    lambda_handler(event,context)
    headers = event['headers']
    etag = headers.get('etag',None)
    print(f"USER HEADERS {headers}")
    
    db = firestore.client()
    teams_list = []
    try:
        
        email =  getEmailFromToken(event,context)
        if(etag):
            isEtag = await isEtaggged(email,'users',etag)
            if(isEtag):
                response = api_helper.make_api_response_etag(304,result={},etag=etag)
                return response 
            else:
                return await getUserInfoFromDB(email)
        else:
            return await getUserInfoFromDB(email)
        
    except exceptions.AuthError as e:
        response = api_helper.make_api_response(401,None,e)

@timeit
async def enter_screenV2(event, context):
    lambda_handler(event,context)
    headers = event['headers']
    etag = headers.get('etag',None)
    print(f"USER HEADERS {headers}")
    
    db = firestore.client()
    teams_list = []
    try:
        
        email =  getEmailFromToken(event,context)
        if(etag):
            isEtag = await isEtaggged(email,'users_v2',etag)
            if(isEtag):
                response = api_helper.make_api_response_etag(304,result={},etag=etag)
                return response 
            else:
                return await getUserInfoFromDBV2(email)
        else:
            return await getUserInfoFromDBV2(email)
        
    except exceptions.AuthError as e:
        response = api_helper.make_api_response(401,None,e)


