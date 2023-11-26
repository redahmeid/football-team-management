from classes import Club, Team
from config import app_config
import id_generator
import db
import aiomysql
import asyncio
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

                # Define the SQL query to insert data into a table
                insert_query = "INSERT INTO Teams (ID,Name,AgeGroup, live) VALUES (%s,%s,%s,%s)"

                # Data to be inserted
                id = id_generator.generate_random_number(5)
                data_to_insert = (id,team.name,team.age_group,True)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                await conn.commit()
                # Commit the transaction
                
                print("IN SAVE TEAM %s"%id)
                return id

async def retrieve_teams_by_user_id(user_id:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "select * from Roles as r inner join Teams as t on r.Team_ID = t.ID and r.Email = %s" 

                # Execute the SQL query to insert data
                await cursor.execute(insert_query,user_id)
            
                row = await cursor.fetchall()
                
                # club = Club(id=id,name=row)
                print(row)
                return row

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
                insert_query = "select * from Teams where id=%s" 

                # Execute the SQL query to insert data
                await cursor.execute(insert_query,team_id)
                row = await cursor.fetchone()
                
                # club = Club(id=id,name=row)
                print(row)
                return row


if __name__ == "__main__":
  asyncio.run(retrieve_teams_by_user_id("r.hmeid@gmail.com"))