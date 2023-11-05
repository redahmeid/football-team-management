from classes import Club, Team, TeamUser,User
from config import app_config
import id_generator
import db

# ID varchar(255),"\
        # "User_ID varchar(255),"\
        # "Team_ID varchar(255),"\
        # "Role varchar(255),"\
        # "live VARCHAR(255),"\

def save_user(id,email):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Users (ID,Email,live) VALUES (%s,%s,%s)"

    # Data to be inserted
    id = id_generator.generate_random_number(5)
    data_to_insert = (id,email,True)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    row_count = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return id

def retrieve_user_id_by_email(email:str):
    print("IN RETRIEVE USER %s"%email)
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Users where Email=%s" 
    
    # Execute the SQL query to insert data
    cursor.execute(insert_query,email)
    row = cursor.fetchone()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(row)
    return row["ID"]  

