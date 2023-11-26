from classes import Club, Team, User, TeamUser
from config import app_config
import id_generator
import db
import asyncio
import aiomysql
# "CREATE TABLE Teams" \
#         "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "AgeGroup varchar(255) NOT NULL,"\
#         "Email varchar(255) NOT NULL,"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Club_ID) references Clubs(ID))"

async def save_role(user:TeamUser):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Define the SQL query to insert data into a table
                insert_query = "INSERT INTO Roles (ID,Email,Team_ID,Role,live) VALUES (%s,%s,%s,%s,%s)"

                # Data to be inserted
                id = id_generator.generate_random_number(5)
                data_to_insert = (id,user.user_id,user.team_id,user.role.value,True)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                await conn.commit()
                
                return id

async def retrieve_role_by_user_id_and_team_id(user_id,team_id):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "select * from Roles where Email=%s and Team_ID=%s"

                data_to_insert = (user_id,team_id)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                data = await cursor.fetchall()
                print(data)
                return data

if __name__ == "__main__":
  asyncio.run(retrieve_role_by_user_id_and_team_id("r.hmeid@gmail.com","15344"))