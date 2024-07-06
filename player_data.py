from classes import  Team,Player
from config import app_config
import id_generator
import classes
import db
import player_responses
from typing import List, Dict
import sys
import aiomysql
import functools
import time
import asyncio
from fcatimer import fcatimer

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
        return f"CREATE TABLE if not exists {PLAYER_SEASON_TABLE.TABLE_NAME}" \
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
                insert_query = "INSERT INTO Players (ID,Name,Surname,Team_ID,live) VALUES (%s,%s,%s,'','true')"
                # Define the SQL query to insert data into a table
                
                
                
                data_to_insert = (id,player.forename,player.surname)
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
@fcatimer
async def retrieve_players_by_team_with_stats(team_id:str) -> List[Dict[str,List[classes.Player]]]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "SELECT "\
                                "Players.ID, "\
                                "Players.Name, Players.Surname, Players.Shortname, "\
                                "Players_Seasons.ID,  Players_Seasons.Team_Season_ID, "\
                                "GROUP_CONCAT(DISTINCT Roles.Email SEPARATOR ', ') AS Guardians, "\
                                "SUM(DISTINCT CASE WHEN Player_Ratings.POTM = 'TRUE' THEN 1 ELSE 0 END) AS POTM_Count, "\
                                "COALESCE(COUNT(DISTINCT CASE WHEN Goals.Player_ID = Players_Seasons.ID THEN Goals.ID END),0) AS GoalCount, "\
                                "COALESCE(COUNT(DISTINCT CASE WHEN Goals.Assister_ID = Players_Seasons.ID THEN Goals.ID END),0) AS AssistCount, "\
                                 "COALESCE(AVG(Player_Ratings.Rating),0) AS AverageRating, "\
                                 "COALESCE(AVG(Player_Ratings.Technical),0) AS AverageTech, "\
                                 "COALESCE(AVG(Player_Ratings.Physical),0) AS AveragePhys, "\
                                 "COALESCE(AVG(Player_Ratings.Psychological),0) AS AveragePsych, "\
                                 "COALESCE(AVG(Player_Ratings.Social),0) AS AverageSocial "\
                            "FROM Players "\
                            "INNER JOIN Players_Seasons ON Players_Seasons.Player_ID = Players.ID "\
                                f"AND Players_Seasons.Team_Season_ID = {team_id} "\
                            "LEFT JOIN Goals ON Goals.Player_ID = Players_Seasons.ID "\
                               "OR Goals.Assister_ID = Players_Seasons.ID "\
                            "LEFT JOIN Player_Ratings ON Player_Ratings.Player_ID = Players_Seasons.ID "\
                            "LEFT JOIN Roles ON Roles.Player_ID = Players_Seasons.ID "\
                            "GROUP BY Players_Seasons.ID, Players.Name "\
                            "ORDER BY GoalCount DESC"
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                
                players = list()

                for result in results:
                    player_response = convertPlayerWithStats(result)
                    players.append(player_response)
                
                team_players ={}
                team_players["status"] = "squad"
                team_players["players"] = players
                
                print(team_players)
                return [team_players]


            
@fcatimer
async def retrieve_players_by_team_no_stats(team_id:str) -> List[Dict[str,List[classes.Player]]]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "SELECT "\
                                "Players.ID, "\
                                "Players.Name, Players.Surname, Players.Shortname, "\
                                "Players_Seasons.ID,  Players_Seasons.Team_Season_ID "\
                            "FROM Players "\
                            "INNER JOIN Players_Seasons ON Players_Seasons.Player_ID = Players.ID "\
                                f"AND Players_Seasons.Team_Season_ID = {team_id} "
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                
                players = list()

                for result in results:
                    player_response = convertPlayerNoStats(result)
                    players.append(player_response)
                
                team_players ={}
                team_players["status"] = "squad"
                team_players["players"] = players
                
                print(team_players)
                return [team_players]

@fcatimer
async def retrieve_players_by_user(email:str) -> List[Dict[str,List[classes.Player]]]:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "SELECT "\
                                "Players.ID, "\
                                "Players.Name, Players.Surname, Players.Shortname, "\
                                "Players_Seasons.ID, Players_Seasons.Team_Season_ID, "\
                                "GROUP_CONCAT(DISTINCT Roles.Email SEPARATOR ', ') AS Guardians, "\
                                "SUM(DISTINCT CASE WHEN Player_Ratings.POTM = 'TRUE' THEN 1 ELSE 0 END) AS POTM_Count, "\
                                "COALESCE(COUNT(DISTINCT CASE WHEN Goals.Player_ID = Players_Seasons.ID THEN Goals.ID END),0) AS GoalCount, "\
                                "COALESCE(COUNT(DISTINCT CASE WHEN Goals.Assister_ID = Players_Seasons.ID THEN Goals.ID END),0) AS AssistCount, "\
                                "COALESCE(AVG(Player_Ratings.Rating),0) AS AverageRating, "\
                                "COALESCE(AVG(Player_Ratings.Technical),0) AS AverageTech, "\
                                "COALESCE(AVG(Player_Ratings.Physical),0) AS AveragePhys, "\
                                "COALESCE(AVG(Player_Ratings.Psychological),0) AS AveragePsych, "\
                                "COALESCE(AVG(Player_Ratings.Social),0) AS AverageSocial "\
                                "FROM Players INNER JOIN Players_Seasons ON Players_Seasons.Player_ID = Players.ID "\
                                "LEFT JOIN Goals ON Goals.Player_ID = Players_Seasons.ID OR Goals.Assister_ID = Players_Seasons.ID "\
                                "LEFT JOIN Player_Ratings ON Player_Ratings.Player_ID = Players_Seasons.ID "\
                                f"INNER JOIN Roles ON Roles.Player_ID = Players_Seasons.ID and Roles.Email='{email}' "\
                                "GROUP BY Players_Seasons.ID, Players.Name, Players_Seasons.Team_Season_ID  ORDER BY GoalCount DESC;"
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                results = await cursor.fetchall()
                
                players = list()

                for result in results:
                    player_response = convertPlayerWithStats(result)
                    players.append(player_response)
                
                return players

            

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
               
                

async def retrieve_player(id:str) -> List[classes.Player]:
    
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Define the SQL query to insert data into a table
                insert_query = f"select * from Players inner join {PLAYER_SEASON_TABLE.TABLE_NAME} on {PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.PLAYER_ID}={TABLE.TABLE_NAME}.{TABLE.ID} and {PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.ID}='{id}' and live <> 'false' or live IS NULL" 
                print(insert_query)
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


    player_info = classes.PlayerInfo(id=data[f'{PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.ID}'],name=data[TABLE.NAME],forename=data[TABLE.NAME],surname=data["Surname"],shortname=data["Shortname"],team_id=data['Team_Season_ID'])
    playerResponse = classes.Player(info=player_info)
    return playerResponse.model_dump()
def convertPlayerWithStats(data):
    player_info = classes.PlayerInfo(id=data[f'{PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.ID}'],name=data[TABLE.NAME],forename=data[TABLE.NAME],surname=data["Surname"],shortname=data["Shortname"],team_id=data["Team_Season_ID"])
    player_stats = classes.PlayerStats(goals=data["GoalCount"],assists=data["AssistCount"],rating=round(data["AverageRating"],ndigits=2),potms=data["POTM_Count"])
    player_rating = classes.PlayerRating(overall=str(round(data["AverageRating"],ndigits=2)),technical=str(round(data["AverageTech"],ndigits=2)),physical=str(round(data["AveragePhys"],ndigits=2)),psychological=str(round(data["AveragePsych"],ndigits=2)),social=str(round(data["AverageSocial"],ndigits=2)))
    guardians = []
    if(data['Guardians']):
        guardians = data['Guardians'].split(',')
    playerResponse = classes.Player(info=player_info,stats=player_stats,rating=player_rating,guardians=guardians)
    return playerResponse.model_dump()

def convertPlayerNoStats(data):
    player_info = classes.PlayerInfo(id=data[f'{PLAYER_SEASON_TABLE.TABLE_NAME}.{PLAYER_SEASON_TABLE.ID}'],name=data[TABLE.NAME],forename=data[TABLE.NAME],surname=data["Surname"],shortname=data["Shortname"],team_id=data["Team_Season_ID"])
    guardians = []
    
    playerResponse = classes.Player(info=player_info)
    return playerResponse.model_dump()


if __name__ == "__main__":
    if(sys.argv[1]=="retrievePlayers"):
        retrieve_players_by_team_with_stats(sys.argv[2])
        