from classes import Match, PlayerMatch
from config import app_config
import id_generator
from firebase_admin import auth
import db

# "CREATE TABLE Match_Day_Lineup" \
#         "(ID varchar(255),"\
#         "Match_ID varchar(255) NOT NULL,"\
#         "Player_ID varchar(255) NOT NULL,"\
#         "Subbed_On int,"\
#         "Subbed_Off int,"\
#         "Position varchar(255),"\
#         "PRIMARY KEY (Match_ID,Player_ID,Start_Time_Minutes),"\
#         "FOREIGN KEY(Match_ID) references Matches(ID),"\
#         "FOREIGN KEY(Player_ID) references Players(ID))"

def save_match_day_player(match_id, player_id,subbed_on,subbed_off,position):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Match_Day_Lineup (ID,Match_ID,Player_ID, Subbed_On, Subbed_Off,Position) VALUES (%s,%s,%s,%s,%s,%s)"

    # Data to be inserted
    id = id_generator.generate_random_number(5)
    data_to_insert = (id,match_id,player_id,subbed_on,subbed_off,position)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
   
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return str(id)



def update_subbed_off_player(subbed_off_time, match_day_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "update Match_Day_Lineup set Subbed_Off= %s where ID=%s"

    data_to_insert = (subbed_off_time,match_day_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    result = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return result

def update_subbed_on_player(subbed_on_time, match_day_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "update Match_Day_Lineup set Subbed_On= %s where ID=%s"

    data_to_insert = (subbed_on_time,match_day_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    result = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return result

def delete_match_day_player(match_day_id):
    print("IS A MATCH ID THERE %s"%match_day_id)
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "delete from Match_Day_Lineup where ID=%s"
    print("QUERY %s"%insert_query)
    data_to_insert = (match_day_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    result = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return result

def retrieve_starting_lineup(match_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    print("IS A MATCH ID THERE %s"%match_id)
    # Define the SQL query to insert data into a table
    insert_query = "select * from Match_Day_Lineup where Match_ID=%s and Subbed_On <= 0 and Subbed_Off > 0"
    print("INSERT QUERY %s"%insert_query)
    data_to_insert = (match_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, match_id)
    print("EXECUTED")
    result = cursor.fetchall()
    print("STARTNNG LINEUP RESULT: " )
    # Commit the transaction
    connection.commit()
    print("STARTNNG LINEUP RESULT: " )
    # Close the cursor and connection
    cursor.close()
    connection.close()
    return result



def update_match_status(match_id,status):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    # Define the SQL query to insert data into a table
    insert_query = "update Matches set Status=%s where Match_ID=%s"
    
    data_to_insert = (status,match_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    
    result = cursor.rowcount
    # Commit the transaction
    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    return result






