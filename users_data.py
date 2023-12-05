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

async def save_user(id,email):
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Define the SQL query to insert data into a table
                insert_query = "INSERT INTO Users (ID,Email,live) VALUES (%s,%s,%s)"

                # Data to be inserted
                id = id_generator.generate_random_number(5)
                data_to_insert = (id,email,True)

                # Execute the SQL query to insert data
                await cursor.execute(insert_query, data_to_insert)
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

