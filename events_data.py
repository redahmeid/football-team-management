from classes import Match, PlayerMatch
import response_classes
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
    TABLE_NAME = "Match_Events"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    MINUTE="Minute"
    DETAIL = "Detail"
    TYPE = "Type"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE if not exists {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{TABLE.MINUTE} int,"\
        f"{TABLE.DETAIL} varchar(255),"\
        f"{TABLE.TYPE} varchar(255),"\
        f"{TABLE.TIME} int,"\
        f"{TABLE.SOFT_DELETE} bool,"\
        f"{TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({TABLE.ID}))"


@fcatimer
async def save_match_event(match_id,player_id,time_playing,type,detail):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                    
                id = id_generator.generate_random_number(5)
            
                insert_query = f"insert INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.MATCH_ID},{TABLE.PLAYER_ID},{TABLE.MINUTE},{TABLE.TYPE},{TABLE.DETAIL}, {TABLE.TIME}) VALUES ('{id}','{match_id}','{player_id}',{time_playing},'{type}','{detail}',{time_playing})"
                
                await cursor.execute(insert_query)
                    
                    # Commit the transaction
                await conn.commit()

                return True


@fcatimer
async def retrieve_match_events(match:response_classes.MatchInfo):
     async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
   
                insert_query = f"select * from {TABLE.TABLE_NAME} inner join {player_data.PLAYER_SEASON_TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{TABLE.PLAYER_ID}={player_data.PLAYER_SEASON_TABLE.TABLE_NAME}.{player_data.PLAYER_SEASON_TABLE.ID} inner join {player_data.TABLE.TABLE_NAME} on {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID}={player_data.PLAYER_SEASON_TABLE.TABLE_NAME}.{player_data.PLAYER_SEASON_TABLE.PLAYER_ID} and {TABLE.TABLE_NAME}.{TABLE.MATCH_ID}={match_id} order by {TABLE.TABLE_NAME}.{TABLE.MINUTE} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"

                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                player_stats = []
                for result in results:
                    player_stats.append(convertToGoalPlayerMatchStats(result,match))
                    
                return player_stats

def convertToGoalPlayerMatchStats(data,match:response_classes.MatchInfo):
    player_info = player_responses.PlayerInfo(id=data[TABLE.PLAYER_ID],name=data[player_data.TABLE.NAME])
    return response_classes.PlayerMatchStat(player=player_info,time=int(data[TABLE.TIME]),minute=int(data[TABLE.TIME]),type=data[TABLE.TYPE],detail=data[TABLE.DETAIL])






        