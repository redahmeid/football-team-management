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
    OPPOSITION="Opposition"
    TEAM_ID="Team_ID"
    HOME_OR_AWAY="HomeOrAway"
    DATE = "Date"
    STATUS = "Status"
    GOALS_FOR = "Goals_For"
    GOALS_AGAINST = "Goals_Against"
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
        f"{TABLE.LENGTH} int,"\
        f"{TABLE.TYPE} varchar(255),"\
        f"{TABLE.TIME_STARTED} int,"\
        f"PRIMARY KEY ({TABLE.ID}),"\
        f"FOREIGN KEY({TABLE.TEAM_ID}) references Teams({TABLE.ID}))"
    def alterTable():
        return f"ALTER TABLE {TABLE.TABLE_NAME}"\
        f" ADD {TABLE.TYPE} varchar(255)"


@timeit
async def save_team_fixture(match:match_responses.MatchInfo,team_id):
    start_time = datetime.utcnow().timestamp()
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO Matches (ID,Opposition,HomeOrAway, Date,Length,Team_ID,Status,Goals_For,Goals_Against,Type) VALUES ('{id}','{match.opposition}','{match.homeOrAway}','{match.date}','{match.length}','{team_id}','{match.status}',0,0,'{match.type.value}')"
                print(insert_query)
                # Data to be inserted
                
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                end_time = datetime.utcnow().timestamp()-start_time
                logger.info(f"Save team fixtures took {end_time} to finish")
                return id

@timeit
async def retrieve_matches_by_team(team_id:str) -> List[match_responses.MatchInfo]:
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from {TABLE.TABLE_NAME} inner join Teams on {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}=Teams.ID and {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}='{team_id}' order by {TABLE.TABLE_NAME}.{TABLE.DATE} asc" 
                print(insert_query)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                rows = await cursor.fetchall()


                # club = Club(id=id,name=row)
                matches = []
                
                for row in rows:
                    matches.append(convertDataToMatchInfo(row))
                
            
                return matches
@timeit
async def update_match_status(match_id,status)  -> List[match_responses.MatchInfo]:
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
                
@timeit
async def increment_goals_scored(match_id,goals)  -> List[match_responses.MatchInfo]:
    start_time = datetime.utcnow().timestamp()
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"update {TABLE.TABLE_NAME} set {TABLE.GOALS_FOR}={TABLE.GOALS_FOR}+{goals} where {TABLE.ID}='{match_id}'" 
                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
@timeit
async def increment_goals_conceded(match_id,goals)  -> List[match_responses.MatchInfo]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"update {TABLE.TABLE_NAME} set {TABLE.GOALS_AGAINST}={TABLE.GOALS_AGAINST}+{goals} where {TABLE.ID}='{match_id}'" 
                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
@timeit
async def start_match(match_id)  -> List[match_responses.MatchInfo]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"update {TABLE.TABLE_NAME} set {TABLE.STATUS}='{matches_state_machine.MatchState.started.value}', {TABLE.TIME_STARTED}={datetime.utcnow().timestamp()} where {TABLE.ID}='{match_id}'" 
                

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                

@timeit
async def retrieve_match_by_id(id:str) -> List[match_responses.MatchInfo]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from {TABLE.TABLE_NAME} inner join Teams on {TABLE.TABLE_NAME}.{TABLE.TEAM_ID}=Teams.ID and {TABLE.TABLE_NAME}.{TABLE.ID}='{id}'" 
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                rows = await cursor.fetchall()
                print(rows)
                # club = Club(id=id,name=row)
                matches = []
                for row in rows:
                    matches.append(convertDataToMatchInfo(row))
                print(matches)
                return matches
@timeit
async def retrieve_next_match_by_team(team_id:str) -> List[match_responses.MatchInfo]:
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
                
                if(rows is not None): matches.append(convertDataToMatchInfo(rows))
                return matches

def convertDataToMatchInfo(data):
    print(data)
    team_response = convertTeamDataToTeamResponse(data)
    if data.get(TABLE.TIME_STARTED) is not None and data[TABLE.TIME_STARTED] != 0:
        how_long_ago_in_minutes = int((datetime.utcnow().timestamp()-data[TABLE.TIME_STARTED])/60)  
    else:
        how_long_ago_in_minutes = 0
    return match_responses.MatchInfo(id=data[TABLE.ID],team=team_response,status=matches_state_machine.MatchState(data[f'{TABLE.STATUS}']),length=data[TABLE.LENGTH],opposition=data[TABLE.OPPOSITION],homeOrAway=match_responses.HomeOrAway(data[TABLE.HOME_OR_AWAY]),date=data[TABLE.DATE],how_long_ago_started=how_long_ago_in_minutes,time_start=data[TABLE.TIME_STARTED],goals=data[TABLE.GOALS_FOR],conceded=data[TABLE.GOALS_AGAINST])

def convertTeamDataToTeamResponse(team) -> match_responses.TeamResponse:
    
    id = team["Teams.ID"]
    baseTeamUrl = "/teams/%s"%(id)
    name = team["Name"]
    ageGroup = team["AgeGroup"]
    live = team["live"]
    if(live == None):
        live = True
    self = match_responses.Link(link=baseTeamUrl,method="get")
    players = match_responses.Link(link="%s/players"%(baseTeamUrl),method="get")
    fixtures= match_responses.Link(link="%s/matches"%(baseTeamUrl),method="get")
    addPlayers = match_responses.Link(link="%s/players"%(baseTeamUrl),method="post")
    addFixtures = match_responses.Link(link="%s/matches"%(baseTeamUrl),method="post")
    nextMatch = match_responses.Link(link="%s/next_match"%(baseTeamUrl),method="get")

    response =  match_responses.TeamResponse(id=id,name=name,ageGroup=ageGroup,live=live,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    
    return response

if __name__ == "__main__":
  asyncio.run(retrieve_match_by_id(12585))

