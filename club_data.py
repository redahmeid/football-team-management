import json
from pydantic import TypeAdapter, ValidationError
from classes import Club, Team
import mysql.connector
from config import app_config
import response_errors
import id_generator
import db



def save_club(club:Club):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Clubs (ID,name,short_name, email,phone) VALUES (%s,%s,%s,%s,%s)"

    # Data to be inserted
    id = "%s%s" %(club.short_name,id_generator.generate_random_number(5))
    data_to_insert = (id,club.name,club.short_name,club.email,club.phone)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    row_count = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return (row_count,id)

def retrieve_club(id:str):
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Clubs where ID = %s" %(id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    row = cursor.fetchone()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(row)
    return row