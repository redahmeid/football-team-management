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
from typing import List

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

async def save_team(team:Team):
    print("IN SAVE TEAM ")
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
# Data to be inserted
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.NAME},{TABLE.AGE_GROUP}, {TABLE.LIVE}) VALUES ({id},'{team.name}','{team.age_group}',True)"

                
                data_to_insert = (id,team.name,team.age_group,True)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                # Commit the transaction
                
                print("IN SAVE TEAM %s"%id)
                return id

async def retrieve_teams_by_user_id(user_id:str) -> List:
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from Roles as r inner join Teams as t on r.Team_ID = t.ID  and r.Email = '{user_id}' order by t.Name" 
                print(insert_query)
                insert_query_2 = f"select * from Roles as r inner join {team_season_data.TABLE.TABLE_NAME} on r.Team_ID={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join {TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{team_season_data.TABLE.ID}={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID}  and r.Email = '{user_id}' order by {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_AGE_GROUP}, {TABLE.TABLE_NAME}.Name" 
                print(insert_query_2)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await cursor.execute(insert_query_2)
                row = await cursor.fetchall()

                # club = Club(id=id,name=row)
                print(row)  
                return row
            
# async def update_team_details(team:UpdateTeam):
#     async with aiomysql.create_pool(**db.db_config) as pool:
#         async with pool.acquire() as conn:
#             async with conn.cursor(aiomysql.DictCursor) as cursor:

#                 # Define the SQL query to insert data into a table
#                 insert_query = f"update Team set Name={team.name}" 
#                 print(insert_query)
#                 # Execute the SQL query to insert data
#                 await cursor.execute(insert_query)
            
#                 row = await cursor.fetchall()
                
#                 # club = Club(id=id,name=row)
#                 print(row)
#                 return row

async def retrieve_users_by_team_id(team_id:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from Roles as r inner join {team_season_data.TABLE.TABLE_NAME} on r.Team_ID = {team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.ID} inner join {users_data.TABLE.TABLE_NAME} on r.Email={users_data.TABLE.TABLE_NAME}.{users_data.TABLE.EMAIL} and r.Team_ID={team_id}" 
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
            
                rows = await cursor.fetchall()
                coaches = []
                for row in rows:  
                    user = convertAdminDataToAdminResponse(row)
                    coaches.append(user)
                return coaches

async def does_userid_match_team(user_id:str,team_id:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from Roles where Team_ID={team_id} and Email = '{user_id}'" 

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
            
                await conn.commit()
                
                return True
                

async def retrieve_team_by_id(team_id:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = f"select * from Teams inner join {team_season_data.TABLE.TABLE_NAME} on Teams.ID={team_season_data.TABLE.TABLE_NAME}.{team_season_data.TABLE.TEAM_ID} and {team_season_data.TABLE.TABLE_NAME}.ID = {team_id}"  
                print(insert_query)
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                row = await cursor.fetchone()
                
                # club = Club(id=id,name=row)
                print(row)
                return row

def convertAdminDataToAdminResponse(team) -> response_classes.Admin:
    print(team)
    role = team["Role"]
    
    email = team["Email"]
    name = team["Name"]
    

    response =  response_classes.Admin(email=email,role=roles.Role(role),name=name)
    print(response)
    return response
if __name__ == "__main__":
  asyncio.run(retrieve_team_by_id("56409"))