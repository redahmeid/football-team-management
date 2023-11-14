from classes import Match, PlayerMatch
from config import app_config
import id_generator
from firebase_admin import auth
import db
import match_responses
import matches_state_machine
import match_day_data
from typing import List

# "CREATE TABLE Matches" \
#         "(ID varchar(255),"\
#         "Opposition varchar(255) NOT NULL,"\
#         "Team_ID varchar(255) NOT NULL,"\
#         "HomeOrAway varchar(255),"\
#         "Date datetime,"\
#         "Status varchar(255),"\
#         "Goals_For int,"\
#         "Goals_Against int,"\
#         "Length int,"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Team_ID) references Teams(ID))"

class TABLE:
    ID = "ID"
    OPPOSITION="Opposition"
    TEAM_ID="Team_ID"
    HOME_OR_AWAY="HomeOrAway"
    DATE = "Date"
    STATUS = "Status"
    GOALS_FOR = "Goals_For"
    GOALS_AGAINST = "Goals_Against"
    LENGTH = "Length"
    TABLE_NAME="Matches"

    def createTable():
        return f"CREATE TABLE Matches" \
        f"({TABLE.ID} varchar(255),"\
        f"{TABLE.OPPOSITION} varchar(255) NOT NULL,"\
        f"{TABLE.TEAM_ID} varchar(255) NOT NULL,"\
        f"{TABLE.HOME_OR_AWAY} varchar(255),"\
        f"{TABLE.DATE} datetime,"\
        f"{TABLE.STATUS} varchar(255),"\
        f"{TABLE.GOALS_FOR} int,"\
        f"{TABLE.GOALS_AGAINST} int,"\
        f"{TABLE.LENGTH} int,"\
        f"PRIMARY KEY ({TABLE.ID}),"\
        f"FOREIGN KEY({TABLE.TEAM_ID}) references Teams({TABLE.ID}))"


def save_team_fixture(match:Match):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()
    id = id_generator.generate_random_number(5)
    # Define the SQL query to insert data into a table
    insert_query = f"INSERT INTO Matches (ID,Opposition,HomeOrAway, Date,Length,Team_ID,Status) VALUES ('{id}','{match.opposition}','{match.homeOrAway}','{match.date}','{match.length}','{match.team_id}','{match.status}')"
    print(insert_query)
    # Data to be inserted
    
    
    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    print(cursor.rowcount)
   
    # Commit the transaction
    connection.commit()
    if(cursor.rowcount>0):
        match_day_data.update_match_lineup_status(match_id=id,status=match.status,minute=0)
    # Close the cursor and connection
    cursor.close()
    connection.close()
    return id


def retrieve_matches_by_team(team_id:str) -> List[match_responses.MatchInfo]:
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = f"select * from {TABLE.TABLE_NAME} where {TABLE.TABLE_NAME}.{TABLE.TEAM_ID} = '{team_id}' order by {TABLE.TABLE_NAME}.{TABLE.DATE} asc" 
    print(insert_query)

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    rows = cursor.fetchall()

     # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    matches = []
    print(rows)
    for row in rows:
        matches.append(convertDataToMatchInfo(row))
    print(matches)
    return matches

def update_match_status(match_id,status)  -> List[match_responses.MatchInfo]:
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = f"update {TABLE.TABLE_NAME} set {TABLE.STATUS}='{status}' where {TABLE.ID}='{match_id}'" 
    print(insert_query)

    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    rowcount = cursor.rowcount
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    if(rowcount>0):
        return retrieve_match_by_id(match_id)
    else:
        return None

def retrieve_match_by_id(id:str) -> List[match_responses.MatchInfo]:
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = f"select * from {TABLE.TABLE_NAME} where {TABLE.TABLE_NAME}.{TABLE.ID}='{id}'" 
    print(insert_query)
    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    rows = cursor.fetchall()

     # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    matches = []
    print(rows)
    for row in rows:
        matches.append(convertDataToMatchInfo(row))
    return matches

def retrieve_next_match_by_team(team_id:str) -> List[match_responses.MatchInfo]:
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = f"select * from Matches where {TABLE.TEAM_ID} = {team_id} and {TABLE.TABLE_NAME}.{TABLE.DATE}>= CURRENT_DATE() order by {TABLE.TABLE_NAME}.{TABLE.DATE} asc" 
    print(insert_query)
    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    rows = cursor.fetchone()

     # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    matches = []
    
    matches.append(convertDataToMatchInfo(rows))
    return matches

def convertDataToMatchInfo(data):
    return match_responses.MatchInfo(id=data[TABLE.ID],status=matches_state_machine.MatchState(data[f'{TABLE.STATUS}']),length=data[TABLE.LENGTH],opposition=data[TABLE.OPPOSITION],homeOrAway=match_responses.HomeOrAway(data[TABLE.HOME_OR_AWAY]),date=data[TABLE.DATE])
