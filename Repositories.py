from pathlib import Path
import json
import Models


class TournamentRepository:

    def __init__(self, dir_path : str):
        self.dir_path = dir_path

    @property
    def dir_path(self):
        return self._dir_path

    @dir_path.setter
    def dir_path(self, value):
        self._dir_path = value

    def load_all(self):
        try:
            with open (self._dir_path, "r", encoding="utf8") as f:
                return (json.load(f))
        
        except (FileNotFoundError, json.JSONDecodeError):
            print("Le fichier est introuvable ou illisible")
    
    def save_tournament(self, data):
        with open (self._dir_path, "w", encoding="utf8") as f:
            json.dump(data, f, indent= 4)



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
                database = Models.Player.from_dict(json.load(f))
                return database
        
        except (FileNotFoundError, json.JSONDecodeError):
            print("Le fichier est introuvable ou illisible")

    def save_player_modification(self, players_dict):
        for player in players_dict:
            database = player.todict()
            
        with open(self._file_path, "w", encoding="utf8") as f:
            json.dump(database, f, indent= 4)