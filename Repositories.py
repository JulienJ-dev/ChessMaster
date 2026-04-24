from pathlib import Path
import json
import Models


class TournamentRepository:

    def __init__(self, file_path: str, tournaments: list = None):
        self.file_path = file_path
        self.tournaments = tournaments if tournaments is not None else []

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    def load_all(self, bootload: bool = False):
        try:
            with open(self._file_path, "r", encoding="utf8") as f:
                data = json.load(f)
                self.tournaments = [Models.Tournament.from_dict(item) for item in data]
                return self.tournaments
        except (FileNotFoundError, json.JSONDecodeError):
            if not bootload:
                print("Le fichier est introuvable ou illisible")
            return self.tournaments

    def update_tournament(self, modified_tournament: Models.Tournament):
        for i, tournament in enumerate(self.tournaments, start=0):
            if tournament.uuid_value == modified_tournament.uuid_value:
                self.tournaments[i] = modified_tournament
                break
        self.save_tournaments()

    def add_tournament(self, new_tournament: Models.Tournament):
        self.tournaments.append(new_tournament)
        self.save_tournaments()

    def save_tournaments(self):
        Path(self._file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self._file_path, "w", encoding="utf8") as f:
            json.dump([t.to_dict() for t in self.tournaments], f, indent=4)

    def save_backup(self):
        backup_path = Path(self._file_path).with_suffix(".backup.json")
        with open(backup_path, "w", encoding="utf8") as f:
            json.dump([t.to_dict() for t in self.tournaments], f, indent=4)

    def restore_backup(self):
        backup_path = Path(self._file_path).with_suffix(".backup.json")
        if not backup_path.exists():
            raise FileNotFoundError("Aucune sauvegarde disponible")
        with open(backup_path, "r", encoding="utf8") as f:
            data = json.load(f)
            self.tournaments = [Models.Tournament.from_dict(item) for item in data]
        self.save_tournaments()


class PlayerRepository:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.players = []

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    def load_all(self, bootload: bool = False):
        try:
            with open(self._file_path, "r", encoding="utf8") as f:
                data = json.load(f)
                self.players = Models.Player.from_dict(data)
                return self.players
        except (FileNotFoundError, json.JSONDecodeError):
            if not bootload:
                print("La base de données des joueurs est introuvable ou illisible")
            return self.players

    def add_player(self, new_player: Models.Player):
        self.players.append(new_player)
        self.save_players()

    def update_player(self, modified_player: Models.Player):
        for i, player in enumerate(self.players, start=0):
            if player.uuid_value == modified_player.uuid_value:
                self.players[i] = modified_player
                break
        self.save_players()

    def save_players(self):
        Path(self._file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self._file_path, "w", encoding="utf8") as f:
            json.dump([p.to_dict() for p in self.players], f, indent=4)

    def save_backup(self):
        backup_path = Path(self._file_path).with_suffix(".backup.json")
        with open(backup_path, "w", encoding="utf8") as f:
            json.dump([p.to_dict() for p in self.players], f, indent=4)

    def restore_backup(self):
        backup_path = Path(self._file_path).with_suffix(".backup.json")
        if not backup_path.exists():
            raise FileNotFoundError("Aucune sauvegarde disponible")
        with open(backup_path, "r", encoding="utf8") as f:
            data = json.load(f)
            self.players = Models.Player.from_dict(data)
        self.save_players()
