
from config import app_config
import id_generator
from firebase_admin import auth
import db
import roles_data
import logging
import time
import asyncio
import aiomysql
logger = logging.getLogger(__name__)
import functools
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fcatimer(func):
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



class TABLE:
    ID = "ID"
    CLUB_NAME="Club_Name"
    TABLE_NAME="Clubs"

    def createTable():
        return f"CREATE TABLE if not exists {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.CLUB_NAME} varchar(255) NOT NULL,"\
        f"PRIMARY KEY ({TABLE.ID}))"

class ClUB_TEAM_TABLE:
    ID = "ID"
    TEAM_ID="Team_ID"
    CLUB_ID="Club_ID"
    TABLE_NAME="Clubs_Teams"

    def createTable():
        return f"CREATE TABLE if not exists {ClUB_TEAM_TABLE.TABLE_NAME}" \
        f"({ClUB_TEAM_TABLE.ID} varchar(255),"\
        f"{ClUB_TEAM_TABLE.CLUB_ID} varchar(255) NOT NULL,"\
        f"{ClUB_TEAM_TABLE.TEAM_ID} varchar(255) NOT NULL,"\
        f"PRIMARY KEY ({TABLE.ID}))"


@fcatimer
async def save_club(club_name):
    
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO {TABLE.TABLE_NAME} ({TABLE.ID}, {TABLE.CLUB_NAME}) VALUES ('{id}','{club_name}')"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
                return id

@fcatimer
async def add_team_to_club(club_id,team_id):
    
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO {ClUB_TEAM_TABLE.TABLE_NAME} ({ClUB_TEAM_TABLE.ID}, {ClUB_TEAM_TABLE.CLUB_ID}, {ClUB_TEAM_TABLE.TEAM_ID}) VALUES ('{id}','{club_id}','{team_id}')"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
                return id

@fcatimer
async def retrieve_clubs_by_user_id(user_id):
    
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = f"select * from {TABLE.TABLE_NAME} inner join {roles_data.TABLE.TABLE_NAME} on {TABLE.CLUB_ID}={roles_data.TABLE.TABLE_NAME}.{roles_data.TABLE.CLUB_ID} and {roles_data.TABLE.TABLE_NAME}.{roles_data.TABLE.EMAIL}={user_id}"
                print(insert_query)
                
                cursor.execute(insert_query)
                rows = cursor.fetchall()
                
                return id

@fcatimer
async def retrieve_seasons_by_team_id(team_id):
    
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = f"select * from {TABLE.TABLE_NAME} where {TABLE.TEAM_ID}={team_id}"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                rows = cursor.fetchall()
                
                return rows


# def convertAdminDataToAdminResponse(team) -> response_classes.ClubResponse:
#     print(team)
#     club_name = team[TABLE.CLUB_NAME]
#     id = team[TABLE.ID]
    

#     response =  response_classes.ClubResponse(name=club_name,id=id)
#     print(response)
#     return response