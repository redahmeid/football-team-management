from classes import Club, Team, TeamUser,User
from config import app_config
import id_generator
import db
import aiomysql
# ID varchar(255),"\
        # "User_ID varchar(255),"\
        # "Team_ID varchar(255),"\
        # "Role varchar(255),"\
        # "live VARCHAR(255),"\
class TABLE:
    TABLE_NAME = "Users"
    ID = "ID"
    NAME="Name"
    EMAIL="Email"
    LIVE="live"

    def createTable():
        return f"CREATE TABLE if not exists {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.EMAIL} varchar(255) NOT NULL Unique,"\
        f"{TABLE.NAME} VARCHAR(255),"\
        f"{TABLE.LIVE} VARCHAR(255),"\
        f"PRIMARY KEY ({TABLE.ID}))"
    def alterTable():
        return f"ALTER TABLE {TABLE.TABLE_NAME}"\
        f" ADD {TABLE.NAME} varchar(255)"
async def save_user(id,email,name):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
# Data to be inserted
                id = id_generator.generate_random_number(5)
                # Define the SQL query to insert data into a table
                insert_query = f"INSERT INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.EMAIL},{TABLE.NAME},{TABLE.LIVE}) VALUES ({id},'{email}','{name}',{True})"
                print(insert_query)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query)
                await conn.commit()
                
                return id

async def retrieve_user_id_by_email(email:str):
    async with aiomysql.create_pool(**db.db_config) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:

                    # Define the SQL query to insert data into a table
                    insert_query = "select * from Users where Email=%s" 
                    print(insert_query)
                    # Execute the SQL query to insert data
                    await cursor.execute(insert_query,email)
                    row = await cursor.fetchone()
                    # Commit the transaction
                    
                    # club = Club(id=id,name=row)
                    print("USER is ")
                    print(row)
                    if(row):
                       return row["ID"]  
                    else:
                        return None

