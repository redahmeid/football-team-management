import json
import boto3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from exceptions import AuthError

# Initialize the AWS Secrets Manager client
secretsmanager = boto3.client('secretsmanager')

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
    except ValueError as e:
        print("FIREBASE initalize error %s"%e)
    

        
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
    
def getEmailFromToken(event,context):
    print("GET EMAIL FROM TOKEN")
    id_token = event["headers"]['Authorization'].split('Bearer ')[1]
    if(validate_firebase_id_token(id_token)):
        print("GET EMAIL FROM TOKEN SUCESS")
        return auth.verify_id_token(id_token)["email"]
    else:
        print("GET EMAIL FROM TOKEN ERROR")
        raise AuthError


