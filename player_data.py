from classes import Club, Team,Player
from config import app_config
import id_generator
import db
import player_responses
from typing import List, Dict
import sys
import aiomysql
import asyncio
# # "CREATE TABLE Players" \
#         "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "Team_ID varchar(255) NOT NULL,"\
#         "Email varchar(255),"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Team_ID) references Teams(ID))"
class TABLE:
    TABLE_NAME = "Players"
    ID = "ID"
    NAME="Name"
    TEAM_ID="Team_ID"
    EMAIL="Email"

    def createTable():
        return f"CREATE TABLE {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.NAME} varchar(255) NOT NULL,"\
        f"{TABLE.TEAM_ID} varchar(255) NOT NULL,"\
        f"{TABLE.EMAIL} int,"\
        f"PRIMARY KEY ({TABLE.ID}),"\
        f"FOREIGN KEY({TABLE.TEAM_ID}) references Teams(ID))"

class PLAYER_SEASON_TABLE:
    TABLE_NAME = "Players_Seasons"
    ID = "ID"
    PLAYER_ID = "Player_ID"
    TEAM_SEASON_ID="Team_Season_ID"

    def createTable():
        return f"CREATE TABLE {PLAYER_SEASON_TABLE.TABLE_NAME}" \
        f"({PLAYER_SEASON_TABLE.ID} varchar(255),"\
        f"{PLAYER_SEASON_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{PLAYER_SEASON_TABLE.TEAM_SEASON_ID} varchar(255) NOT NULL,"\
        f"PRIMARY KEY ({TABLE.ID}))"
        
async def save_player(player:Player):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Data to be inserted
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = "INSERT INTO Players (ID,Name,Team_ID,live) VALUES (%s,%s,'','true')"
                # Define the SQL query to insert data into a table
                
                
                
                data_to_insert = (id,player.name)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                
                await conn.commit()
                
                return id

async def save_player_season(player_id,team_season_id):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Data to be inserted
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO {PLAYER_SEASON_TABLE.TABLE_NAME} ({PLAYER_SEASON_TABLE.ID},{PLAYER_SEASON_TABLE.TEAM_SEASON_ID},{PLAYER_SEASON_TABLE.PLAYER_ID}) VALUES ({id},{team_season_id},{player_id})"
                # Define the SQL query to insert data into a table
                 # Execute the SQL query to insert data
                print(insert_query)
                await cursor.execute(insert_query)
               
                await conn.commit()
                
                return id

async def retrieve_players_by_team(team_id:str) -> List[Dict[str,List[player_responses.PlayerResponse]]]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from Players inner join {PLAYER_SEASON_TABLE.TABLE_NAME} on {PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.PLAYER_ID}={TABLE.TABLE_NAME}.{TABLE.ID} and {PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.TEAM_SEASON_ID} = {team_id} and live <> 'false' or live IS NULL" 
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                
                players = list()
                for result in results:
                    players.append(convertStartingLineup(result))
                
                team_players ={}
                team_players["status"] = "squad"
                team_players["players"] = players
                
                print(team_players)
                return [team_players]

async def squad_size_by_team(team_id:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "select count(*) as count from Players where Team_ID = %s and live <> 'false' or live IS NULL" 
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query,team_id)
                row = await cursor.fetchone()
                
                # club = Club(id=id,name=row)
                print(row)
                return row

async def delete_player(player_id:str):
   async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Define the SQL query to insert data into a table
                insert_query = "update Players set live='false' where ID='%s'" %(player_id)

                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
               
                

async def retrieve_player(id:str) -> List[player_responses.PlayerResponse]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Define the SQL query to insert data into a table
                insert_query = f"select * from Players inner join {PLAYER_SEASON_TABLE.TABLE_NAME} on {PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.PLAYER_ID}={TABLE.TABLE_NAME}.{TABLE.ID} and {PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.ID}={id} and live <> 'false' or live IS NULL" 

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
               
                # club = Club(id=id,name=row)
                print(results)
                players = []
                for result in results:
                    players.append(convertStartingLineup(result))
                return players



def convertStartingLineup(data):
    player_info = player_responses.PlayerInfo(id=data[f'{PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.ID}'],name=data[TABLE.NAME])
    playerResponse = player_responses.PlayerResponse(info=player_info)
    return playerResponse.model_dump()


if __name__ == "__main__":
    if(sys.argv[1]=="retrievePlayers"):
        retrieve_players_by_team(sys.argv[2])
        