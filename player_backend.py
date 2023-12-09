
from pydantic import TypeAdapter
from classes import Player

from player_data import save_player_season,save_player,retrieve_players_by_team,delete_player,retrieve_player,squad_size_by_team


async def create_players(name, team_id):
    
        request_player = Player(name=name,team_id=team_id)
        PlayerValidator = TypeAdapter(Player)

        try:
            new_player = PlayerValidator.validate_python(request_player)
            id = await save_player(new_player)
            player_season_id = await save_player_season(id,team_id)
            result = await retrieve_player(player_season_id)
            return result[0]

        except Exception as e:
            raise



