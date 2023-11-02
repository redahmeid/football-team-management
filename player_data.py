from classes import Club, Team,Player
from config import app_config
import id_generator
import db

# # "CREATE TABLE Players" \
#         "(ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "Team_ID varchar(255) NOT NULL,"\
#         "Email varchar(255),"\
#         "PRIMARY KEY (ID),"\
#         "FOREIGN KEY(Team_ID) references Teams(ID))"

def save_player(player:Player):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "INSERT INTO Players (ID,Name,Team_ID,live) VALUES (%s,%s,%s,'true')"

    # Data to be inserted
    id = id_generator.generate_random_number(5)
    data_to_insert = (id,player.name,player.team_id)

    # Execute the SQL query to insert data
    cursor.execute(insert_query, data_to_insert)
    row_count = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    return id



def retrieve_players_by_team(team_id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Players where Team_ID = %s and live <> 'false' or live IS NULL" 
    print(insert_query)
    # Execute the SQL query to insert data
    cursor.execute(insert_query,team_id)
    row = cursor.fetchall()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(row)
    return row

def delete_player(player_id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "update Players set live='false' where ID='%s'" %(player_id)

    print(insert_query)
    # Execute the SQL query to insert data
    cursor.execute(insert_query)
    row = cursor.rowcount
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(row)
    return row

def retrieve_player(id:str):
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query to insert data into a table
    insert_query = "select * from Players as p where p.ID = %s and p.live <> 'false'" 

    # Execute the SQL query to insert data
    cursor.execute(insert_query,id)
    row = cursor.fetchone()
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()
    # club = Club(id=id,name=row)
    print(row)
    return row

if __name__ == "__main__":
    retrieve_players_by_team("18071")
    # retrieve_player("29308")