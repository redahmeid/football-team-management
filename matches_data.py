import classes 
from config import app_config
import id_generator

from firebase_admin import auth
import db
from etag_manager import updateDocument
import response_classes
import match_day_data
import matches_state_machine
from typing import List
from datetime import datetime
import logging
from etag_manager import getObject,updateDocument
import time
from cache_trigger import updateTeamCache, updateMatchCache, updateUserCache
import asyncio
import aiomysql
logger = logging.getLogger(__name__)
import functools
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import team_season_data
import team_response_creator

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
    OPPOSITION="Opposition"
    TEAM_ID="Team_ID"
    HOME_OR_AWAY="HomeOrAway"
    DATE = "Date"
    STATUS = "Status"
    GOALS_FOR = "Goals_For"
    GOALS_AGAINST = "Goals_Against"
    CAPTAIN = "Captain"
    POTM = "POTM"
    LENGTH = "Length"
    TYPE="Type"
    TIME_STARTED = "Time_Started"
    TABLE_NAME="Matches"

    def createTable():
        return f"CREATE TABLE if not exists Matches" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.OPPOSITION} varchar(255) NOT NULL,"\
        f"{TABLE.TEAM_ID} varchar(255) NOT NULL,"\
        f"{TABLE.HOME_OR_AWAY} varchar(255),"\
        f"{TABLE.DATE} datetime,"\
        f"{TABLE.STATUS} varchar(255),"\
        f"{TABLE.GOALS_FOR} int,"\
        f"{TABLE.GOALS_AGAINST} int,"\
        f"{TABLE.CAPTAIN} varchar(255),"\
        f"{TABLE.POTM} varchar(255),"\
        f"{TABLE.LENGTH} int,"\
        f"{TABLE.TYPE} varchar(255),"\
        f"{TABLE.TIME_STARTED} int,"\
        f"PRIMARY KEY ({TABLE.ID}))"
    def alterTable():
        return f"ALTER TABLE {TABLE.TABLE_NAME}"\
        f" ADD {TABLE.POTM} varchar(255)"
   
class PLAYER_RATINGS:
    ID = "ID"
    PLAYER_ID="Player_ID"
    MATCH_ID="Match_ID"
    RATING="Rating"
    TECHNICAL="Technical"
    PHYSICAL="Physical"
    PSYCH="Psychological"
    SOCIAL="Social"
    COMMENTS="Comments"
    POTM = "POTM"
    TABLE_NAME="Player_Ratings"

    def createTable():
        return f"CREATE TABLE if not exists Player_Ratings" \
        f"({PLAYER_RATINGS.ID} varchar(255),"\
        f"{PLAYER_RATINGS.PLAYER_ID} varchar(255),"\
        f"{PLAYER_RATINGS.MATCH_ID} varchar(255),"\
        f"{PLAYER_RATINGS.RATING} varchar(255),"\
        f"{PLAYER_RATINGS.TECHNICAL} varchar(255),"\
        f"{PLAYER_RATINGS.PHYSICAL} varchar(255),"\
        f"{PLAYER_RATINGS.PSYCH} varchar(255),"\
        f"{PLAYER_RATINGS.SOCIAL} varchar(255),"\
        f"{PLAYER_RATINGS.COMMENTS} varchar(255),"\
        f"{PLAYER_RATINGS.POTM} varchar(255),"\
        f"PRIMARY KEY ({TABLE.ID}))"

@fcatimer
async def create_player_ratings(match_id, players:List[dict]):
    start_time = datetime.utcnow().timestamp()
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                for player in players:
                    print(f"CREATE PLAYER RATING {player}")
                    player_id = player["info"]["id"]
                    technical = player["playerRating"]["technical"]
                    physical = player["playerRating"]["physical"]
                    psych = player["playerRating"]["psychological"]
                    social = player["playerRating"]["social"]
                    comments = player["playerRating"]["comments"]
                    rating = (float(technical)+float(physical)+float(psych)+float(social))/4
                    comments = comments.replace("'","''")
                    isPOTM = player["playerRating"]["isPOTM"]
                    # potm = player["player_rating"]["potm"]
                    id = id_generator.generate_random_number(7)


                    # Define the SQL query to insert data into a table
                    delete_rating = f"delete from {PLAYER_RATINGS.TABLE_NAME} where {PLAYER_RATINGS.MATCH_ID}={match_id} and {PLAYER_RATINGS.PLAYER_ID}={player_id}"
                    print(delete_rating)
                    # Data to be inserted
                    
                    # Execute the SQL query to insert data
                    await cursor.execute(delete_rating)
                    await conn.commit()

                    # Define the SQL query to insert data into a table
                    insert_query = f"INSERT INTO {PLAYER_RATINGS.TABLE_NAME} ({PLAYER_RATINGS.ID},{PLAYER_RATINGS.PLAYER_ID},{PLAYER_RATINGS.MATCH_ID},{PLAYER_RATINGS.RATING},{PLAYER_RATINGS.TECHNICAL},{PLAYER_RATINGS.PHYSICAL},{PLAYER_RATINGS.PSYCH},{PLAYER_RATINGS.SOCIAL},{PLAYER_RATINGS.COMMENTS},{PLAYER_RATINGS.POTM}) VALUES ('{id}','{player_id}','{match_id}','{rating}','{technical}','{physical}','{psych}','{social}','{comments}','{isPOTM}')"
                    print(insert_query)
                    # Data to be inserted
                    
                    # Execute the SQL query to insert data
                    await cursor.execute(insert_query)
                    await conn.commit()
                return id

@fcatimer
async def retrieve_player_ratings(match_id):
    start_time = datetime.utcnow().timestamp()
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

               
                # potm = player["player_rating"]["potm"]
                id = id_generator.generate_random_number(7)
                # Define the SQL query to insert data into a table
                insert_query = f"select * from  {PLAYER_RATINGS.TABLE_NAME} where {PLAYER_RATINGS.MATCH_ID}={match_id}"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                rows = await cursor.fetchall()
                return id

@fcatimer
async def save_team_from_cache(match:classes.MatchInfo,team_id):
    start_time = datetime.utcnow().timestamp()
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO Matches (ID,Opposition,HomeOrAway, Date,Length,Team_ID,Status,Goals_For,Goals_Against,Type) VALUES ('{match.id}','{match.opposition}','{match.homeOrAway.value}','{match.date}','{match.length}','{team_id}','{match.status.value}',0,0,'{match.type.value}')"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                end_time = datetime.utcnow().timestamp()-start_time
                logger.info(f"Save team fixtures took {end_time} to finish")
                return id
            

@fcatimer
async def save_team_fixture(match:classes.MatchInfo,team_id):
    start_time = datetime.utcnow().timestamp()
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                id = id_generator.generate_random_number(7)
                location = match.location.replace("'","''")
                opposition = match.opposition.replace("'","''")
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO Matches (ID,Opposition,HomeOrAway, Date,Length,Team_ID,Status,Goals_For,Goals_Against,Type,Location,PlaceId) VALUES ('{id}','{opposition}','{match.homeOrAway.value}','{match.date}','{match.length}','{team_id}','{match.status.value}',0,0,'{match.type.value}','{location}','{match.placeId}')"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                end_time = datetime.utcnow().timestamp()-start_time
                logger.info(f"Save team fixtures took {end_time} to finish")
                return id

@fcatimer
async def set_captain(match:classes.MatchInfo,player_id):
    start_time = datetime.utcnow().timestamp()
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                # Define the SQL query to insert data into a table
                insert_query = f"Update {TABLE.TABLE_NAME} set {TABLE.CAPTAIN}={player_id} where {TABLE.ID}={match.id}"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
                return match.id

@fcatimer
async def set_potm(match:classes.MatchInfo,player_id):
    start_time = datetime.utcnow().timestamp()
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                
                # Define the SQL query to insert data into a table
                insert_query = f"Update {TABLE.TABLE_NAME} set {TABLE.POTM}={player_id} where {TABLE.ID}={match.id}"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
                return match.id

@fcatimer
async def retrieve_matches_by_team(team_id:str) -> List[classes.MatchInfo]:
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from {TABLE.TABLE_NAME} inner join {team_season_data.TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join Teams on {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}=Teams.ID and {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}='{team_id}' and ({TABLE.STATUS} <> 'cancelled' ) order by {TABLE.TABLE_NAME}.{TABLE.DATE} " 
                print(insert_query)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                rows = await cursor.fetchall()


                # club = Club(id=id,name=row)
                matches = []
                
                for row in rows:
                    matches.append(await convertDataToMatchInfo(row))
                
            
                return matches

@fcatimer
async def retrieve_not_played_by_team(team_id:str,offset:str=0) -> List[classes.MatchInfo]:
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from {TABLE.TABLE_NAME} inner join {team_season_data.TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join Teams on {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}=Teams.ID and {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}='{team_id}' and ({TABLE.STATUS} <> 'cancelled' and {TABLE.STATUS} <> 'ended' and {TABLE.STATUS} <> 'rated') order by {TABLE.TABLE_NAME}.{TABLE.DATE} asc limit 10 offset {offset}" 
                print(insert_query)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                rows = await cursor.fetchall()


                # club = Club(id=id,name=row)
                matches = []
                
                for row in rows:
                    matches.append(await convertDataToMatchInfo(row))
                
            
                return matches

@fcatimer
async def retrieve_results_by_team(team_id:str,offset:str=0) -> List[classes.MatchInfo]:
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from {TABLE.TABLE_NAME} inner join {team_season_data.TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join Teams on {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}=Teams.ID and {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}='{team_id}' and ({TABLE.STATUS}  = 'rated' or {TABLE.STATUS}  = 'ended') order by {TABLE.TABLE_NAME}.{TABLE.DATE} desc limit 10 offset {offset}" 
                print(insert_query)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                rows = await cursor.fetchall()


                # club = Club(id=id,name=row)
                matches = []
                
                for row in rows:
                    matches.append(await convertDataToMatchInfo(row))
                
            
                return matches
            

@fcatimer
async def wins_by_team(team_id:str) -> List[classes.MatchInfo]:
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select count(*) as wins from {TABLE.TABLE_NAME} inner join {team_season_data.TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join Teams on {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}=Teams.ID and {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}='{team_id}' and ({TABLE.STATUS}='ended' or {TABLE.STATUS}='rated') and {TABLE.GOALS_FOR}>{TABLE.GOALS_AGAINST} order by {TABLE.TABLE_NAME}.{TABLE.DATE} asc" 
                print(insert_query)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                row = await cursor.fetchone()
                print(row)


                
            
                return row["wins"]

@fcatimer
async def defeats_by_team(team_id:str) -> List[classes.MatchInfo]:
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select count(*) as defeats from {TABLE.TABLE_NAME} inner join {team_season_data.TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join Teams on {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}=Teams.ID and {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}='{team_id}' and ({TABLE.STATUS}='ended' or {TABLE.STATUS}='rated') and {TABLE.GOALS_FOR}<{TABLE.GOALS_AGAINST} order by {TABLE.TABLE_NAME}.{TABLE.DATE} asc" 
                print(insert_query)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                row = await cursor.fetchone()
                print(row)

                
            
                return row["defeats"]

@fcatimer
async def draws_by_team(team_id:str) -> List[classes.MatchInfo]:
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select count(*) as draws from {TABLE.TABLE_NAME} inner join {team_season_data.TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join Teams on {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}=Teams.ID and {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}='{team_id}' and ({TABLE.STATUS}='ended' or {TABLE.STATUS}='rated') and {TABLE.GOALS_FOR}={TABLE.GOALS_AGAINST} order by {TABLE.TABLE_NAME}.{TABLE.DATE} asc" 
                print(insert_query)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                row = await cursor.fetchone()
                print(row)

                
            
                return row["draws"]

@fcatimer
async def updateScore(match_id,goals_for,goals_against):
    fs_match = await getObject(match_id,'matches_store')
    
    fs_match.update({'goals':goals_for,'conceded':goals_against})



@fcatimer
async def update_match_status(match_id,status)  -> List[classes.MatchInfo]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"update {TABLE.TABLE_NAME} set {TABLE.STATUS}='{status}' where {TABLE.ID}='{match_id}'" 
                print(insert_query)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
                
                return await retrieve_match_by_id(match_id)
                
@fcatimer
async def increment_goals_scored(match_id,goals)  -> List[classes.MatchInfo]:
    start_time = datetime.utcnow().timestamp()
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"update {TABLE.TABLE_NAME} set {TABLE.GOALS_FOR}={TABLE.GOALS_FOR}+{goals} where {TABLE.ID}='{match_id}'" 
                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
@fcatimer
async def increment_goals_conceded(match_id,goals)  -> List[classes.MatchInfo]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"update {TABLE.TABLE_NAME} set {TABLE.GOALS_AGAINST}={TABLE.GOALS_AGAINST}+{goals} where {TABLE.ID}='{match_id}'" 
                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
@fcatimer
async def start_match(match_id)  -> List[classes.MatchInfo]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"update {TABLE.TABLE_NAME} set {TABLE.STATUS}='{matches_state_machine.MatchState.started.value}', {TABLE.TIME_STARTED}={datetime.utcnow().timestamp()} where {TABLE.ID}='{match_id}'" 
                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                

@fcatimer
async def retrieve_match_by_id(id:str) -> List[classes.MatchInfo]:
    result = await getObject(id,'matches_store')

    match = classes.MatchInfo(**result.get().to_dict())
                
    return [match]
@fcatimer
async def retrieve_next_match_by_team(team_id:str) -> List[classes.MatchInfo]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from {TABLE.TABLE_NAME} inner join Teams on {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}=Teams.ID and {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}='{team_id}'  and {TABLE.TABLE_NAME}.{TABLE.DATE}>= CURRENT_DATE() order by {TABLE.TABLE_NAME}.{TABLE.DATE} asc" 
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                rows = await cursor.fetchone()

                # club = Club(id=id,name=row)
                matches = []
                
                if(rows is not None): matches.append(await convertDataToMatchInfo(rows))
                return matches

async def convertDataToMatchInfo(data):
    print(data)
    team_response = await team_response_creator.convertTeamSeasonDataToTeamResponse(data)
    if data.get(TABLE.TIME_STARTED) is not None and data[TABLE.TIME_STARTED] != 0:
        how_long_ago_in_minutes = int((datetime.utcnow().timestamp()-data[TABLE.TIME_STARTED])/60)  
    else:
        how_long_ago_in_minutes = 0
    

    match_info = classes.MatchInfo(location=data["Location"],placeId=data["PlaceId"],id=data[TABLE.ID],type=data[TABLE.TYPE],captain=data[TABLE.CAPTAIN], team=team_response,status=matches_state_machine.MatchState(data[TABLE.STATUS]),length=data[TABLE.LENGTH],opposition=data[TABLE.OPPOSITION],homeOrAway=response_classes.HomeOrAway(data[TABLE.HOME_OR_AWAY]),date=data[TABLE.DATE],how_long_ago_started=how_long_ago_in_minutes,time_start=data[TABLE.TIME_STARTED],goals=data[TABLE.GOALS_FOR],conceded=data[TABLE.GOALS_AGAINST])
    
    await updateDocument('matches_new',match_info.id,match_info)
    return match_info


# if __name__ == "__main__":
#   asyncio.run(retrieve_match_by_id(22172))

