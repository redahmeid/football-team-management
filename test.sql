SELECT Players.ID, Players.Name, Players_Seasons.ID, Players_Seasons.Team_Season_ID, SUM(DISTINCT CASE WHEN Player_Ratings.POTM = 'TRUE' THEN 1 ELSE 0 END) AS POTM_Count, COALESCE(COUNT(DISTINCT CASE WHEN Goals.Player_ID = Players_Seasons.ID THEN Goals.ID END),0) AS GoalCount, COALESCE(COUNT(DISTINCT CASE WHEN Goals.Assister_ID = Players_Seasons.ID THEN Goals.ID END),0) AS AssistCount, COALESCE(AVG(Player_Ratings.Rating),0) AS AverageRating, COALESCE(AVG(Player_Ratings.Technical),0) AS AverageTech, COALESCE(AVG(Player_Ratings.Physical),0) AS AveragePhys, COALESCE(AVG(Player_Ratings.Psychological),0) AS AveragePsych, COALESCE(AVG(Player_Ratings.Social),0) AS AverageSocial FROM Players INNER JOIN Players_Seasons ON Players_Seasons.Player_ID = Players.ID LEFT JOIN Goals ON Goals.Player_ID = Players_Seasons.ID OR Goals.Assister_ID = Players_Seasons.ID LEFT JOIN Player_Ratings ON Player_Ratings.Player_ID = Players_Seasons.ID INNER JOIN Roles ON Roles.Player_ID = Players_Seasons.ID and Roles.Email='r.hmeid+dev@gmail.com' GROUP BY Players_Seasons.ID, Players.Name, Players_Seasons.Team_Season_ID ORDER BY GoalCount DESC;


SELECT 
  m.ID, 
  al.*
  -- m.Goals_For, 
  -- m.Goals_Against,
  -- m.Status,
  -- m.Type,
  -- m.HomeOrAway,
  -- m.Date,
  -- m.Captain,
  -- m.Length,
  -- m.Team_ID,
  -- m.Opposition,
  -- m.Time_Started,
  -- GROUP_CONCAT(DISTINCT CONCAT(p1.Name, '-', ps1.ID, '-', CAST(g.Time AS DECIMAL(10, 2)), '-', IFNULL(p2.Name, ''), '-', IFNULL(p2.ID, ''),'-',g.Type,'-',g.Assist_Type) SEPARATOR ',') AS Scorers,
  -- GROUP_CONCAT(DISTINCT CONCAT(o.Time) SEPARATOR ',') AS Conceded,
  -- GROUP_CONCAT(DISTINCT CONCAT(p3.Name, '-', pl.Player_ID, '-', pl.Minute, '-', pl.Position) SEPARATOR ',') AS Planned_Lineups,
  -- GROUP_CONCAT(DISTINCT CONCAT(p4.Name, '-', r.Player_ID, '-', r.Rating) SEPARATOR ',') AS Ratings,
  -- GROUP_CONCAT(DISTINCT CONCAT(p5.Name, '-', al.Player_ID, '-', CAST(al.Time AS DECIMAL(10, 2)), '-', al.Position) SEPARATOR ',') AS Actual_Lineups
FROM Matches AS m
-- LEFT JOIN Goals AS g ON g.Match_ID = m.ID

-- LEFT JOIN Players_Seasons ps1 ON g.Player_ID = ps1.ID
-- LEFT JOIN Players p1 ON p1.ID = ps1.Player_ID

-- LEFT JOIN Players_Seasons ps2 ON g.Assister_ID = ps2.ID
-- LEFT JOIN Players p2 ON p2.ID = ps2.Player_ID

-- LEFT JOIN Planned_Lineups pl ON pl.Match_ID = m.ID
-- LEFT JOIN Players_Seasons ps3 ON pl.Player_ID = ps3.ID
-- LEFT JOIN Players p3 ON p3.ID = ps3.Player_ID

-- LEFT JOIN Player_Ratings r ON r.Match_ID = m.ID
-- LEFT JOIN Players_Seasons ps4 ON r.Player_ID = ps4.ID
-- LEFT JOIN Players p4 ON p4.ID = ps4.Player_ID

LEFT JOIN Actual_Lineups al ON al.Match_ID = m.ID
LEFT JOIN Players_Seasons ps5 ON al.Player_ID = ps5.ID
-- LEFT JOIN Players p5 ON p5.ID = ps5.Player_ID

-- LEFT JOIN Opposition_Goals AS o ON o.Match_ID = m.ID

where m.Team_ID=86062 and Status = 'end' or Status = 'rated'
GROUP BY m.ID, al.ID;

SELECT 
  m.ID AS MatchID,
  m.Goals_For, 
  GROUP_CONCAT(DISTINCT CONCAT(p.Name, '-', g.Player_ID, '-', g.Time, '-', IFNULL(p2.Name, 'No Assister')) SEPARATOR ',') AS Scorers,
  GROUP_CONCAT(DISTINCT CONCAT(p1.Name, '-', pl.Player_ID, '-', pl.Minute) SEPARATOR ',') AS Planned_Lineups,
  GROUP_CONCAT(DISTINCT CONCAT(p3.Name, '-', al.Player_ID) SEPARATOR ',') AS Actual_Lineups
FROM Matches AS m
LEFT JOIN Goals AS g ON g.Match_ID = m.ID
LEFT JOIN Players p ON p.ID = g.Player_ID
LEFT JOIN Players p2 ON p2.ID = g.Assister_ID
LEFT JOIN Planned_Lineups pl ON pl.Match_ID = m.ID
LEFT JOIN Players p1 ON p1.ID = pl.Player_ID
LEFT JOIN Actual_Lineups al ON al.Match_ID = m.ID
LEFT JOIN Players p3 ON p3.ID = al.Player_ID
GROUP BY m.ID;


SELECT 
  m.ID,
  GROUP_CONCAT( CONCAT(p.Name, '-', pl.Player_ID, '-', pl.Minute, '-', IFNULL(pl.Position, 'No Position')) SEPARATOR ',') AS Planned_Lineups
FROM Matches AS m
LEFT JOIN Planned_Lineups pl ON pl.Match_ID = m.ID
LEFT JOIN Players p ON p.ID = pl.Player_ID
WHERE m.ID = '6479009'
GROUP BY m.ID;



-- Assuming there's a 'Players' table with player details
-- and a 'Goals' table with goal scorer information

SELECT 
  m.ID AS MatchID,
  m.Opposition,
  p.Name AS PlayerName,
  CASE 
    WHEN pl.Player_ID IS NOT NULL THEN 'Planned'
    WHEN al.Player_ID IS NOT NULL THEN 'Actual'
  END AS LineupType,
  g.Time AS GoalTime
FROM Matches m
LEFT JOIN Planned_Lineups pl ON m.ID = pl.Match_ID
LEFT JOIN Actual_Lineups al ON m.ID = al.Match_ID
JOIN Players p ON p.ID = pl.Player_ID OR p.ID = al.Player_ID
LEFT JOIN Goals g ON m.ID = g.Match_ID AND p.ID = g.Player_ID
ORDER BY LineupType, GoalTime;
