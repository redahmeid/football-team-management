import json
import boto3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth, messaging
from exceptions import AuthError

# Initialize the AWS Secrets Manager client
secretsmanager = boto3.client('secretsmanager')
import functools
import time
import asyncio
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

def getToken(event):
    id_token = event["headers"]['Authorization'].split('Bearer ')[1]
    if(validate_firebase_id_token(id_token)):
        
        return auth.verify_id_token(id_token)
    else:
        raise AuthError

from notifications import save_token,save_token_by_match

@timeit
def lambda_handler(event, context):
    
    try:
        # Retrieve the serviceAccountKey.json from Secrets Manager
        secret_name = "dev/firebase"  # Replace with your secret name
        secret = secretsmanager.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(secret['SecretString'])
        
        # Initialize Firebase Admin SDK with the retrieved credentials
        firebase_cred = credentials.Certificate(secret_dict)
        
        app = firebase_admin.initialize_app(credential=firebase_cred)
        print("FIREBASE APP initialized: %s"%app)
        headers = event["headers"]
        pathParameters = event.get("pathParameters")

        # Check if pathParameters is not None and 'match_id' exists as a key
        if pathParameters and "match_id" in pathParameters:
            match_id = pathParameters["match_id"]
            # Proceed with your logic using match_id
        else:
            match_id=""

        print(headers)
        device_token = headers.get('x-device-id',None)
        print(f"DEVICE TOKEN {device_token}")
        try:
            email = getToken(event)["email"]
        except AuthError as e:
            email =""
        loop = asyncio.get_running_loop()  # Get the current loop
        loop.create_task(save_token(email=email,token=device_token))
        print("Token saved")
    except ValueError as e:
        print("FIREBASE initalize error %s"%e)
    

def send_push_notification(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )

    response = messaging.send(message)
    print('Successfully sent message:', response)

@timeit        
def validate_firebase_id_token(id_token):
    try:
        
        decoded_token = auth.verify_id_token(id_token)
        
        print("#####################DECODED TOKEN#####################")
        print(decoded_token)
        # Token is valid; you can access the claims or UID like this:
        uid = decoded_token['uid']
        # Perform your server-side actions here
        return True
    except Exception as e:
        # Token is invalid
        print(f"Error validating token: {e}")
        return False

@timeit        
def delete_firebase_account(event):
    try:
        
        auth.delete_user(getToken(event)['uid'])
        
        return True
    except Exception as e:
        # Token is invalid
        print(f"Error deleting user")
        return False

@timeit
def getEmailFromToken(event,context):
    print("GET EMAIL FROM TOKEN")
    id_token = event["headers"]['Authorization'].split('Bearer ')[1]
    print(f"ID TOKEN = {id_token}")
    if(validate_firebase_id_token(id_token)):
        print("GET EMAIL FROM TOKEN SUCESS")
        return auth.verify_id_token(id_token)["email"]
    else:
        print("GET EMAIL FROM TOKEN ERROR")
        raise AuthError


