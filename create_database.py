from config import app_config
import json
from pydantic import TypeAdapter, ValidationError
from classes import Club
import db



def create_database():
    connection = db.connection()
    print("CREATE DATABASE IN %s" %(connection.db))
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "CREATE database %s" %(app_config.database)
    

    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()
     # Close the cursor and connection
    cursor.close()
    connection.close()
    create_clubs_table()
    # create_teams_table()
   
    


def create_clubs_table():
    connection = db.connection(app_config.database)
    print("CREATE TABLE IN %s" %(connection.db))
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Clubs" \
    "(ID varchar(255),"\
    "Name varchar(255) NOT NULL,"\
    "Short_Name varchar(255) NOT NULL,"\
    "Email varchar(255),"\
    "Phone varchar(255)NOT NULL,"\
    "AgeGroup int,"\
    "PRIMARY KEY (ID))"


    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

def create_teams_table():
    connection = db.connection()
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Teams "
    +"(ID varchar(255),"
    +"Name varchar(255) NOT NULL,"
    +"Email varchar(255),"
    +"Phone varchar(255)NOT NULL,"
    +"Age_Group int,"
    +"Club_id varchar(255),"
    +"PRIMARY KEY (ID),"
    +"FOREIGN KEY (Club_id) REFERENCES Clubs(ID))"


    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
