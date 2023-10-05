import json
from pydantic import TypeAdapter, ValidationError
from classes import Club
import mysql.connector
from config import app_config

# Replace these with your database credentials
host = app_config.host
user = app_config.user
password = app_config.password
database = app_config.database
footy_db = app_config.admin_db



def drop_database():
    # Connect to the Aurora MySQL database
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=footy_db
    )
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "DROP database %s" %(database)

    
    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
