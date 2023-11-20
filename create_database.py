from config import app_config
import db
import match_day_data
import matches_data



def create_database():
    try:
        # Define the SQL query to insert data into a table
        insert_query = "CREATE database %s" %(app_config.database)
        print(insert_query)
        connection = db.connection()
        print("CREATE DATABASE IN %s" %(connection.db))     
        # Create a cursor object to interact with the database
        cursor = connection.cursor()

        
        

        # Execute the SQL query to insert data
        cursor.execute(insert_query)

        # Commit the transaction
        connection.commit()
        # Close the cursor and connection
        cursor.close()
        connection.close()
        
        # create_teams_table()
    except Exception as e:
        print(e)
    
    create_teams_table()
    create_tables(matches_data.TABLE.createTable())
    create_players_table()
    create_users_table()
    create_team_users_table()
    create_tables(match_day_data.PLANNED_LINEUP_TABLE.createTable())
    create_tables(match_day_data.ACTUAL_LINEDUP_TABLE.createTable())
    create_tables(match_day_data.MATCH_STATUS_TABLE.createTable())
    

def create_tables(sql):
    print(sql)
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

   
    # Execute the SQL query to insert data
    cursor.execute(sql)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

def create_teams_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Teams" \
        "(ID varchar(255),"\
        "Name varchar(255) NOT NULL,"\
        "AgeGroup varchar(255) NOT NULL,"\
        "live VARCHAR(255),"\
        "PRIMARY KEY (ID))"


    print(insert_query)
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

   
    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

def create_users_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Users" \
        "(ID varchar(255),"\
        "Email varchar(255) NOT NULL Unique,"\
        "live VARCHAR(255),"\
        "PRIMARY KEY (ID))"


    print(insert_query)
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

   
    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

def create_team_users_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Roles" \
        "(ID varchar(255),"\
        "Email varchar(255),"\
        "Team_ID varchar(255),"\
        "Role varchar(255),"\
        "live VARCHAR(255),"\
        "PRIMARY KEY (ID),"\
        "FOREIGN KEY(Email) references Users(Email),"\
        "FOREIGN KEY(Team_ID) references Teams(ID))"


    print(insert_query)
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

   
    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

def create_players_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Players" \
        "(ID varchar(255),"\
        "Name varchar(255) NOT NULL,"\
        "Team_ID varchar(255) NOT NULL,"\
        "Email varchar(255),"\
        "live varchar(255),"\
        "PRIMARY KEY (ID),"\
        "FOREIGN KEY(Team_ID) references Teams(ID))"


    print(insert_query)
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

   
    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

def alter_players_table(field_name,data_type):
     # Define the SQL query to insert data into a table
    insert_query = "alter TABLE Players ADD %s %s"%(field_name,data_type)

    print(insert_query)

    
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

   
    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    describe_query = "describe Players"

    print(describe_query)

   
    # Execute the SQL query to insert data
    cursor.execute(describe_query)
    row = cursor.fetchall()

    print(row)
    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

def create_matches_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Matches" \
        "(ID varchar(255),"\
        "Opposition varchar(255) NOT NULL,"\
        "Team_ID varchar(255) NOT NULL,"\
        "HomeOrAway varchar(255),"\
        "Date datetime,"\
        "Status varchar(255),"\
        "Goals_For int,"\
        "Goals_Against int,"\
        "Length int,"\
        "PRIMARY KEY (ID),"\
        "FOREIGN KEY(Team_ID) references Teams(ID))"


    print(insert_query)
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

   
    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

def create_match_day_lineup_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Match_Day_Lineup" \
        "(ID varchar(255),"\
        "Match_ID varchar(255) NOT NULL,"\
        "Player_ID varchar(255) NOT NULL,"\
        "Subbed_On int,"\
        "Subbed_Off int,"\
        "Position varchar(255),"\
        "PRIMARY KEY (ID),"\
        "FOREIGN KEY(Match_ID) references Matches(ID),"\
        "FOREIGN KEY(Player_ID) references Players(ID))"


    print(insert_query)
    connection = db.connection(app_config.database)
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

   
    # Execute the SQL query to insert data
    cursor.execute(insert_query)

    # Commit the transaction
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

