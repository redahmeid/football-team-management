from classes import Match, PlayerMatch
import response_classes
from config import app_config
from firebase_admin import credentials, firestore
# Initialize the AWS Secrets Manager client
import traceback
from firebase_admin import auth,messaging
import boto3
import db
import player_responses
import player_data
from typing import List, Dict
import matches_state_machine
from datetime import datetime
import team_data
import matches_data
import sys
import asyncio
import logging
import time
import functools
import aiomysql
import json
import firebase_admin
logger = logging.getLogger(__name__)
import functools
import uuid
from etag_manager import setEtag

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

from fcatimer import fcatimer

# "CREATE TABLE Match_Day_Lineup" \
#         "(ID varchar(255),"\
#         "Match_ID varchar(255) NOT NULL,"\
#         "Player_ID varchar(255) NOT NULL,"\
#         "Subbed_On int,"\
#         "Subbed_Off int,"\
#         "Position varchar(255),"\
#         "PRIMARY KEY (Match_ID,Player_ID,Start_Time_Minutes),"\
#         "FOREIGN KEY(Match_ID) references Matches(ID),"\
#         "FOREIGN KEY(Player_ID) references Players(ID))"


class TABLE:
    TABLE_NAME = "Notifications"
    ID = "ID"
    EMAIL = "EMAIL"
    TOKEN="Token"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    TEAM_ID="Team_ID"
    NOTIFY="Notify"
    DEVICE="Device"
    VERSION="Version"
    TIME="Time"

    def createTable():
        sql = f"CREATE TABLE if not exists {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.EMAIL} varchar(255),"\
        f"{TABLE.MATCH_ID} varchar(255),"\
        f"{TABLE.TOKEN} varchar(255),"\
        f"{TABLE.DEVICE} varchar(255),"\
        f"{TABLE.VERSION} varchar(255),"\
        f"{TABLE.NOTIFY} bool,"\
        f"{TABLE.TIME} int,"\
        f"CONSTRAINT UQ_MATCH UNIQUE ({TABLE.MATCH_ID},{TABLE.TOKEN},{TABLE.DEVICE}),"\
        f"CONSTRAINT UQ_EMAIL UNIQUE ({TABLE.EMAIL},{TABLE.TOKEN},{TABLE.DEVICE}),"\
        f"PRIMARY KEY ({TABLE.ID}))"

        print(sql)
        return sql
    def removeMatchID():
        return f"ALTER TABLE {TABLE.TABLE_NAME}"\
        f" DROP column {TABLE.MATCH_ID}"
    def removePlayerID():
        return f"ALTER TABLE {TABLE.TABLE_NAME}"\
        f" DROP Column {TABLE.PLAYER_ID}"
    def removeTeamID():
        return f"ALTER TABLE {TABLE.TABLE_NAME}"\
        f" DROP Column {TABLE.TEAM_ID}"

class MESSAGES_TABLE:
    TABLE_NAME = "Messages"
    ID = "ID"
    MESSAGE="Message"
    NOTIFICATION_ID="Notification_Id"
    TIME="Time"

    def createTable():
        return f"CREATE TABLE if not exists {MESSAGES_TABLE.TABLE_NAME}" \
        f"({MESSAGES_TABLE.ID} varchar(255),"\
        f"{MESSAGES_TABLE.MESSAGE} varchar(255),"\
        f"{MESSAGES_TABLE.NOTIFICATION_ID} varchar(255),"\
        f"{MESSAGES_TABLE.TIME} int,"\
        f"PRIMARY KEY ({MESSAGES_TABLE.ID}))"
    

@fcatimer
async def save_token(email,token,device,version):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                id = uuid.uuid4()
                select_query = f"select * from {TABLE.TABLE_NAME} where {TABLE.EMAIL}='{email}' and {TABLE.DEVICE}='{device}'"
                await cursor.execute(select_query)
                row = await cursor.fetchall()
                if(len(row)>0):
                    if(row[0][TABLE.TOKEN]==token and row[0][TABLE.VERSION]==version):
                        return True
                    else:
                        insert_query = f"UPDATE {TABLE.TABLE_NAME} set {TABLE.TOKEN}='{token}, {TABLE.VERSION}='{version}' where {TABLE.EMAIL}='{email}' and {TABLE.DEVICE}='{device}'"
                else:
                    insert_query = f"insert INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.EMAIL},{TABLE.TOKEN}, {TABLE.TIME},{TABLE.NOTIFY},{TABLE.DEVICE},{TABLE.VERSION}) VALUES ('{id}','{email}','{token}',{int(datetime.utcnow().timestamp())},True,'{device}','{version}')"
                
                print(insert_query)
                try:
                    await cursor.execute(insert_query)
                    await conn.commit()
                    print("Succesfully saved the token")
                    return True
                except Exception as e:
                    print(e)
                    print("Token already exists")
                    return False
                    
                    # Commit the transaction

@fcatimer
async def turn_off_notifications(token):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                
                
                insert_query = f"update {TABLE.TABLE_NAME} set {TABLE.NOTIFY}=False where {TABLE.TOKEN}='{token}'"
                print(insert_query)
                try:
                    await cursor.execute(insert_query)
                    await conn.commit()
                    print("Succesfully saved the token")
                    return True
                except Exception as e:
                    print(e)
                    print("Token already exists")
                    return False
                    
                    # Commit the transaction




@fcatimer
async def delete_token(email,token):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                id = uuid.uuid4()
                select_query = f"delete  from {TABLE.TABLE_NAME} where {TABLE.EMAIL}='{email}' and {TABLE.TOKEN}='{token}'"
                await cursor.execute(select_query)
                row = await cursor.fetchall()

                if(len(row)>0):
                    return
                
                insert_query = f"insert INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.EMAIL},{TABLE.TOKEN}, {TABLE.TIME}) VALUES ('{id}','{email}','{token}',{int(datetime.utcnow().timestamp())})"
                
                try:
                    await cursor.execute(insert_query)
                    await conn.commit()
                    print("Succesfully saved the token")
                    return True
                except Exception as e:
                    print(e)
                    print("Token already exists")
                    return False
                    
                    # Commit the transaction
                

@fcatimer
async def save_token_by_match(match_id,token):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                id = uuid.uuid4()
                select_query = f"delete from {TABLE.TABLE_NAME} where {TABLE.MATCH_ID}='{match_id}' and {TABLE.TOKEN}='{token}'"
                await cursor.execute(select_query)

                insert_query = f"insert INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.MATCH_ID},{TABLE.TOKEN}, {TABLE.TIME},{TABLE.NOTIFY}) VALUES ('{id}','{match_id}','{token}',{int(datetime.utcnow().timestamp())},True)"
                print(insert_query)
                try:
                    await cursor.execute(insert_query)
                    await conn.commit()
                    print("Succesfully saved the token")
                    return True
                except Exception as e:
                    print(e)
                    print("Token already exists")
                    return False
                    
                    # Commit the transaction
                

@fcatimer
async def save_message(notification_id,message):
    await setEtag(notification_id,'notifications',message)

async def getDeviceToken(email):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                id = uuid.uuid4()
            
                insert_query = f"select {TABLE.TOKEN} from {TABLE.TABLE_NAME} where {TABLE.EMAIL}='{email}' and {TABLE.NOTIFY}=True"

                print(insert_query)
                await cursor.execute(insert_query)
                    
                row = await cursor.fetchall()


                logger.info("Succesfully saved the token")
                return row
            
@fcatimer
async def getDeviceTokenByMatchOnly(match_id):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                id = uuid.uuid4()
            
                insert_query = f"select {TABLE.TOKEN} from {TABLE.TABLE_NAME} where {TABLE.MATCH_ID}='{match_id}' and {TABLE.EMAIL} IS NULL and {TABLE.NOTIFY}=True"

                print(insert_query)
                await cursor.execute(insert_query)
                    
                row = await cursor.fetchall()


                logger.info("Succesfully saved the token")
                return row


@fcatimer
async def sendNotificationUpdatesLink(match_id,message,subject,type,data):
    secretsmanager = boto3.client('secretsmanager')
    event = {
        "type":type,
        "id":match_id,
        "message":message,
        "subject":subject,
        "data":data
    }
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
    FunctionName=app_config.send_notifications,  # Name of the target Lambda
    InvocationType='Event',
    Payload=json.dumps(event)  # Asynchronous invocation
    ) 

@fcatimer
async def sendNotificationUpdates(match_id,message,subject,type):
    secretsmanager = boto3.client('secretsmanager')
    event = {
        "type":type,
        "id":match_id,
        "message":message,
        "subject":subject,
    }
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
    FunctionName=app_config.send_notifications,  # Name of the target Lambda
    InvocationType='Event',
    Payload=json.dumps(event)  # Asynchronous invocation
    ) 

@fcatimer
async def backgroundSendMatchUpdateNotification(event,context):
    secretsmanager = boto3.client('secretsmanager')
    try:
        # Retrieve the serviceAccountKey.json from Secrets Manager
        secret_name = "dev/firebase"  # Replace with your secret name
        secret = secretsmanager.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(secret['SecretString'])
        
        # Initialize Firebase Admin SDK with the retrieved credentials
        firebase_cred = credentials.Certificate(secret_dict)
        
        app = firebase_admin.initialize_app(credential=firebase_cred)
        print("FIREBASE APP initialized: %s"%app)
    except Exception as e:
        print(e)


    id = event["id"]
    message = event["message"]
    subject = event["subject"]
    type = event["type"]
    data = event.get("data",None)
    if(data is None):
        data = {
            "id":id
        }
    silent = data.get("silent",'False')
    if(type=='match'):
        for user in await getStakeholders(id):

            tokens = await getDeviceToken(user.email)
            for token in tokens:
                new_token = token["Token"]
                if(silent=="True"):
                    await send_push_message(new_token,subject,message,data)
                else:
                    await send_push_notification(new_token,subject,message,data)
        
        tokens = await getDeviceTokenByMatchOnly(id)

        for token in tokens:
            new_token = token["Token"]
            if(silent=="True"):
                await send_push_message(new_token,subject,message,data)
            else:
                await send_push_notification(new_token,subject,message,data)
    elif(type=='team'):
        tokens = await getDeviceToken(id)
        for token in tokens:
            new_token = token["Token"]
            if(silent=="True"):
                await send_push_message(new_token,subject,message,data)
            else:
                await send_push_notification(new_token,subject,message,data)
    if(type=='admins'):
        for user in await getStakeholders(id):
            tokens = await getDeviceToken(user.email)
            for token in tokens:
                new_token = token["Token"]
                if(silent=="True"):
                    await send_push_message(new_token,subject,message,data)
                else:
                    await send_push_notification(new_token,subject,message,data)
        
        

        
async def getStakeholders(match_id):
    matches = await matches_data.retrieve_match_by_id(match_id)

    match = matches[0]
    print(f"MATCH {match}")
    team_id = match.team.id
    print(f"TEAM ID {team_id}")
    admins = await team_data.retrieve_users_by_team_id(team_id)
    unique_objects = {obj.email: obj for obj in admins}.values()
    return list(unique_objects)

@fcatimer     
async def send_push_notification(token, title, body,data):
    secretsmanager = boto3.client('secretsmanager')
    print(data)
    message = messaging.Message(
        
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        data = data
    )

    print(f"MESSAGE {message}")
    print(f"DATA {data}")
    print(f"MESSAGE {message}")
    print(f"BODY {body}")
    try:
        response = messaging.send(message)
        print(f"Sent to {token}")
        await save_message(token,body)
    except firebase_admin._messaging_utils.UnregisteredError as e:
        print(f"Token is invalid or unregistered: {e}")
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        print(f"Exception is {e}")
    

async def send_push_message(token, title, body,data):
    secretsmanager = boto3.client('secretsmanager')
    print(f"Sent to {token}")
    message = messaging.Message(
        token=token,
        data = data
    )
    try:
        messaging.send(message)
        await save_message(token,body)
    except firebase_admin._messaging_utils.UnregisteredError as e:
        print(f"Token is invalid or unregistered: {e}")
    except Exception as e:
        traceback.print_exception(*sys.exc_info()) 
        print(f"Exception is {e}")
    
    
    

