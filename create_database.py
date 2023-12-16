from config import app_config
import db
import match_day_data
import matches_data
import sys
import notifications
import aiomysql
import asyncio
import users_data
import team_season_data
import player_data
import roles_data

async def drop_database():
    try:
        # Define the SQL query to insert data into a table
        insert_query = "Drop database %s" %(app_config.database)
        print(insert_query)
        print(db.admin_db_config)
        async with aiomysql.create_pool(**db.admin_db_config) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Execute the SQL query to insert data
                    await cursor.execute(insert_query)

                    # Commit the transaction
                    await conn.commit()
                    
                    
                    # create_teams_table()
    except Exception as e:
        print(e)

                                    
async def create_database():
    try:
        # Define the SQL query to insert data into a table
        insert_query = "CREATE database %s" %(app_config.database)
        print(insert_query)
        print(db.admin_db_config)
        async with aiomysql.create_pool(**db.admin_db_config) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Execute the SQL query to insert data
                    await cursor.execute(insert_query)

                    # Commit the transaction
                    await conn.commit()
                    
                    
                    # create_teams_table()
    except Exception as e:
        print(e)
    await create_teams_table()
    await create_tables(matches_data.TABLE.createTable())
    await create_players_table()
    await create_tables(users_data.TABLE.createTable()), 
    await create_tables(player_data.PLAYER_SEASON_TABLE.createTable()), 
    await create_tables(roles_data.TABLE.createTable()), 
    
    await create_tables(match_day_data.PLANNED_LINEUP_TABLE.createTable()),
    await create_tables(match_day_data.ACTUAL_LINEDUP_TABLE.createTable()),
    await create_tables(match_day_data.MATCH_STATUS_TABLE.createTable()),
    await create_tables(match_day_data.GOALS_TABLE.createTable()),
    await create_tables(match_day_data.ASSISTS_TABLE.createTable()),
    await create_tables(match_day_data.OPPOSITION_GOALS_TABLE.createTable()),
    await create_tables(notifications.TABLE.createTable()),
    await create_tables(match_day_data.PERIODS_TABLE.createTable()),
    await create_tables(match_day_data.SUBS_TABLE.createTable()), 
    await create_tables(team_season_data.TABLE.createTable()), 
    await create_tables(notifications.MESSAGES_TABLE.createTable()),
    try:
        await create_tables(matches_data.TABLE.alterTable())
    except Exception as e:
        print(e)
    try:
        await create_tables(match_day_data.ACTUAL_LINEDUP_TABLE.alterTable())
    except Exception as e:
        print(e)
    try:
        await create_tables(users_data.TABLE.alterTable())
    except Exception as e:
        print(e)
    try:
        await create_tables(match_day_data.GOALS_TABLE.alterTable())
    except Exception as e:
        print(e)
    
    try:
        await create_tables(roles_data.TABLE.alterTable())
    except Exception as e:
        print(e)
    # try:
    #     await create_tables(notifications.TABLE.removeMatchID())
    # except Exception as e:
    #     print(e)
    # try:
    #     await create_tables(notifications.TABLE.removeTeamID())
    # except Exception as e:
    #     print(e)
    # try:
    #     await create_tables(notifications.TABLE.removePlayerID())
    # except Exception as e:
    #     print(e)


async def create_tables(sql):
  
   async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

                # Execute the SQL query to insert data
                await cursor.execute(sql)
                await conn.commit()

async def create_teams_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE if not exists Teams" \
        "(ID varchar(255),"\
        "Name varchar(255) NOT NULL,"\
        "AgeGroup varchar(255) NOT NULL,"\
        "live VARCHAR(255),"\
        "PRIMARY KEY (ID))"


    print(insert_query)
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

   
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)

                # Commit the transaction
                await conn.commit()


async def create_users_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE if not exists Users" \
        "(ID varchar(255),"\
        "Email varchar(255) NOT NULL Unique,"\
        "live VARCHAR(255),"\
        "PRIMARY KEY (ID))"


    print(insert_query)
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

            
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)

                # Commit the transaction
                await conn.commit()


async def create_team_users_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE if not exists Roles" \
        "(ID varchar(255),"\
        "Email varchar(255),"\
        "Team_ID varchar(255),"\
        "Role varchar(255),"\
        "live VARCHAR(255),"\
        "PRIMARY KEY (ID))"


    print(insert_query)
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

   
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)

                # Commit the transaction
                await conn.commit()


async def create_players_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE if not exists Players" \
        "(ID varchar(255),"\
        "Name varchar(255) NOT NULL,"\
        "Team_ID varchar(255) NOT NULL,"\
        "Email varchar(255),"\
        "live varchar(255),"\
        "PRIMARY KEY (ID))"


    print(insert_query)
    async with aiomysql.create_pool(**db.db_config) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:

   
                # Execute the SQL query to insert data
                await cursor.execute(insert_query)

                # Commit the transaction
                await conn.commit()


def alter_players_table(field_name,data_type):
     # Define the SQL query to insert data into a table
    insert_query = "alter TABLE Players ADD %s %s"%(field_name,data_type)

    print(insert_query)

    
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

   
    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    describe_query = "describe Players"

    print(describe_query)

   
    # Execute the SQL query to insert data
    cursor.execute(describe_query)
    row = cursor.fetchall()

    print(row)
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()



if __name__ == "__main__":
    if(sys.argv[1]=="create"):   
        asyncio.run(create_database())