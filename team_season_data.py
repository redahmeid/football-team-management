from classes import Match, PlayerMatch
from config import app_config
import id_generator
from firebase_admin import auth
import db
import match_responses

import matches_state_machine
from typing import List
from datetime import datetime
import logging
import time
import asyncio
import aiomysql
logger = logging.getLogger(__name__)
import functools
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import response_classes

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

# "CREATE TABLE Matches" \
#         "(ID varchar(255),"\
#         "Opposition varchar(255) NOT NULL,"\
#         "Team_ID varchar(255) NOT NULL,"\
#         "HomeOrAway varchar(255),"\
#         "Date datetime,"\
#         "Status varchar(255),"\
#         "Goals_For int,"\
#         "Goals_Against int,"\
#         "Length int,"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Team_ID) references Teams(ID))"

class TABLE:
    ID = "ID"
    TEAM_ID="Team_ID"
    TEAM_AGE_GROUP="Age_Group"
    SEASON_NAME="Season_Name"
    TABLE_NAME="Team_Season"

    def createTable():
        return f"CREATE TABLE if not exists {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.TEAM_ID} varchar(255) NOT NULL,"\
        f"{TABLE.SEASON_NAME} varchar(255) NOT NULL,"\
        f"{TABLE.TEAM_AGE_GROUP} varchar(255) NOT NULL,"\
        f"PRIMARY KEY ({TABLE.ID}),"\
        f"FOREIGN KEY({TABLE.TEAM_ID}) references Teams({TABLE.ID}))"
    


@timeit
async def save_team_season(team_id,season_name,age_group):
    
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.TABLE_NAME},{TABLE.TEAM_AGE_GROUP}, {TABLE.SEASON_NAME}) VALUES ('{id}','{team_id}','{age_group}','{season_name}')"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
                return id




