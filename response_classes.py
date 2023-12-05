from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from validators import validate_email,validate_short_name
import datetime
import match_responses
import player_responses

class Link(BaseModel):
    link:str
    method:str


class PlayerResponse(BaseModel):
    id:str
    name:str
    isSelected:bool=False
    live:bool
    self:Link
    deletePlayer:Link

class SelectedPlayerResponse(BaseModel):
    id:str
    selectionId:Optional[str]=None
    name:str
    isSelected:bool=False
    position:Optional[str]=None
    self:Link
    toggleStarting:Link

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
    fixtures:Optional[List] = []
    squad:Optional[List] = []
    coaches:Optional[List]=[]
    live:bool
    self:Link
    nextMatch:Link        #save_response["next_match"] = {"ID":match["ID"],"opposition":match["Opposition"],"date":match["Date"].isoformat(),"homeOrAway":match["HomeOrAway"], "club_name":match["c.Name"], "team_name":match["Name"], "age_group":match["AgeGroup"]}
    teamPlayers:Link        #save_response["players"] = {"link":"/teams/%s/players"%(save_response["ID"]),"method":"get"}
    teamFixtures:Link        #save_response["fixtures"] = {"link":"/teams/%s/matches"%(save_response["ID"]),"method":"get"}
    addPlayers:Link        #save_response["addPlayers"] = {"link":"/teams/%s/players"%(save_response["ID"]),"method":"post"}
    addFixtures:Link        #save_response["addFixtures"] = {"link":"/teams/%s/matches"%(save_response["ID"]),"method":"post"}

class MatchResponse(BaseModel):
    match:match_responses.MatchInfo
    players:Optional[List[player_responses.PlayerResponse]]=None
    links:Optional[Dict[str,Link]]=None

