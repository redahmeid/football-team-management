import json
from pydantic import TypeAdapter, ValidationError
from classes import Club
from config import app_config
import db




def drop_database():
    print("In drop database")
    connection = db.connection()
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "DROP database %s" %(app_config.database)
    print("After drop db")
    
    # Execute the SQL query to insert data
    cursor.execute(insert_query)
   
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
