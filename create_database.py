from config import app_config
import json
from pydantic import TypeAdapter, ValidationError
from classes import Club
import mysql.connector



host = app_config.host
user = app_config.user
password = app_config.password
database = app_config.database
footy_db = app_config.admin_db




def create_database():
    # Replace these with your database credentials
    
    
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
    insert_query = "CREATE database %s" %(database)
    

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
  
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
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
  
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
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
