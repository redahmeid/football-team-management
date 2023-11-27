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


class PLANNED_LINEUP_TABLE:
    TABLE_NAME = "Planned_Lineups"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    MINUTE="Minute"
    POSITION = "Position"
    NAME="Name"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE if not exists {PLANNED_LINEUP_TABLE.TABLE_NAME}" \
        f"({PLANNED_LINEUP_TABLE.ID} varchar(255),"\
        f"{PLANNED_LINEUP_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{PLANNED_LINEUP_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{PLANNED_LINEUP_TABLE.MINUTE} int,"\
        f"{PLANNED_LINEUP_TABLE.POSITION} varchar(255),"\
        f"{PLANNED_LINEUP_TABLE.TIME} int,"\
        f"{PLANNED_LINEUP_TABLE.SOFT_DELETE} bool,"\
        f"{PLANNED_LINEUP_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({PLANNED_LINEUP_TABLE.ID}),"\
        f"FOREIGN KEY({PLANNED_LINEUP_TABLE.MATCH_ID}) references Matches(ID),"\
        f"FOREIGN KEY({PLANNED_LINEUP_TABLE.PLAYER_ID}) references Players(ID))"

class ACTUAL_LINEDUP_TABLE:
    TABLE_NAME = "Actual_Lineups"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    POSITION = "Position"
    NAME="Name"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE if not exists {ACTUAL_LINEDUP_TABLE.TABLE_NAME}" \
        f"({ACTUAL_LINEDUP_TABLE.ID} varchar(255),"\
        f"{ACTUAL_LINEDUP_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{ACTUAL_LINEDUP_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{ACTUAL_LINEDUP_TABLE.POSITION} varchar(255),"\
        f"{ACTUAL_LINEDUP_TABLE.TIME} int,"\
        f"{ACTUAL_LINEDUP_TABLE.SOFT_DELETE} bool,"\
        f"{ACTUAL_LINEDUP_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({ACTUAL_LINEDUP_TABLE.ID}),"\
        f"FOREIGN KEY({ACTUAL_LINEDUP_TABLE.MATCH_ID}) references Matches(ID),"\
        f"FOREIGN KEY({ACTUAL_LINEDUP_TABLE.PLAYER_ID}) references Players(ID))"

class GOALS_TABLE:
    TABLE_NAME = "Goals"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE if not exists {GOALS_TABLE.TABLE_NAME}" \
        f"({GOALS_TABLE.ID} varchar(255),"\
        f"{GOALS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{GOALS_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{GOALS_TABLE.TIME} int,"\
        f"{GOALS_TABLE.SOFT_DELETE} bool,"\
        f"{GOALS_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({GOALS_TABLE.ID}),"\
        f"FOREIGN KEY({GOALS_TABLE.MATCH_ID}) references Matches(ID),"\
        f"FOREIGN KEY({GOALS_TABLE.PLAYER_ID}) references Players(ID))"

class OPPOSITION_GOALS_TABLE:
    TABLE_NAME = "Opposition_Goals"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_NUMBER="Player_Number"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE if not exists {OPPOSITION_GOALS_TABLE.TABLE_NAME}" \
        f"({OPPOSITION_GOALS_TABLE.ID} varchar(255),"\
        f"{OPPOSITION_GOALS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{OPPOSITION_GOALS_TABLE.TIME} int,"\
        f"{OPPOSITION_GOALS_TABLE.SOFT_DELETE} bool,"\
        f"{OPPOSITION_GOALS_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({OPPOSITION_GOALS_TABLE.ID}),"\
        f"FOREIGN KEY({OPPOSITION_GOALS_TABLE.MATCH_ID}) references Matches(ID))"
    

class ASSISTS_TABLE:
    TABLE_NAME = "Assists"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE if not exists {ASSISTS_TABLE.TABLE_NAME}" \
        f"({ASSISTS_TABLE.ID} varchar(255),"\
        f"{ASSISTS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{ASSISTS_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{ASSISTS_TABLE.TIME} int,"\
        f"{ASSISTS_TABLE.SOFT_DELETE} bool,"\
        f"{ASSISTS_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({ASSISTS_TABLE.ID}),"\
        f"FOREIGN KEY({ASSISTS_TABLE.MATCH_ID}) references Matches(ID),"\
        f"FOREIGN KEY({ASSISTS_TABLE.PLAYER_ID}) references Players(ID))"
    
class PERIODS_TABLE:
    TABLE_NAME = "Periods"
    ID = "ID"
    MATCH_ID="Match_ID"
    STATUS="Status"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE if not exists {PERIODS_TABLE.TABLE_NAME}" \
        f"({PERIODS_TABLE.ID} varchar(255),"\
        f"{PERIODS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{PERIODS_TABLE.STATUS} varchar(255) NOT NULL,"\
        f"{PERIODS_TABLE.TIME} int,"\
        f"{PERIODS_TABLE.SOFT_DELETE} bool,"\
        f"{PERIODS_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({PERIODS_TABLE.ID}),"\
        f"FOREIGN KEY({PERIODS_TABLE.MATCH_ID}) references Matches(ID))"

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

class MATCH_STATUS_TABLE:
    TABLE_NAME="Match_Status"
    ID = "ID"
    MATCH_ID="Match_ID"
    STATUS="Status"
    LINEUP_CHANGE="Lineup_Change"
    

    def createTable():
        return f"CREATE TABLE IF NOT EXISTS {MATCH_STATUS_TABLE.TABLE_NAME} " \
        f"({MATCH_STATUS_TABLE.ID} varchar(255),"\
        f"{MATCH_STATUS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{MATCH_STATUS_TABLE.STATUS} varchar(255) NOT NULL,"\
        f"{MATCH_STATUS_TABLE.LINEUP_CHANGE} int,"\
        f"PRIMARY KEY ({MATCH_STATUS_TABLE.ID}),"\
        f"FOREIGN KEY({MATCH_STATUS_TABLE.MATCH_ID}) references Matches(ID))"

async def retrieve_periods_by_match(match_id) -> List[match_responses.MatchPeriod]:
    print("IN HERE")
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
   
                insert_query = f"select * from {PERIODS_TABLE.TABLE_NAME} where {PERIODS_TABLE.MATCH_ID}={match_id} order by {PERIODS_TABLE.TIME} asc"
                print(insert_query)
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                periods = []
                for result in results:
                    periods.append(convertToPeriods(result))
                
                return periods
async def save_goals_for(match_id,player_id,time_playing):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
        
                id = id_generator.generate_random_number(5)
            
                insert_query = f"insert INTO {GOALS_TABLE.TABLE_NAME} ({GOALS_TABLE.ID},{GOALS_TABLE.MATCH_ID},{GOALS_TABLE.PLAYER_ID}, {GOALS_TABLE.TIME}) VALUES ('{id}','{match_id}','{player_id}',{time_playing})"
                await cursor.execute(insert_query)
                    
                    # Commit the transaction
                await conn.commit()

                return True
@timeit
async def save_assists_for(match_id,player_id,time_playing):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                    
                id = id_generator.generate_random_number(5)
            
                insert_query = f"insert INTO {ASSISTS_TABLE.TABLE_NAME} ({ASSISTS_TABLE.ID},{ASSISTS_TABLE.MATCH_ID},{ASSISTS_TABLE.PLAYER_ID}, {ASSISTS_TABLE.TIME}) VALUES ('{id}','{match_id}','{player_id}',{time_playing})"
                
                await cursor.execute(insert_query)
                    
                    # Commit the transaction
                await conn.commit()

                return True

@timeit
async def update_period(match_id,status):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                    
                id = id_generator.generate_random_number(5)
            
                insert_query = f"insert INTO {PERIODS_TABLE.TABLE_NAME} ({PERIODS_TABLE.ID},{PERIODS_TABLE.MATCH_ID},{PERIODS_TABLE.STATUS}, {PERIODS_TABLE.TIME}) VALUES ('{id}','{match_id}','{status}',{int(datetime.utcnow().timestamp())})"
                print(insert_query)
                await cursor.execute(insert_query)
                    
                    # Commit the transaction
                await conn.commit()

                return True

@timeit
async def retrieve_player_assists(match:match_responses.MatchInfo):
     async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
   
                insert_query = f"select * from {ASSISTS_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {ASSISTS_TABLE.TABLE_NAME}.{ASSISTS_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} where {ASSISTS_TABLE.MATCH_ID}={match.id} order by {ASSISTS_TABLE.TIME} asc"

                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                player_stats = []
                for result in results:
                    player_stats.append(convertToAssistsPlayerMatchStats(result,match))
                
                return player_stats
@timeit
async def retrieve_player_goals(match:match_responses.MatchInfo):
     async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor: 
   
                insert_query = f"select * from {GOALS_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {GOALS_TABLE.TABLE_NAME}.{GOALS_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} where {GOALS_TABLE.MATCH_ID}={match.id} order by {GOALS_TABLE.TIME} asc"

                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                
                player_stats = []
                for result in results:
                    player_stats.append(convertToGoalPlayerMatchStats(result,match))
                    # Commit the transaction

                return player_stats
@timeit
async def retrieve_opposition_goals(match:match_responses.MatchInfo):
     async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
   
                insert_query = f"select * from {OPPOSITION_GOALS_TABLE.TABLE_NAME} where {OPPOSITION_GOALS_TABLE.MATCH_ID}={match.id} order by {OPPOSITION_GOALS_TABLE.TIME} asc"

                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                player_stats = []
                for result in results:
                    player_stats.append(convertToOppositionPlayerMatchStats(result,match))
                    
                return player_stats
async def save_opposition_goal(match_id,time_playing):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
        
                id = id_generator.generate_random_number(5)
            
                insert_query = f"insert INTO {OPPOSITION_GOALS_TABLE.TABLE_NAME} ({OPPOSITION_GOALS_TABLE.ID},{OPPOSITION_GOALS_TABLE.MATCH_ID}, {OPPOSITION_GOALS_TABLE.TIME}) VALUES ('{id}','{match_id}',{time_playing})"
                
                await cursor.execute(insert_query)
                await conn.commit()
                return True

async def save_planned_lineup(match_id,minute,players:List[player_responses.PlayerResponse]):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                for player in players:
                    
                    id = id_generator.generate_random_number(5)
                    
                    #reset the plan
                    delete_query =f"update {PLANNED_LINEUP_TABLE.TABLE_NAME} set {PLANNED_LINEUP_TABLE.SOFT_DELETE}=True, {PLANNED_LINEUP_TABLE.SOFT_DELETE_TIME}={int(datetime.utcnow().timestamp())} where {PLANNED_LINEUP_TABLE.MATCH_ID}='{match_id}' and {PLANNED_LINEUP_TABLE.PLAYER_ID}='{player.info.id}' and {PLANNED_LINEUP_TABLE.MINUTE} >= {minute}"
                    
                    await cursor.execute(delete_query)
                    insert_query = f"insert INTO {PLANNED_LINEUP_TABLE.TABLE_NAME} ({PLANNED_LINEUP_TABLE.ID},{PLANNED_LINEUP_TABLE.MATCH_ID},{PLANNED_LINEUP_TABLE.PLAYER_ID}, {PLANNED_LINEUP_TABLE.MINUTE},{PLANNED_LINEUP_TABLE.POSITION},{PLANNED_LINEUP_TABLE.TIME}) VALUES ('{id}','{match_id}','{player.info.id}',{minute},'{player.selectionInfo.position}',{int(datetime.utcnow().timestamp())})"
                    
                    await cursor.execute(insert_query)
                await conn.commit()
                return True

async def save_actual_lineup(match_id,players:List[player_responses.PlayerResponse],time_playing):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                for player in players:
                    
                    id = id_generator.generate_random_number(5)
                    
                    insert_query = f"insert INTO {ACTUAL_LINEDUP_TABLE.TABLE_NAME} ({ACTUAL_LINEDUP_TABLE.ID},{ACTUAL_LINEDUP_TABLE.MATCH_ID},{ACTUAL_LINEDUP_TABLE.PLAYER_ID}, {ACTUAL_LINEDUP_TABLE.POSITION},{ACTUAL_LINEDUP_TABLE.TIME}) VALUES ('{id}','{match_id}','{player.info.id}','{player.selectionInfo.position}',{time_playing})"
                    print(insert_query)
                    await cursor.execute(insert_query)
                await conn.commit()
                return True

@timeit
async def retrieveAllPlannedLineups(match_id):
    

    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Perform a non-blocking query
                insert_query = f"select * from {PLANNED_LINEUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MATCH_ID}={match_id} and ({PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} IS NULL or {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} != True) order by {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                players = []

                all_lineups = []
                i = 0
                for result in results:
                    player = convertToPlannedStartingLineup(result)
                    
                    if(i==0): minute = player.selectionInfo.minuteOn
                    i+=1
                    if(minute!=player.selectionInfo.minuteOn):
                        all_lineups.append({"status":minute,"players":players})
                        minute=player.selectionInfo.minuteOn
                        players = []
                    players.append(player)
                    if(i+1==len(results)):
                        all_lineups.append({"status":minute,"players":players})
    
    
    
    return all_lineups

@timeit
async def retrieveNextPlanned(match:match_responses.MatchInfo,how_long_ago):
     async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                minutes =how_long_ago
                
                # Define the SQL query to insert data into a table
                insert_query = f"select * from {PLANNED_LINEUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MATCH_ID}={match.id} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE}>{minutes} and ({PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} IS NULL or {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} != True) order by {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                
                players = []
                i = 0
                minute = 0
                for result in results:
                    player = convertToPlannedStartingLineup(result)
                    
                    if(i==0): minute = player.selectionInfo.minuteOn
                    i+=1
                    if(minute!=player.selectionInfo.minuteOn):
                        break
                    players.append(player)
                
                return players
    
@timeit
async def retrieveNextPlannedByMinute(match:match_responses.MatchInfo,minutes):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
   
    
                # Define the SQL query to insert data into a table
                insert_query = f"select * from {PLANNED_LINEUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MATCH_ID}={match.id} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE}>{minutes} and ({PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} IS NULL or {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} != True) order by {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
            

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                
            
                players = []
                i = 0
                minute = 0
                for result in results:
                    player = convertToPlannedStartingLineup(result)
                    
                    if(i==0): minute = player.selectionInfo.minuteOn
                    i+=1
                    if(minute!=player.selectionInfo.minuteOn):
                        break
                    players.append(player)
                
                return players
@timeit
async def retrieveStartingLineup(match_id):
     async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Define the SQL query to insert data into a table
                insert_query = f"select * from {PLANNED_LINEUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MATCH_ID}={match_id} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE}=0 and ({PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} IS NULL or {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} != True) order by {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
           
                players = []
                i = 0
                minute = 0
                for result in results:
                    player = convertToPlannedStartingLineup(result)
                    
                    if(i==0): minute = player.selectionInfo.minuteOn
                    i+=1
                    if(minute!=player.selectionInfo.minuteOn):
                        break
                    players.append(player)
                
                return players
@timeit
async def retrieveCurrentActual(match,how_log_ago):
     async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                minutes = how_log_ago
                
                # Define the SQL query to insert data into a table
                insert_query = f"select * from {ACTUAL_LINEDUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.MATCH_ID}={match.id} and {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.TIME}<={minutes} and ({ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.SOFT_DELETE} IS NULL or {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.SOFT_DELETE} != False) order by {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.TIME} desc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
                # Execute the SQL query to insert data
                print(insert_query)
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                players = []
                i = 0
                minute = 0
                for result in results:
                    player = convertToActualStartingLineup(result)
                    if(i==0): minute = player.selectionInfo.minuteOn
                    i+=1
                    if(minute!=player.selectionInfo.minuteOn):
                        break
                    players.append(player)
                
                return players    

@timeit
async def retrieveAllActualLineups(match_id):
     async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Define the SQL query to insert data into a table
                insert_query = f"select * from {ACTUAL_LINEDUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.MATCH_ID}={match_id} and {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.SOFT_DELETE} <> False order by {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.TIME} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
           
                players = []
                for result in results:
                    players.append(convertToActualStartingLineup(result))
                
                return players





def convertToPlannedStartingLineup(data):
    player_info = player_responses.PlayerInfo(id=data[PLANNED_LINEUP_TABLE.PLAYER_ID],name=data[player_data.TABLE.NAME])
    selection_info = player_responses.SelectionInfo(id=data[PLANNED_LINEUP_TABLE.ID],position=data[PLANNED_LINEUP_TABLE.POSITION],minuteOn=data[PLANNED_LINEUP_TABLE.MINUTE])
    playerResponse = player_responses.PlayerResponse(info=player_info,selectionInfo=selection_info)
    return playerResponse

def convertToActualStartingLineup(data):
    player_info = player_responses.PlayerInfo(id=data[ACTUAL_LINEDUP_TABLE.PLAYER_ID],name=data[player_data.TABLE.NAME])
    selection_info = player_responses.SelectionInfo(id=data[ACTUAL_LINEDUP_TABLE.ID],position=data[ACTUAL_LINEDUP_TABLE.POSITION],minuteOn=int(data[ACTUAL_LINEDUP_TABLE.TIME]))
    playerResponse = player_responses.PlayerResponse(info=player_info,selectionInfo=selection_info)
    return playerResponse

def convertToOppositionPlayerMatchStats(data,match:match_responses.MatchInfo):
    player_info = player_responses.PlayerInfo(id="",name="")
    
    return match_responses.PlayerMatchStat(player=player_info,time=data[OPPOSITION_GOALS_TABLE.TIME])

def convertToGoalPlayerMatchStats(data,match:match_responses.MatchInfo):
    player_info = player_responses.PlayerInfo(id=data[GOALS_TABLE.PLAYER_ID],name=data[player_data.TABLE.NAME])
    
    return match_responses.PlayerMatchStat(player=player_info,time=data[GOALS_TABLE.TIME])

def convertToAssistsPlayerMatchStats(data,match:match_responses.MatchInfo):

    player_info = player_responses.PlayerInfo(id=data[ASSISTS_TABLE.PLAYER_ID],name=data[player_data.TABLE.NAME])
    
    return match_responses.PlayerMatchStat(player=player_info,time=data[ASSISTS_TABLE.TIME])

def convertToPeriods(data):

    period = match_responses.MatchPeriod(status=data[PERIODS_TABLE.STATUS],time=data[PERIODS_TABLE.TIME])
    
    return period
def main():
    return asyncio.run( retrieve_periods_by_match(sys.argv[2]))

if __name__ == "__main__":
    if(sys.argv[1]=="retrieveCurrentActual"): 
        retrieveCurrentActual(sys.argv[2])
    if(sys.argv[1]=="retrieveAllPlannedLineups"):   
        retrieveAllPlannedLineups(sys.argv[2])
    if(sys.argv[1]=="retrieveCurrentActual"): 
        match = asyncio.run(matches_data.retrieve_match_by_id(sys.argv[2]));  
        players = asyncio.run(retrieveCurrentActual(match[0],sys.argv[3]))
        print(len(players))
    if(sys.argv[1]=="retrieveNextPlanned"):  
        retrieveNextPlanned(sys.argv[2])
    if(sys.argv[1]=="stats"):  
        retrieve_player_goals(sys.argv[2])
        retrieve_player_assists(sys.argv[2])
        retrieve_opposition_goals(sys.argv[2])
    if(sys.argv[1]=="periods"):  
        asyncio.run( retrieve_periods_by_match(sys.argv[2]))



        