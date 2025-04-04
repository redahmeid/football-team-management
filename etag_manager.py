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
async def whereEqual(collection,field,value):
    db = firestore.client()
    query = db.collection(f"{app_config.db_prefix}_{collection}").where(filter=firestore.FieldFilter(field, '==', value))

        # Get documents matching the query
    docs = query.get() 
    return docs


@fcatimer
async def whereNotIn(collection,field,value):
    db = firestore.client()
    query = db.collection(f"{app_config.db_prefix}_{collection}").where(filter=firestore.FieldFilter(field, 'not in', value))

        # Get documents matching the query
    docs = query.get() 
    return docs


@fcatimer
async def whereIn(collection,field,value):
    db = firestore.client()
    query = db.collection(f"{app_config.db_prefix}_{collection}").where(filter=firestore.FieldFilter(field, 'in', value))

        # Get documents matching the query
    docs = query.get() 
    return docs


@fcatimer
async def whereNotEqual(collection,field,value):
    db = firestore.client()
    query = db.collection(f"{app_config.db_prefix}_{collection}").where(filter=firestore.FieldFilter(field, '!=', value))

        # Get documents matching the query
    docs = query.get() 
    return docs

@fcatimer
async def whereNested(collection,field,value):
    db = firestore.client()
    query = db.collection(f"{app_config.db_prefix}_{collection}").where(field, '==', value)

        # Get documents matching the query
    docs = query.get() 
    return docs

def check_if_collection_exists(collection_name):
    db = firestore.Client()
    try:
        # Attempt to get one document from the collection
        docs = db.collection(collection_name).limit(1).stream()
        for doc in docs:
            return True  # Collection exists if we can iterate over at least one document
        return False  # No documents found, collection does not exist
    except Exception as e:
        print(f'Error checking collection existence: {e}')
        return False

async def whereIDIn(collection, wheres):
    db = firestore.client()
    query = db.collection(f"{app_config.db_prefix}_{collection}")
    all_docs = []  # Empty list to store all matching documents

    for where_clause in wheres:
        field = where_clause['field']
        operator = where_clause['compare']
        value = where_clause['fieldValue']

        # Handle query by document ID
        if field == '__name__':
            # Construct the full document path
            if isinstance(value, list):
                full_doc_paths = [f"{app_config.db_prefix}_{collection}/{doc_id}" for doc_id in value]
            else:
                full_doc_paths = [f"{app_config.db_prefix}_{collection}/{value}"]
            print(full_doc_paths)
                # If value is a single document ID, wrap it in a list
            query = query.where('__name__', 'in', full_doc_paths)
        else:
            # Regular field query
            query = query.where(field, operator, value)

    # Execute the query
    docs = query.stream()
    all_docs.extend(docs)
    
    return all_docs


@fcatimer
async def whereEqualwhere(collection,wheres):
    db = firestore.client()
    
    query = db.collection(f"{app_config.db_prefix}_{collection}")
    all_docs = []  # Empty list to store all matching documents

    
    query = db.collection(f"{app_config.db_prefix}_{collection}")
        # query = query.where(firestore.FieldPath(['field']), where_clause['compare'], where_clause['fieldValue'])
    for where_clause in wheres:
        query = query.where(filter=where_clause)
    
        # Get documents matching the current query
    print(query)
    docs = query.get()
    all_docs.extend(docs)

    
    return all_docs

@fcatimer
async def whereEqualwhereOr(collection,wheres,orWheres):
    db = firestore.client()
    
    query = db.collection(f"{app_config.db_prefix}_{collection}")
    all_docs = []  # Empty list to store all matching documents

    
    query = db.collection(f"{app_config.db_prefix}_{collection}")
        # query = query.where(firestore.FieldPath(['field']), where_clause['compare'], where_clause['fieldValue'])
    for where_clause in wheres:
        query = query.where(filter=where_clause)
    for where_clause in orWheres:
        query = query.orWhere(filter=where_clause)
        # Get documents matching the current query
    print(query)
    docs = query.get()
    all_docs.extend(docs)

    
    return all_docs

@fcatimer
async def whereContains(collection,field,value):
    db = firestore.client()
    query = db.collection(f"{app_config.db_prefix}_{collection}").where(filter=firestore.FieldFilter(field,'array_contains',value))
    print(f"QUERY {query}")
        # Get documents matching the query
    docs = query.get() 
    print(f"DOCS {docs}")
    return docs

@fcatimer
async def updateDocument(collection,id,object):
    db = firestore.client()
    doc_ref = db.collection(f"{app_config.db_prefix}_{collection}").document(id)  # Replace with your collection and document ID
    print(f'UPDATE DOCUMENT - object - {id} {object}')
    if(object):
        if isinstance(object, dict):
            dictObj = object
        else:
            dictObj = object.dict()
        

        versions = dictObj.get('versions',[])
        print(f'UPDATE DOCUMENT - versions - {versions}')
        if(len(versions)>0):
            last_version = versions[len(versions)-1]
        else:
            last_version = None
        print(f'UPDATE DOCUMENT - last_version - {last_version}')
        if(last_version):
            new_version_number = last_version['version']+1
        else:
            new_version_number = 1
        print(f'UPDATE DOCUMENT - new_version_number - {new_version_number}')
        version = {'version':new_version_number,'by':'server_side'}
        versions.append(version)
        dictObj['versions'] = versions
        print(f'UPDATE DOCUMENT - dictObj - {dictObj}')
    

        doc_ref.set(dictObj,merge=True)  

        print(f'Document updated successfully! {collection} {id}')

def is_dictable(obj):
    """
    Check if an object is Dictable.
    """
    return hasattr(obj, '__dict__')

@fcatimer
async def getLatestObject(id,type):
    db = firestore.client()
    
    doc_ref = db.collection(f"{app_config.db_prefix}_{type}").document(id)
    doc = doc_ref.get()
    if doc.exists:
        etag_obj = doc.to_dict()     
        print("ETAG EXISTS")
        return etag_obj
    else:
        return None
    
@fcatimer
async def getObject(id,type):
    db = firestore.client()
    print(f"GET OBJECT {app_config.db_prefix}_{type}")
    doc_ref = db.collection(f"{app_config.db_prefix}_{type}").document(id)
    doc = doc_ref.get()
    if doc.exists:
        
        return doc_ref
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