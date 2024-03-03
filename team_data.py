from classes import Club, Team,UpdateTeam
from config import app_config
import id_generator
import db
import aiomysql
import response_classes
import users_data
import roles
import asyncio
import team_season_data
import match_day_data
import player_data
import matches_data
import player_responses
from typing import List
from timeit import timeit
import logging
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

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
class TABLE:
    ID = "ID"
    NAME="Name"
    AGE_GROUP="AgeGroup"
    LIVE="live"
    TABLE_NAME="Teams"

    def createTable():
        return f"CREATE TABLE if not exists {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.NAME} varchar(255),"\
        f"{TABLE.AGE_GROUP} varchar(255),"\
        f"{TABLE.LIVE} bool,"\
        f"PRIMARY KEY ({TABLE.ID}),)"
   

# "CREATE TABLE Teams" \
#         "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "AgeGroup varchar(255) NOT NULL,"\
#         "Email varchar(255) NOT NULL,"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Club_ID) references Clubs(ID))"
@timeit
async def save_team(team:Team,id):
    print("IN SAVE TEAM ")
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
# Data to be inserted
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.NAME},{TABLE.AGE_GROUP}, {TABLE.LIVE}) VALUES ({id},'{team.name}','{team.age_group}',True)"

                
                data_to_insert = (id,team.name,team.age_group,True)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                # Commit the transaction
                
                print("IN SAVE TEAM %s"%id)
                return id
@timeit
async def delete_team(team_id):
    print("IN DELETE TEAM ")
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
# Data to be inserted
                # Define the SQL query to insert data into a table
                insert_query = f"DELETE FROM {TABLE.TABLE_NAME} where "

                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                # Commit the transaction
                
                print("IN SAVE TEAM %s"%id)
                return id

@timeit
async def retrieve_teams_by_user_id(user_id:str) -> List[response_classes.TeamResponse]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                
                insert_query_2 = f"select * from Roles as r inner join {team_season_data.TABLE.TABLE_NAME} on r.Team_ID={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join {TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}  and r.Email = '{user_id}' and ({team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.DELETE}=False or {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.DELETE} IS NULL) order by {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_AGE_GROUP}, {TABLE.TABLE_NAME}.Name" 
                logger.info(insert_query_2)
                await cursor.execute(insert_query_2)
                rows = await cursor.fetchall()

                teams = [] 
                for row in rows:
                    team = await retrieve_teams_by_user_id_convert_to_team_response(row)
                    teams.append(team)
                return teams
            

@timeit
async def retrieve_users_by_team_id(team_id:str) -> List[response_classes.Admin]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from Roles as r inner join {team_season_data.TABLE.TABLE_NAME} on r.Team_ID = {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join {users_data.TABLE.TABLE_NAME} on r.Email={users_data.TABLE.TABLE_NAME}.{users_data.TABLE.EMAIL} and r.Team_ID={team_id}" 
                logger.info(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
            
                rows = await cursor.fetchall()
                coaches = []
                for row in rows:  
                    user = convertAdminDataToAdminResponse(row)
                    coaches.append(user)
                logger.info(coaches)
                return coaches
@timeit
async def does_userid_match_team(user_id:str,team_id:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from Roles where Team_ID={team_id} and Email = '{user_id}'" 
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
            
                rows = await cursor.fetchall()
                print(rows)
                if(len(rows)>0):
                    return True
                else:
                    return False
                
@timeit
async def retrieve_team_by_id(team_id:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from {team_season_data.TABLE.TABLE_NAME} inner join {TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{TABLE.ID}={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID} and {team_season_data.TABLE.TABLE_NAME}.ID = {team_id} and ({team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.DELETE}=False or {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.DELETE} IS NULL)"  
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                row = await cursor.fetchone()
                
                team = await retrieve_team_by_id_convert_to_team_response(row)
                return team
            
@timeit
async def retrieve_team_assister_stats(team_id:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f" select count(*), {match_day_data.GOALS_TABLE.ASSISTER_ID}, {player_data.TABLE.NAME} from {match_day_data.GOALS_TABLE.TABLE_NAME} inner join {matches_data.TABLE.TABLE_NAME} on {match_day_data.GOALS_TABLE.MATCH_ID}={matches_data.TABLE.TABLE_NAME}.{matches_data.TABLE.ID} inner join {player_data.PLAYER_SEASON_TABLE.TABLE_NAME} on {match_day_data.GOALS_TABLE.ASSISTER_ID}={player_data.PLAYER_SEASON_TABLE.TABLE_NAME}.{player_data.PLAYER_SEASON_TABLE.ID} inner join {player_data.TABLE.TABLE_NAME} on {player_data.PLAYER_SEASON_TABLE.TABLE_NAME}.{player_data.PLAYER_SEASON_TABLE.PLAYER_ID} = {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {matches_data.TABLE.TABLE_NAME}={team_id} group by {match_day_data.GOALS_TABLE.ASSISTER_ID}"  
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                row = await cursor.fetchone()
                
                team = await retrieve_team_by_id_convert_to_team_response(row)
                return team
@timeit
async def retrieve_team_scorer_stats(team_id:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f" select count(*), {match_day_data.GOALS_TABLE.PLAYER_ID}, {player_data.TABLE.NAME} from {match_day_data.GOALS_TABLE.TABLE_NAME} inner join {matches_data.TABLE.TABLE_NAME} on {match_day_data.GOALS_TABLE.MATCH_ID}={matches_data.TABLE.TABLE_NAME}.{matches_data.TABLE.ID} inner join {player_data.PLAYER_SEASON_TABLE.TABLE_NAME} on {match_day_data.GOALS_TABLE.PLAYER_ID}={player_data.PLAYER_SEASON_TABLE.TABLE_NAME}.{player_data.PLAYER_SEASON_TABLE.ID} inner join {player_data.TABLE.TABLE_NAME} on {player_data.PLAYER_SEASON_TABLE.TABLE_NAME}.{player_data.PLAYER_SEASON_TABLE.PLAYER_ID} = {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {matches_data.TABLE.TABLE_NAME}={team_id} group by {match_day_data.GOALS_TABLE.PLAYER_ID}"  
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                row = await cursor.fetchone()
                
                team = await retrieve_team_by_id_convert_to_team_response(row)
                return team




def convertAdminDataToAdminResponse(team) -> response_classes.Admin:
    logger.info(f"ADMIN DATE TO ADMIN RESPONSE {team}")
    role = team["Role"]
    
    email = team["Email"]
    name = team["Name"]
    

    response =  response_classes.Admin(email=email,role=roles.Role(role),name=name)
    print(response)
    return response
if __name__ == "__main__":
  asyncio.run(retrieve_team_by_id("56409"))

async def retrieve_team_by_id_convert_to_team_response(team,order=0) -> response_classes.TeamResponse:
    logger.info(f"{order} TEAM {team}")
    id = team[f"{team_season_data.TABLE.ID}"]
    ageGroup = team[team_season_data.TABLE.TEAM_AGE_GROUP]
    season = team[team_season_data.TABLE.SEASON_NAME]
    season_id = team[f"{team_season_data.TABLE.ID}"]
    name = team[TABLE.NAME]
    team_id = team[f"{team_season_data.TABLE.TEAM_ID}"]
    baseTeamUrl = f"/teams/{season_id}"
    self = response_classes.Link(link=baseTeamUrl,method="get")
    players = response_classes.Link(link="%s/players"%(baseTeamUrl),method="get")
    fixtures= response_classes.Link(link="%s/matches"%(baseTeamUrl),method="get")
    addPlayers = response_classes.Link(link="%s/players"%(baseTeamUrl),method="post")
    addFixtures = response_classes.Link(link="%s/matches"%(baseTeamUrl),method="post")
    nextMatch = response_classes.Link(link="%s/next_match"%(baseTeamUrl),method="get")

    response =  response_classes.TeamResponse(id=id,season=season, team_id=team_id,name=name, season_id=season_id,ageGroup=ageGroup,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    logger.info(f"{order} Response {response}")
    return response

async def retrieve_teams_by_user_id_convert_to_team_response(team,order=0) -> response_classes.TeamResponse:
    logger.info(f"{order} TEAM {team}")
    id = team[f"{team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}"]
    ageGroup = team[team_season_data.TABLE.TEAM_AGE_GROUP]
    season = team[team_season_data.TABLE.SEASON_NAME]
    season_id = team[f"{team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}"]
    name = team["Name"]
    team_id = team[f"{team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}"]
    baseTeamUrl = f"/teams/{season_id}"
    self = response_classes.Link(link=baseTeamUrl,method="get")
    players = response_classes.Link(link="%s/players"%(baseTeamUrl),method="get")
    fixtures= response_classes.Link(link="%s/matches"%(baseTeamUrl),method="get")
    addPlayers = response_classes.Link(link="%s/players"%(baseTeamUrl),method="post")
    addFixtures = response_classes.Link(link="%s/matches"%(baseTeamUrl),method="post")
    nextMatch = response_classes.Link(link="%s/next_match"%(baseTeamUrl),method="get")

    response =  response_classes.TeamResponse(id=id,season=season, team_id=team_id,name=name, season_id=season_id,ageGroup=ageGroup,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    logger.info(f"{order} Response {response}")
    return response