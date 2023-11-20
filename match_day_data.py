from classes import Match, PlayerMatch
from config import app_config
import id_generator
from firebase_admin import auth
import db
import player_responses
import player_data
from typing import List, Dict
import matches_state_machine
from datetime import datetime
import matches_data
import sys


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


class PLANNED_LINEUP_TABLE:
    TABLE_NAME = "Planned_Lineups"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    MINUTE="Minute"
    POSITION = "Position"
    NAME="Name"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE {PLANNED_LINEUP_TABLE.TABLE_NAME}" \
        f"({PLANNED_LINEUP_TABLE.ID} varchar(255),"\
        f"{PLANNED_LINEUP_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{PLANNED_LINEUP_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{PLANNED_LINEUP_TABLE.MINUTE} int,"\
        f"{PLANNED_LINEUP_TABLE.POSITION} varchar(255),"\
        f"{PLANNED_LINEUP_TABLE.TIME} int,"\
        f"{PLANNED_LINEUP_TABLE.SOFT_DELETE} bool,"\
        f"{PLANNED_LINEUP_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({PLANNED_LINEUP_TABLE.ID}),"\
        f"FOREIGN KEY({PLANNED_LINEUP_TABLE.MATCH_ID}) references Matches(ID),"\
        f"FOREIGN KEY({PLANNED_LINEUP_TABLE.PLAYER_ID}) references Players(ID))"

class ACTUAL_LINEDUP_TABLE:
    TABLE_NAME = "Actual_Lineups"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    POSITION = "Position"
    NAME="Name"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE {ACTUAL_LINEDUP_TABLE.TABLE_NAME}" \
        f"({ACTUAL_LINEDUP_TABLE.ID} varchar(255),"\
        f"{ACTUAL_LINEDUP_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{ACTUAL_LINEDUP_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{ACTUAL_LINEDUP_TABLE.POSITION} varchar(255),"\
        f"{ACTUAL_LINEDUP_TABLE.TIME} int,"\
        f"{ACTUAL_LINEDUP_TABLE.SOFT_DELETE} bool,"\
        f"{ACTUAL_LINEDUP_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({ACTUAL_LINEDUP_TABLE.ID}),"\
        f"FOREIGN KEY({ACTUAL_LINEDUP_TABLE.MATCH_ID}) references Matches(ID),"\
        f"FOREIGN KEY({ACTUAL_LINEDUP_TABLE.PLAYER_ID}) references Players(ID))"

class GOALS_TABLE:
    TABLE_NAME = "Goals"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE {GOALS_TABLE.TABLE_NAME}" \
        f"({GOALS_TABLE.ID} varchar(255),"\
        f"{GOALS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{GOALS_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{GOALS_TABLE.TIME} int,"\
        f"{GOALS_TABLE.SOFT_DELETE} bool,"\
        f"{GOALS_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({GOALS_TABLE.ID}),"\
        f"FOREIGN KEY({GOALS_TABLE.MATCH_ID}) references Matches(ID),"\
        f"FOREIGN KEY({GOALS_TABLE.PLAYER_ID}) references Players(ID))"

class OPPOSITION_GOALS_TABLE:
    TABLE_NAME = "Opposition_Goals"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_NUMBER="Player_Number"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE {OPPOSITION_GOALS_TABLE.TABLE_NAME}" \
        f"({OPPOSITION_GOALS_TABLE.ID} varchar(255),"\
        f"{OPPOSITION_GOALS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{OPPOSITION_GOALS_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{OPPOSITION_GOALS_TABLE.TIME} int,"\
        f"{OPPOSITION_GOALS_TABLE.SOFT_DELETE} bool,"\
        f"{OPPOSITION_GOALS_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({OPPOSITION_GOALS_TABLE.ID}),"\
        f"FOREIGN KEY({OPPOSITION_GOALS_TABLE.MATCH_ID}) references Matches(ID))"
    

class ASSISTS_TABLE:
    TABLE_NAME = "Assists"
    ID = "ID"
    MATCH_ID="Match_ID"
    PLAYER_ID="Player_ID"
    TIME="Time"
    SOFT_DELETE="Deleted"
    SOFT_DELETE_TIME="Deleted_TIME"

    def createTable():
        return f"CREATE TABLE {ASSISTS_TABLE.TABLE_NAME}" \
        f"({ASSISTS_TABLE.ID} varchar(255),"\
        f"{ASSISTS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{ASSISTS_TABLE.PLAYER_ID} varchar(255) NOT NULL,"\
        f"{ASSISTS_TABLE.TIME} int,"\
        f"{ASSISTS_TABLE.SOFT_DELETE} bool,"\
        f"{ASSISTS_TABLE.SOFT_DELETE_TIME} int,"\
        f"PRIMARY KEY ({ASSISTS_TABLE.ID}),"\
        f"FOREIGN KEY({ASSISTS_TABLE.MATCH_ID}) references Matches(ID),"\
        f"FOREIGN KEY({ASSISTS_TABLE.PLAYER_ID}) references Players(ID))"

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
    LINEUP_CHANGE="Lineup_Change"
    

    def createTable():
        return f"CREATE TABLE {MATCH_STATUS_TABLE.TABLE_NAME} " \
        f"({MATCH_STATUS_TABLE.ID} varchar(255),"\
        f"{MATCH_STATUS_TABLE.MATCH_ID} varchar(255) NOT NULL,"\
        f"{MATCH_STATUS_TABLE.STATUS} varchar(255) NOT NULL,"\
        f"{MATCH_STATUS_TABLE.LINEUP_CHANGE} int,"\
        f"PRIMARY KEY ({MATCH_STATUS_TABLE.ID}),"\
        f"FOREIGN KEY({MATCH_STATUS_TABLE.MATCH_ID}) references Matches(ID))"

def save_goals_for(match_id,player_id):
    connection = db.connection(app_config.database)
    
        # Create a cursor object to interact with the database
    cursor = connection.cursor()
    
        
    id = id_generator.generate_random_number(5)
   
    insert_query = f"insert INTO {GOALS_TABLE.TABLE_NAME} ({GOALS_TABLE.ID},{GOALS_TABLE.MATCH_ID},{GOALS_TABLE.PLAYER_ID}, {GOALS_TABLE.TIME}) VALUES ('{id}','{match_id}','{player_id}',{int(datetime.utcnow().timestamp())})"
    print(insert_query)
    cursor.execute(insert_query)
        
        # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return True

def save_assists_for(match_id,player_id):
    connection = db.connection(app_config.database)
    
        # Create a cursor object to interact with the database
    cursor = connection.cursor()
    
        
    id = id_generator.generate_random_number(5)
   
    insert_query = f"insert INTO {ASSISTS_TABLE.TABLE_NAME} ({ASSISTS_TABLE.ID},{ASSISTS_TABLE.MATCH_ID},{ASSISTS_TABLE.PLAYER_ID}, {ASSISTS_TABLE.TIME}) VALUES ('{id}','{match_id}','{player_id}',{int(datetime.utcnow().timestamp())})"
    print(insert_query)
    cursor.execute(insert_query)
        
        # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return True

def save_opposition_goal(match_id,player_number):
    connection = db.connection(app_config.database)
    
        # Create a cursor object to interact with the database
    cursor = connection.cursor()
    
        
    id = id_generator.generate_random_number(5)
   
    insert_query = f"insert INTO {OPPOSITION_GOALS_TABLE.TABLE_NAME} ({OPPOSITION_GOALS_TABLE.ID},{OPPOSITION_GOALS_TABLE.MATCH_ID},{OPPOSITION_GOALS_TABLE.PLAYER_NUMBER}, {OPPOSITION_GOALS_TABLE.TIME}) VALUES ('{id}','{match_id}','{player_number}',{int(datetime.utcnow().timestamp())})"
    print(insert_query)
    cursor.execute(insert_query)
        
        # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return True

def save_planned_lineup(match_id,minute,players:List[player_responses.PlayerResponse]):
    connection = db.connection(app_config.database)
    players_saved = 0
    original_list_size=len(players)
        # Create a cursor object to interact with the database
    cursor = connection.cursor()
    for player in players:
        
        id = id_generator.generate_random_number(5)
        
        #reset the plan
        delete_query =f"update {PLANNED_LINEUP_TABLE.TABLE_NAME} set {PLANNED_LINEUP_TABLE.SOFT_DELETE}=True, {PLANNED_LINEUP_TABLE.SOFT_DELETE_TIME}={int(datetime.utcnow().timestamp())} where {PLANNED_LINEUP_TABLE.MATCH_ID}='{match_id}' and {PLANNED_LINEUP_TABLE.PLAYER_ID}='{player.info.id}' and {PLANNED_LINEUP_TABLE.MINUTE} >= {minute}"
        print(delete_query)
        cursor.execute(delete_query)
        insert_query = f"insert INTO {PLANNED_LINEUP_TABLE.TABLE_NAME} ({PLANNED_LINEUP_TABLE.ID},{PLANNED_LINEUP_TABLE.MATCH_ID},{PLANNED_LINEUP_TABLE.PLAYER_ID}, {PLANNED_LINEUP_TABLE.MINUTE},{PLANNED_LINEUP_TABLE.POSITION},{PLANNED_LINEUP_TABLE.TIME}) VALUES ('{id}','{match_id}','{player.info.id}',{minute},'{player.selectionInfo.position}',{int(datetime.utcnow().timestamp())})"
        print(insert_query)
        cursor.execute(insert_query)
        
        # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return True

def save_actual_lineup(match_id,players:List[player_responses.PlayerResponse]):
    connection = db.connection(app_config.database)
    players_saved = 0
    original_list_size=players.count
        # Create a cursor object to interact with the database
    cursor = connection.cursor()
    for player in players:
        
        id = id_generator.generate_random_number(5)
        
        #reset the plan
        delete_query =f"update {ACTUAL_LINEDUP_TABLE.TABLE_NAME} set {ACTUAL_LINEDUP_TABLE.SOFT_DELETE}=True, {ACTUAL_LINEDUP_TABLE.SOFT_DELETE_TIME}={int(datetime.utcnow().timestamp())} where {ACTUAL_LINEDUP_TABLE.MATCH_ID}='{match_id}' and {ACTUAL_LINEDUP_TABLE.PLAYER_ID}='{player.info.id}'"
        print(delete_query)
        cursor.execute(delete_query)
        insert_query = f"insert INTO {ACTUAL_LINEDUP_TABLE.TABLE_NAME} ({ACTUAL_LINEDUP_TABLE.ID},{ACTUAL_LINEDUP_TABLE.MATCH_ID},{ACTUAL_LINEDUP_TABLE.PLAYER_ID}, {ACTUAL_LINEDUP_TABLE.POSITION},{ACTUAL_LINEDUP_TABLE.TIME}) VALUES ('{id}','{match_id}','{player.info.id}','{player.selectionInfo.position}',{int(datetime.utcnow().timestamp())})"
        print(insert_query)
        cursor.execute(insert_query)
        # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return True


def retrieveAllPlannedLineups(match_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    # Define the SQL query to insert data into a table
    insert_query = f"select * from {PLANNED_LINEUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MATCH_ID}={match_id} and ({PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} IS NULL or {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} != True) order by {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
    print(insert_query)

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

    all_lineups = []
    i = 0
    for result in results:
        player = convertToPlannedStartingLineup(result)
        
        if(i==0): minute = player.selectionInfo.minuteOn
        i+=1
        if(minute!=player.selectionInfo.minuteOn):
            all_lineups.append({"status":minute,"players":players})
            minute=player.selectionInfo.minuteOn
            players = []
        players.append(player)
        if(i+1==len(results)):
            all_lineups.append({"status":minute,"players":players})
    print(all_lineups)
    return all_lineups

def retrieveNextPlanned(match_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    match = matches_data.retrieve_match_by_id(match_id)[0]
    minutes =match.how_long_ago_started
    
    # Define the SQL query to insert data into a table
    insert_query = f"select * from {PLANNED_LINEUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MATCH_ID}={match_id} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE}>{minutes} and ({PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} IS NULL or {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} != True) order by {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
    print(insert_query)

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
    i = 0
    minute = 0
    for result in results:
        player = convertToPlannedStartingLineup(result)
        
        if(i==0): minute = player.selectionInfo.minuteOn
        i+=1
        if(minute!=player.selectionInfo.minuteOn):
            break
        players.append(player)
    print(players)
    return players

def retrieveNextPlannedByMinute(match_id,minutes):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    match = matches_data.retrieve_match_by_id(match_id)[0]
   
    
    # Define the SQL query to insert data into a table
    insert_query = f"select * from {PLANNED_LINEUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MATCH_ID}={match_id} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE}>{minutes} and ({PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} IS NULL or {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} != True) order by {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
    print(insert_query)

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
    i = 0
    minute = 0
    for result in results:
        player = convertToPlannedStartingLineup(result)
        
        if(i==0): minute = player.selectionInfo.minuteOn
        i+=1
        if(minute!=player.selectionInfo.minuteOn):
            break
        players.append(player)
    print(players)
    return players

def retrieveStartingLineup(match_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    
    
    # Define the SQL query to insert data into a table
    insert_query = f"select * from {PLANNED_LINEUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MATCH_ID}={match_id} and {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE}=0 and ({PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} IS NULL or {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.SOFT_DELETE} != True) order by {PLANNED_LINEUP_TABLE.TABLE_NAME}.{PLANNED_LINEUP_TABLE.MINUTE} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
    print(insert_query)

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    results = cursor.fetchall()
    
    # Commit the transaction
    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    
    players = []
    i = 0
    minute = 0
    for result in results:
        player = convertToPlannedStartingLineup(result)
        
        if(i==0): minute = player.selectionInfo.minuteOn
        i+=1
        if(minute!=player.selectionInfo.minuteOn):
            break
        players.append(player)
    
    print(players)
    return players
def retrieveCurrentActual(match_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    match = matches_data.retrieve_match_by_id(match_id)[0]
    minutes = match.how_long_ago_started
    
    # Define the SQL query to insert data into a table
    insert_query = f"select * from {ACTUAL_LINEDUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.MATCH_ID}={match_id} and {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.TIME}<={int(datetime.utcnow().timestamp())} and ({ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.SOFT_DELETE} IS NULL or {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.SOFT_DELETE} != False) order by {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.TIME} desc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
    print(insert_query)

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    results = cursor.fetchall()
    
    # Commit the transaction
    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    
    players = []
    i = 0
    minute = 0
    for result in results:
        player = convertToActualStartingLineup(result)
        if(i==0): minute = player.selectionInfo.minuteOn
        i+=1
        if(minute!=player.selectionInfo.minuteOn):
            break
        players.append(player)
    print(players)
    return players    

def retrieveAllActualLineups(match_id):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    # Define the SQL query to insert data into a table
    insert_query = f"select * from {ACTUAL_LINEDUP_TABLE.TABLE_NAME} inner join {player_data.TABLE.TABLE_NAME} on {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.PLAYER_ID}={player_data.TABLE.TABLE_NAME}.{player_data.TABLE.ID} and {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.MATCH_ID}={match_id} and {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.SOFT_DELETE} <> False order by {ACTUAL_LINEDUP_TABLE.TABLE_NAME}.{ACTUAL_LINEDUP_TABLE.TIME} asc, {player_data.TABLE.TABLE_NAME}.{player_data.TABLE.NAME}"
    print(insert_query)

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
        players.append(convertToActualStartingLineup(result))
    print(players)
    return players





def convertToPlannedStartingLineup(data):
    player_info = player_responses.PlayerInfo(id=data[PLANNED_LINEUP_TABLE.PLAYER_ID],name=data[player_data.TABLE.NAME])
    selection_info = player_responses.SelectionInfo(id=data[PLANNED_LINEUP_TABLE.ID],position=data[PLANNED_LINEUP_TABLE.POSITION],minuteOn=data[PLANNED_LINEUP_TABLE.MINUTE])
    playerResponse = player_responses.PlayerResponse(info=player_info,selectionInfo=selection_info)
    return playerResponse

def convertToActualStartingLineup(data):
    player_info = player_responses.PlayerInfo(id=data[ACTUAL_LINEDUP_TABLE.PLAYER_ID],name=data[player_data.TABLE.NAME])
    selection_info = player_responses.SelectionInfo(id=data[ACTUAL_LINEDUP_TABLE.ID],position=data[ACTUAL_LINEDUP_TABLE.POSITION],minuteOn=data[ACTUAL_LINEDUP_TABLE.TIME])
    playerResponse = player_responses.PlayerResponse(info=player_info,selectionInfo=selection_info)
    return playerResponse


if __name__ == "__main__":
    if(sys.argv[1]=="retrieveCurrentActual"):   
        retrieveCurrentActual(sys.argv[2])
    if(sys.argv[1]=="retrieveAllPlannedLineups"):   
        retrieveAllPlannedLineups(sys.argv[2])
    if(sys.argv[1]=="retrieveCurrentActual"):   
        retrieveCurrentActual(sys.argv[2])
    if(sys.argv[1]=="retrieveNextPlanned"):  
        retrieveNextPlanned(sys.argv[2])