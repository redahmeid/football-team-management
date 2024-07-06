from classes import  Team, User, TeamUser
from config import app_config
import id_generator
import roles
import db
import asyncio
from player_responses import Guardian
from fcatimer import fcatimer
import aiomysql
#  "CREATE TABLE if not exists Roles" \
#         "(ID varchar(255),"\
#         "Email varchar(255),"\
#         "Team_ID varchar(255),"\
#         "Role varchar(255),"\
#         "live VARCHAR(255),"\
#         "PRIMARY KEY (ID))"

class TABLE:
    ID = "ID"
    TEAM_ID="Team_ID"
    CLUB_ID="Club_ID"
    ROLE="Role"
    EMAIL = "Email"
    LIVE="live"
    TABLE_NAME="Roles"

    def createTable():
        return f"CREATE TABLE if not exists {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.TEAM_ID} varchar(255),"\
        f"{TABLE.CLUB_ID} varchar(255),"\
        f"{TABLE.ROLE} varchar(255),"\
        f"{TABLE.EMAIL} varchar(255),"\
        f"{TABLE.LIVE} varchar(255),"\
        f"PRIMARY KEY ({TABLE.ID}))"
    def alterTable():
        return f"ALTER TABLE {TABLE.TABLE_NAME}"\
        f" ADD {TABLE.CLUB_ID} varchar(255)"
    

async def save_role(user:TeamUser):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Define the SQL query to insert data into a table
                insert_query = "INSERT INTO Roles (ID,Email,Team_ID,Role,live) VALUES (%s,%s,%s,%s,%s)"

                # Data to be inserted
                id = id_generator.generate_random_number(5)
                data_to_insert = (id,user.email,user.team_id,user.role.value,True)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                await conn.commit()
                
                return id

async def save_guardian_role(user:Guardian):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Define the SQL query to insert data into a table
                insert_query = "INSERT INTO Roles (ID,Email,Team_ID,Player_ID,Role,live) VALUES (%s,%s,%s,%s,%s,%s)"

                # Data to be inserted
                id = id_generator.generate_random_number(5)
                data_to_insert = (id,user.email,user.team_id,user.player_id,roles.Role.parent.value,True)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                await conn.commit()
                
                return id
            
async def delete_role(user:TeamUser):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Define the SQL query to insert data into a table
                insert_query = f"Delete from Roles where Email={user.email} and Team_ID={user.team_id}"

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
                return id
@fcatimer
async def retrieve_role_by_user_id_and_team_id(user_id,team_id):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "select * from Roles where Email=%s and Team_ID=%s"
                print(insert_query)
                data_to_insert = (user_id,team_id)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                data = await cursor.fetchall()
                print(data)
                return data

@fcatimer
async def retrieve_team_roles_by_user_id(user_id):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "select Email, Team_ID, GROUP_CONCAT(DISTINCT Roles.Role SEPARATOR ',') AS user_roles from Roles where Email=%s and Team_ID IS NOT NULL group by Team_ID;"
                print(insert_query)
                data_to_insert = (user_id)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                data = await cursor.fetchall()
                print(data)
                return data

@fcatimer
async def retrieve_player_roles_by_user_id(user_id):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "select Email, Player_ID, GROUP_CONCAT(DISTINCT Roles.Role SEPARATOR ',') AS user_roles from Roles where Email=%s and Player_ID IS NOT NULL group by Player_ID;"
                print(insert_query)
                data_to_insert = (user_id)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                data = await cursor.fetchall()
                print(data)
                return data

async def delete_roles_by_email(user_id):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "delete from Roles where Email=%s"

                data_to_insert = (user_id)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
                data = await cursor.fetchall()
                print(data)
                return data

if __name__ == "__main__":
  asyncio.run(retrieve_role_by_user_id_and_team_id("r.hmeid@gmail.com","15344"))