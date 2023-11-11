from classes import Match, PlayerMatch
from config import app_config
import id_generator
from firebase_admin import auth
import db
import player_responses
import player_data
from typing import List

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

class TABLE:
    TABLE_NAME = "Match_Day_Lineup"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    MINUTE_ON="Minute_on"
    POSITION = "Position"
    NAME="Name"

    def createTable():
        return f"CREATE TABLE {TABLE.TABLE_NAME}" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{TABLE.MINUTE_ON} int,"\
        f"{TABLE.POSITION} varchar(255),"\
        f"PRIMARY KEY ({TABLE.ID}),"\
        f"FOREIGN KEY({TABLE.MATCH_ID}) references Matches(ID),"\
        f"FOREIGN KEY({TABLE.PLAYER_ID}) references Players(ID))"

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

class MATCH_STATUS_TABLE:
    TABLE_NAME="Match_Status"
    ID = "ID"
    MATCH_ID="Match_ID"
    STATUS="Status"
    MINUTE="Minute_on"
    

    def createTable():
        return f"CREATE TABLE {MATCH_STATUS_TABLE.TABLE_NAME} " \
        f"({MATCH_STATUS_TABLE.ID} varchar(255),"\
        f"{MATCH_STATUS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{MATCH_STATUS_TABLE.STATUS} varchar(255) NOT NULL,"\
        f"{MATCH_STATUS_TABLE.MINUTE} int,"\
        f"PRIMARY KEY ({MATCH_STATUS_TABLE.ID}),"\
        f"FOREIGN KEY({MATCH_STATUS_TABLE.MATCH_ID}) references Matches(ID))"


def save_match_day_player(match_id, player_id,minute,position):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    id = id_generator.generate_random_number(5)
    # Define the SQL query to insert data into a table
    delete_query =f"delete from {TABLE.TABLE_NAME} where {TABLE.MATCH_ID}='{match_id}' and {TABLE.PLAYER_ID}='{player_id}' and {TABLE.MINUTE_ON} = {minute}"
    print(delete_query)
    cursor.execute(delete_query)
    insert_query = f"insert INTO {TABLE.TABLE_NAME} ({TABLE.ID},{TABLE.MATCH_ID},{TABLE.PLAYER_ID}, {TABLE.MINUTE_ON},{TABLE.POSITION}) VALUES ('{id}','{match_id}','{player_id}',{minute},'{position}')"
    print(insert_query)
    # Data to be inserted
    

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
   
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

def retieve_lineup_by_minute(match_id,minute) -> List[player_responses.PlayerResponse]:
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    print("IS A MATCH ID THERE %s"%match_id)
    # Define the SQL query to insert data into a table
    insert_query = f"select * from {TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {TABLE.TABLE_NAME}.{TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {TABLE.TABLE_NAME}.{TABLE.MATCH_ID}={match_id} and {TABLE.TABLE_NAME}.{TABLE.MINUTE_ON} = {minute}"
    

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    results = cursor.fetchall()
    
    # Commit the transaction
    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    print(results)
    players = []
    for result in results:
        players.append(convertStartingLineup(result))
    print(players)
    return players



def update_match_status(match_id,status,minute):
    try:
        connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
        cursor = connection.cursor()
        # Define the SQL query to insert data into a table
        delete_query = f"delete from {MATCH_STATUS_TABLE.TABLE_NAME} where {MATCH_STATUS_TABLE.MATCH_ID}='{match_id}'  and {MATCH_STATUS_TABLE.MINUTE}={minute}"
        print(delete_query)
        
        # Execute the SQL query to insert data
        cursor.execute(delete_query)
        insert_query = f"insert into {MATCH_STATUS_TABLE.TABLE_NAME} ({MATCH_STATUS_TABLE.ID},{MATCH_STATUS_TABLE.STATUS},{MATCH_STATUS_TABLE.MATCH_ID},{MATCH_STATUS_TABLE.MINUTE}) values ('{id_generator.generate_random_number(5)}','{status}','{match_id}',{minute})"
        print(insert_query)
        
        # Execute the SQL query to insert data
        cursor.execute(insert_query)
        
        result = cursor.rowcount
        print(result)
        # Commit the transaction
        connection.commit()
        # Close the cursor and connection
        cursor.close()
        connection.close()
    except Exception as e:
        print(e)
    return result

def retrieve_latest_minute(match_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    # Define the SQL query to insert data into a table
    insert_query = f"select {MATCH_STATUS_TABLE.MINUTE} from {MATCH_STATUS_TABLE.TABLE_NAME} where {MATCH_STATUS_TABLE.MATCH_ID}={match_id} order by {MATCH_STATUS_TABLE.MINUTE} desc"
    
    
    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    
    results = cursor.fetchone()

    # Commit the transaction
    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    print(results[MATCH_STATUS_TABLE.MINUTE])
    return results[MATCH_STATUS_TABLE.MINUTE]

def convertStartingLineup(data):
    player_info = player_responses.PlayerInfo(id=data[TABLE.PLAYER_ID],name=data[TABLE.NAME])
    selection_info = player_responses.SelectionInfo(id=data[TABLE.ID],position=data[TABLE.POSITION],minuteOn=data[TABLE.MINUTE_ON])
    playerResponse = player_responses.PlayerResponse(info=player_info,selectionInfo=selection_info)
    return playerResponse



