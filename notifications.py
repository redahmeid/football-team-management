from classes import Match, PlayerMatch
import response_classes
from config import app_config
import id_generator
from firebase_admin import auth,messaging

import db
import player_responses
import player_data
from typing import List, Dict
import matches_state_machine
from datetime import datetime
import matches_data
import sys
import asyncio
import logging
import time
import functools
import aiomysql
import firebase_admin
logger = logging.getLogger(__name__)
import functools
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

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
    TIME="Time"

    def createTable():
        return f"CREATE TABLE if not exists {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.EMAIL} varchar(255),"\
        f"{TABLE.MATCH_ID} varchar(255),"\
        f"{TABLE.TOKEN} varchar(255),"\
        f"{TABLE.TIME} int,"\
        f"CONSTRAINT UQ_MATCH UNIQUE ({TABLE.MATCH_ID},{TABLE.TOKEN}),"\
        f"PRIMARY KEY ({TABLE.ID}))"
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
    

@timeit
async def save_token(email,token,match_id):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                id = id_generator.generate_random_number(5)
            
                insert_query = f"insert INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.EMAIL},{TABLE.MATCH_ID},{TABLE.TOKEN}, {TABLE.TIME}) VALUES ('{id}','{email}','{match_id}','{token}',{int(datetime.utcnow().timestamp())})"
                
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
                

@timeit
async def save_message(notification_id,message):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                id = id_generator.generate_random_number(5)
            
                insert_query = f"insert INTO {MESSAGES_TABLE.TABLE_NAME} ({MESSAGES_TABLE.ID},{MESSAGES_TABLE.MESSAGE},{MESSAGES_TABLE.NOTIFICATION_ID}, {MESSAGES_TABLE.TIME}) VALUES ('{id}','{message}','{notification_id}',{int(datetime.utcnow().timestamp())})"
                await cursor.execute(insert_query)
                    
                    # Commit the transaction
                await conn.commit()
                logger.info("Message successfulll saved")
                return True

@timeit
async def getDeviceToken(email):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                id = id_generator.generate_random_number(5)
            
                insert_query = f"select {TABLE.TOKEN} from {TABLE.TABLE_NAME} where {TABLE.EMAIL}='{email}'"

                print(insert_query)
                await cursor.execute(insert_query)
                    
                row = await cursor.fetchall()


                logger.info("Succesfully saved the token")
                return row


            
async def send_push_notification(token, title, body,action,link):
    message = messaging.Message(
        
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
        data={
            "action": action,
            "link":link
        }
    )
    try:
        response = messaging.send(message)
    except firebase_admin._messaging_utils.UnregisteredError as e:
        print(f"Token is invalid or unregistered: {e}")
    except Exception as e:
        print(f"Exception is {e}")
    await save_message(token,body)
    
    

