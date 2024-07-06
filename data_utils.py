import response_classes
import classes
# (ID varchar(255),"\
#         "Opposition varchar(255) NOT NULL,"\
#         "Team_ID varchar(255) NOT NULL,"\
#         "HomeOrAway varchar(255),"\
#         "Date datetime,"\
#         "Team_Size int NOT NULL,"\
def convertMatchDatatoMatchResponse(match) -> response_classes.MatchResponse:
    print(match)
    # /teams/{team_id}/matches/{match_id}/players/submit_lineup
    id = match["ID"]
    lineupStatus = match["Status"]
    if(lineupStatus == None):
        lineupStatus = "Draft"
    length = match["Length"]
    baseUrl = "/teams/%s/matches/%s"%(match["Team_ID"],match["ID"])
    opposition = match["Opposition"]
    homeOrAway = match["HomeOrAway"]
    date=match["Date"]
    self = response_classes.Link(link=baseUrl,method="get")
    submitUrl = "%s/lineup_confirmed"%(baseUrl)
    submitLineup = response_classes.Link(link=submitUrl,method="patch")

    response =  response_classes.MatchResponse(id=id,opposition=opposition,homeOrAway=homeOrAway,date=date,self=self, length=length,status=lineupStatus,submitLineup=submitLineup)
    print("Convert Match %s"%(response))
    return response.model_dump()

def convertPlayerDataToPlayerResponse(player) -> classes.Player:
    
    id = player["ID"]
    baseTeamUrl = "/players/%s"%(id)
    name = player["Name"]
    live = player["live"]
    if(live == None):
        live = True
    self = response_classes.Link(link=baseTeamUrl,method="get")
    deletePlayer = response_classes.Link(link=baseTeamUrl,method="delete")
    response =  response_classes.classes.Player(id=id,name=name,live=live,self=self,deletePlayer=deletePlayer)
    print("Convert player %s"%(response))
    return response.model_dump()


def convertPlayerDataToLineupPlayeResponser(player,isSelected,baseUrl,position,team_id,match_id,selection_id) -> response_classes.SelectedPlayer:
    
    id = player["mdl.ID"]
    
    name = player["Name"]
    position=position
    live = player["live"]
    url = "%s/players/%s"%(baseUrl,id)
    if(live == None):
        live = True
    self = response_classes.Link(link=url,method="get")
    
    
    subOnOff = response_classes.Link(link=url,method="patch")
    response =  response_classes.Selectedclasses.Player(id=id,selectionId=selection_id,name=name,live=live,self=self,position=position,toggleStarting=subOnOff,isSelected=isSelected)
    print("Convert player %s"%(response))
    return response.model_dump()

def convertTeamDataToTeamResponse(team) -> response_classes.TeamResponse:
    print("convertTeamDataToTeamResponse: %s"%(team))
    id = team["ID"]
    baseTeamUrl = "/teams/%s"%(id)
    name = team["Name"]
    ageGroup = team["AgeGroup"]
    live = team["live"]
    print("Convert team live %s"%(live))
    if(live == None):
        live = True
    self = response_classes.Link(link=baseTeamUrl,method="get")
    players = response_classes.Link(link="%s/players"%(baseTeamUrl),method="get")
    fixtures= response_classes.Link(link="%s/matches"%(baseTeamUrl),method="get")
    addPlayers = response_classes.Link(link="%s/players"%(baseTeamUrl),method="post")
    addFixtures = response_classes.Link(link="%s/matches"%(baseTeamUrl),method="post")
    nextMatch = response_classes.Link(link="%s/next_match"%(baseTeamUrl),method="get")

    response =  response_classes.TeamResponse(id=id,name=name,ageGroup=ageGroup,live=live,self=self,nextMatch=nextMatch,teamPlayers=players,teamFixtures=fixtures,addFixtures=addFixtures,addPlayers=addPlayers)
    print("Convert team %s"%(response))
    return response.model_dump()