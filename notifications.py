from classes import Match, PlayerMatch
import match_responses
from config import app_config
import id_generator
from firebase_admin import auth
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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        f"{TABLE.TOKEN} varchar(255) NOT NULL,"\
        f"{TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{TABLE.TEAM_ID} varchar(255),"\
        f"{TABLE.TIME} int,"\
        f"PRIMARY KEY ({TABLE.ID}))"


@timeit
async def save_token(email,match_id,player_id,team_id,token):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
    
        
                id = id_generator.generate_random_number(5)
            
                insert_query = f"insert INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.EMAIL},{TABLE.TOKEN},{TABLE.MATCH_ID},{TABLE.PLAYER_ID},{TABLE.TEAM_ID}, {TABLE.TIME}) VALUES ('{id}','{email}','{token}','{match_id}','{player_id}','{team_id}',{int(datetime.utcnow().timestamp())})"
                await cursor.execute(insert_query)
                    
                    # Commit the transaction
                await conn.commit()

                return True
