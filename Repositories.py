from pathlib import Path
import json
import Models


class TournamentRepository:

    def __init__(self, file_path : str):
        self.file_path = file_path

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    def load_all(self):
        try:
            with open (self._file_path, "r", encoding="utf8") as f:
                data = json.load(f)
                return Models.Tournament.from_dict(data)
        
        except (FileNotFoundError, json.JSONDecodeError):
            print("Le fichier est introuvable ou illisible")
            return []
    
    def save_tournaments(self, tournament_list):

        Path(self._file_path).parent.mkdir(parents=True, exist_ok=True)

        with open (self._file_path, "w", encoding="utf8") as f:
            json.dump([t.to_dict() for t in tournament_list], f, indent= 4)



class PlayerRepository:

    def __init__(self, file_path : str):
        self.file_path = file_path
    
    @property
    def file_path(self):
        return self._file_path
    
    @file_path.setter
    def file_path(self, value):
        self._file_path = value
    
    def load_all(self):
        try:
            with open (self._file_path, "r", encoding="utf8") as f:
                data = json.load(f)
                return Models.Player.from_dict(data)
        
        except (FileNotFoundError, json.JSONDecodeError):
            print("Le fichier est introuvable ou illisible")
            return []

    def save_players(self, players_list):
        
        Path(self._file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(self._file_path, "w", encoding="utf8") as f:
            json.dump([p.to_dict() for p in players_list], f, indent= 4)