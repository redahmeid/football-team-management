import functools
import time
import asyncio
import hashlib
import json
import firebase_admin
from firebase_admin import credentials, firestore
import api_helper
import datetime

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


@timeit
async def isEtaggged(id,type,etag):
    db = firestore.client()
    print("ETAG EXISTS")
    doc_ref = db.collection(type).document(id)
    doc = doc_ref.get()
    if doc.exists:
        etag_obj = doc.to_dict()
        print(f"ETAG OBJECT {etag_obj}")
        frometag = etag_obj["etag"]
        
        print(f"ETAG EXISTS {etag} and {frometag}")
        return etag_obj["etag"]==etag
    else:
        return False

@timeit
async def getLatestObject(id,type):
    db = firestore.client()
    print("ETAG EXISTS")
    doc_ref = db.collection(type).document(id)
    doc = doc_ref.get()
    if doc.exists:
        etag_obj = doc.to_dict()     
        return etag_obj
    else:
        return None
   
    
    
@timeit
async def deleteEtag(id,type):
    db = firestore.client()
    user = db.collection(type).document(id)
    doc = user.get()

    if doc.exists:
        # Convert Firestore document to Python dictionary
        user.delete()
        # Use the JSON data as needed
    else:
        print("Document not found!")

@timeit
async def setEtag(id,type,object):
    db = firestore.client()
    data = json.dumps(object,default=str).encode("utf-8")
    # Choose a suitable hashing algorithm (e.g., SHA-256)
    hash_object = hashlib.sha256(data)

    # Generate the ETag
    etag = hash_object.hexdigest()

    doc_ref = db.collection(type).document(id)
    doc_ref.set({"etag":etag,"object":json.dumps(object,default=str),"last_updated":firestore.firestore.SERVER_TIMESTAMP})

    return etag

@timeit
async def setEtagList(id,type,object):
    db = firestore.client()
    data = json.dumps(object, default=lambda o: o.dict()).encode()
    # Choose a suitable hashing algorithm (e.g., SHA-256)
    hash_object = hashlib.sha256(data)

    # Generate the ETag
    etag = hash_object.hexdigest()

    doc_ref = db.collection(type).document(id)
    doc_ref.set({"etag":etag,"object":json.dumps(object, default=lambda o: o.dict()),"last_updated":firestore.firestore.SERVER_TIMESTAMP})

    return etag