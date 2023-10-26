from config import app_config
import db



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
    
    create_clubs_table()
    create_admins_table()
    create_teams_table()
    create_matches_table()
    create_players_table()
    create_planned_match_day_squad_table()
   
    


def create_clubs_table():
    try:
         # Define the SQL query to insert data into a table
        insert_query = "CREATE TABLE Clubs" \
        "(ID varchar(255),"\
        "Name varchar(255) NOT NULL,"\
        "Short_Name varchar(255) NOT NULL,"\
        "Email varchar(255),"\
        "Phone varchar(255)NOT NULL,"\
        "PRIMARY KEY (ID))"

        print(insert_query)
        connection = db.connection(app_config.database)
        print("CREATE TABLE IN %s" %(connection.db))
        # Create a cursor object to interact with the database
        cursor = connection.cursor()

    

        # Execute the SQL query to insert data
        cursor.execute(insert_query)

        # Commit the transaction
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()
    except Exception as e:
        print(e)

def create_admins_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Admins" \
        "(ID varchar(255),"\
        "Name varchar(255) NOT NULL,"\
        "Email varchar(255) NOT NULL,"\
        "Phone varchar(255),"\
        "Club_ID varchar(255),"\
        "Team_ID varchar(255),"\
        "Role varchar(255),"\
        "PRIMARY KEY (ID),"\
        "FOREIGN KEY(Club_ID) references Clubs(ID))"


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

def create_teams_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Teams" \
        "(ID varchar(255),"\
        "Name varchar(255) NOT NULL,"\
        "AgeGroup varchar(255) NOT NULL,"\
        "Email varchar(255) NOT NULL,"\
        "Club_ID varchar(255) NOT NULL,"\
        "live VARCHAR(255),"\
        "PRIMARY KEY (ID),"\
        "FOREIGN KEY(Club_ID) references Clubs(ID))"


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
        "Team_Size int NOT NULL,"\
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

def create_planned_match_day_squad_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Planned_Match_Day_Squad" \
        "(ID varchar(255),"\
        "Match_ID varchar(255) NOT NULL,"\
        "Player_ID varchar(255) NOT NULL,"\
        "Start_Time_Minutes int,"\
        "End_Time_Minutes int,"\
        "Position varchar(255),"\
        "PRIMARY KEY (Match_ID,Player_ID,Start_Time_Minutes),"\
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

def create_actual_matches_players_table():
     # Define the SQL query to insert data into a table
    insert_query = "CREATE TABLE Matches" \
        "(ID varchar(255),"\
        "Match_ID varchar(255) NOT NULL,"\
        "Player_ID varchar(255) NOT NULL,"\
        "Start_Time time,"\
        "End_Time time,"\
        "Goals int,"\
        "Assists int,"\
        "Position varchar(255),"\
        "PRIMARY KEY (ID),"\
        "FOREIGN KEY(Match_ID) references Matches(ID))"\
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

