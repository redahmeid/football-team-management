from classes import Match, PlayerMatch
from config import app_config
import id_generator
from firebase_admin import auth
import db
import match_responses
import matches_state_machine
import match_day_data
from typing import List

sql = "select * from Matches where Matches.ID='17753'"
def run():
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    
    print(sql)
    # Execute the SQL query to insert data
    cursor.execute(sql)
    rows = cursor.fetchall()

     # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print(rows)
    return rows