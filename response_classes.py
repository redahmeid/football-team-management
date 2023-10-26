from pydantic import BaseModel, validator
from typing import Optional, List
from validators import validate_email,validate_short_name
import datetime

class Link(BaseModel):
    link:str
    method:str

class MatchResponse(BaseModel):
    id:str
    opposition:str
    homeOrAway:str
    date:datetime.date
    self:Link

class PlayerResponse(BaseModel):
    id:str
    name:str
    live:bool
    self:Link
    deletePlayer:Link

# (ID varchar(255),"\
#         "Name varchar(255) NOT NULL,"\
#         "Short_Name varchar(255) NOT NULL,"\
#         "Email varchar(255),"\
#         "Phone varchar(255)NOT NULL,"\
class ClubResponse(BaseModel):
    id:str
    name:str
    shortName:str
    email:str
    phone:str
    self:Link
    createTeams:Link
    listTeams:Link

class TeamResponse(BaseModel):
    id:str
    name:str
    ageGroup:str
    clubId:str
    email:str
    live:bool
    self:Link
    nextMatch:Link        #save_response["next_match"] = {"ID":match["ID"],"opposition":match["Opposition"],"date":match["Date"].isoformat(),"homeOrAway":match["HomeOrAway"], "club_name":match["c.Name"], "team_name":match["Name"], "age_group":match["AgeGroup"]}
    teamPlayers:Link        #save_response["players"] = {"link":"/teams/%s/players"%(save_response["ID"]),"method":"get"}
    teamFixtures:Link        #save_response["fixtures"] = {"link":"/teams/%s/matches"%(save_response["ID"]),"method":"get"}
    addPlayers:Link        #save_response["addPlayers"] = {"link":"/teams/%s/players"%(save_response["ID"]),"method":"post"}
    addFixtures:Link        #save_response["addFixtures"] = {"link":"/teams/%s/matches"%(save_response["ID"]),"method":"post"}
   