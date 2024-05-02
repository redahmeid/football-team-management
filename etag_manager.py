import functools

import time
import asyncio
import hashlib
import json
import firebase_admin
from firebase_admin import credentials, firestore
import api_helper
import datetime
from config import app_config
from fcatimer import fcatimer


@fcatimer
async def isEtaggged(id,type,etag):
    db = firestore.client()
    print("ETAG EXISTS")
    doc_ref = db.collection(f"{app_config.db_prefix}_{type}").document(id)
    doc = doc_ref.get()
    if doc.exists:
        etag_obj = doc.to_dict()
        print(f"ETAG OBJECT {etag_obj}")
        frometag = etag_obj["etag"]
        
        print(f"ETAG EXISTS {etag} and {frometag}")
        return etag_obj["etag"]==etag
    else:
        return False
def date_to_timestamp(date_obj):
    unix_epoch = datetime.date(1970, 1, 1)
    timestamp = (date_obj - unix_epoch).total_seconds()
    return int(timestamp)

def serialize(obj):
    if isinstance(obj, datetime.date):
        return date_to_timestamp(obj)
    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    else:
        return obj
    
@fcatimer
async def updateDocument(collection,id,object):
    db = firestore.client()
    doc_ref = db.collection(f"{app_config.db_prefix}_{collection}").document(id)  # Replace with your collection and document ID

# Update the document with matchInfo data
    doc_ref.set(serialize(object.dict()),merge=True)  # Update using dictionary from object

    print('Document updated successfully!')

@fcatimer
async def getLatestObject(id,type):
    db = firestore.client()
    print("ETAG EXISTS")
    doc_ref = db.collection(f"{app_config.db_prefix}_{type}").document(id)
    doc = doc_ref.get()
    if doc.exists:
        etag_obj = doc.to_dict()     
        return etag_obj
    else:
        return None
   

@fcatimer
async def getAllObjects(type):
    db = firestore.client()
    print("ETAG EXISTS")
    doc_ref = db.collection(f"{app_config.db_prefix}_{type}")
    # Get all documents in the collection
    docs = doc_ref.stream()
    objects = []
    # Iterate over the documents and print the data
    for doc in docs:
        objects.append( doc.to_dict())
    return objects
    
    
    
@fcatimer
async def deleteEtag(id,type):
    db = firestore.client()
    user = db.collection(f"{app_config.db_prefix}_{type}").document(id)
    doc = user.get()

    if doc.exists:
        # Convert Firestore document to Python dictionary
        user.delete()
        # Use the JSON data as needed
    else:
        print("Document not found!")

@fcatimer
async def setEtag(id,type,object):
    db = firestore.client()
    data = json.dumps(object,default=str).encode("utf-8")
    # Choose a suitable hashing algorithm (e.g., SHA-256)
    hash_object = hashlib.sha256(data)

    # Generate the ETag
    etag = hash_object.hexdigest()

    doc_ref = db.collection(f"{app_config.db_prefix}_{type}").document(id)
    doc_ref.set({"etag":etag,"object":json.dumps(object,default=str),"last_updated":firestore.firestore.SERVER_TIMESTAMP})

    return etag

@fcatimer
async def setEtagList(id,type,object):
    db = firestore.client()
    data = json.dumps(object, default=lambda o: o.dict()).encode()
    # Choose a suitable hashing algorithm (e.g., SHA-256)
    hash_object = hashlib.sha256(data)

    # Generate the ETag
    etag = hash_object.hexdigest()

    doc_ref = db.collection(f"{app_config.db_prefix}_{type}").document(id)
    doc_ref.set({"etag":etag,"object":json.dumps(object, default=lambda o: o.dict()),"last_updated":firestore.firestore.SERVER_TIMESTAMP})

    return etag