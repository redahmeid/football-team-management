SELECT 
    Players.ID, 
    Players.Name,
    Players_Seasons.ID AS Season_ID,
    SUM(DISTINCT CASE WHEN Player_Ratings.POTM = 'TRUE' THEN 1 ELSE 0 END) AS POTM_Count,
    COALESCE(COUNT(DISTINCT CASE WHEN Goals.Player_ID = Players_Seasons.ID THEN Goals.ID END), 0) AS GoalCount,
    COALESCE(COUNT(DISTINCT CASE WHEN Goals.Assister_ID = Players_Seasons.ID THEN Goals.ID END), 0) AS AssistCount,
    COALESCE(AVG(Player_Ratings.Rating), 0) AS AverageRating
FROM Players
INNER JOIN Players_Seasons ON Players_Seasons.Player_ID = Players.ID 
    AND Players_Seasons.Team_Season_ID = 86062
LEFT JOIN Goals ON Goals.Player_ID = Players_Seasons.ID 
    OR Goals.Assister_ID = Players_Seasons.ID
LEFT JOIN Player_Ratings ON Player_Ratings.Player_ID = Players_Seasons.ID
GROUP BY Players_Seasons.ID, Players.Name 
ORDER BY GoalCount DESC;


SELECT 
    Players.ID, 
    Players.Name, 
    Players_Seasons.ID, 
    COALESCE(COUNT(DISTINCT CASE WHEN Goals.Player_ID = Players_Seasons.ID THEN Goals.ID END),0) AS GoalCount, 
    COALESCE(COUNT(DISTINCT CASE WHEN Goals.Assister_ID = Players_Seasons.ID THEN Goals.ID END),0) AS AssistCount, 
        COALESCE(AVG(Player_Ratings.Rating),0) AS AverageRating 
FROM Players 
INNER JOIN Players_Seasons ON Players_Seasons.Player_ID = Players.ID 
    fAND Players_Seasons.Team_Season_ID = {team_id} 
LEFT JOIN Goals ON Goals.Player_ID = Players_Seasons.ID 
    OR Goals.Assister_ID = Players_Seasons.ID 
LEFT JOIN Player_Ratings ON Player_Ratings.Player_ID = Players_Seasons.ID 
GROUP BY Players_Seasons.ID, Players.Name 
ORDER BY GoalCount DESC


SELECT Players.ID, Players.Name, Players_Seasons.ID, SUM(DISTINCT CASE WHEN Player_Ratings.POTM = 'TRUE' THEN 1 ELSE 0 END) AS POTM_Count, COALESCE(COUNT(DISTINCT CASE WHEN Goals.Player_ID = Players_Seasons.ID THEN Goals.ID END),0) AS GoalCount, COALESCE(COUNT(DISTINCT CASE WHEN Goals.Assister_ID = Players_Seasons.ID THEN Goals.ID END),0) AS AssistCount, COALESCE(AVG(Player_Ratings.Rating),0) AS AverageRating, COALESCE(AVG(Player_Ratings.Technical),0) AS AverageTech, COALESCE(AVG(Player_Ratings.Physical),0) AS AveragePhys, COALESCE(AVG(Player_Ratings.Psychological),0) AS AveragePsych, COALESCE(AVG(Player_Ratings.Social),0) AS AverageSocial FROM Players INNER JOIN Players_Seasons ON Players_Seasons.Player_ID = Players.ID AND Players_Seasons.Team_Season_ID = 86062 LEFT JOIN Goals ON Goals.Player_ID = Players_Seasons.ID OR Goals.Assister_ID = Players_Seasons.ID LEFT JOIN Player_Ratings ON Player_Ratings.Player_ID = Players_Seasons.ID GROUP BY Players_Seasons.ID, Players.Name ORDER BY GoalCount DESC

SELECT Players.ID, Players.Name, Players_Seasons.ID, Roles.Email as parent, COALESCE(COUNT(DISTINCT CASE WHEN Goals.Player_ID = Players_Seasons.ID THEN Goals.ID END),0) AS GoalCount, COALESCE(COUNT(DISTINCT CASE WHEN Goals.Assister_ID = Players_Seasons.ID THEN Goals.ID END),0) AS AssistCount, COALESCE(AVG(Player_Ratings.Rating),0) AS AverageRating FROM Players INNER JOIN Players_Seasons ON Players_Seasons.Player_ID = Players.ID AND Players_Seasons.Team_Season_ID = 32390 LEFT JOIN Goals ON Goals.Player_ID = Players_Seasons.ID OR Goals.Assister_ID = Players_Seasons.ID LEFT JOIN Player_Ratings ON Player_Ratings.Player_ID = Players_Seasons.ID LEFT JOIN Roles ON Players_Seasons.ID=Roles.Player_ID GROUP BY Players_Seasons.ID, Players.Name, Roles.Email ORDER BY GoalCount DESC;
