import uuid


class Tournament:

    def __init__(self,
                name : str,
                location : str,
                start_date : str,
                end_date : str,
                description : str = "",
                registered_players = None,
                current_round = 0,
                rounds = None,
                nb_rounds : int = 4,
                finished : bool = False,
                uuid_value = None):
        
        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.current_round = current_round
        self.rounds = rounds
        self.registered_players = registered_players
        self.description = description
        self.nb_rounds = nb_rounds
        self.finished = finished
        self.uuid_value = uuid_value or str(uuid.uuid4())

    def __str__(self):                                           
        return f"""
        Nom : {self.name}
        Ville : {self.location}
        Date de démarrage : {self.start_date}
        Date de fin : {self.end_date}
        Description : {self.description}
        Nombre de rounds : {self.nb_rounds}
        Rounds : {self.rounds}
        """

    @staticmethod
    def from_dict(tournament_json_data):

        registered_players = []
        if tournament_json_data["registered_players"] is not None:
            for player in tournament_json_data["registered_players"]:
                player = Player(player["first_name"], player["last_name"], player["birth_date"], player["player_id"], player["uuid_value"])
                registered_players.append(player)

        return Tournament(
                        tournament_json_data["name"],
                        tournament_json_data["location"],
                        tournament_json_data["start_date"],
                        tournament_json_data["end_date"],
                        tournament_json_data["description"],
                        registered_players if registered_players else None,
                        tournament_json_data["current_round"],
                        tournament_json_data["rounds"],
                        tournament_json_data["nb_rounds"],
                        tournament_json_data["finished"],
                        tournament_json_data["uuid_value"]
        )

    def to_dict(self):
        
        tournament_data =  {
            "name" : self.name,
            "location" : self.location,
            "start_date" : self.start_date,
            "end_date" : self.end_date,
            "current_round" : self.current_round,
            "rounds" : self.rounds,
            "registered_players" : self.registered_players,
            "description" : self.description,
            "nb_rounds" : self.nb_rounds,
            "finished" : self.finished,
            "uuid_value" : self.uuid_value
            }
        
        if self.registered_players:
            tournament_data["registered_players"] = []


            for player in self.registered_players:
                player_data = {
                        "first_name" : player.first_name,
                        "last_name" : player.last_name,
                        "birth_date" : player.birth_date,
                        "player_id" : player.player_id,
                        "uuid_value" : player.uuid_value
                        }
                tournament_data["registered_players"].append(player_data)

        return tournament_data
    
class Round:

    def __init__(self,
                 match_list : list[Match],
                 round_number : str,
                 start_round : str,
                 end_round : str ):
    
        self._match_list = match_list
        self._round_number = round_number
        self._start_round = start_round
        self._end_round = end_round
        pass

class Match:

    def __init__(self,
                 player1 : Player,
                 player2: Player,
                 score_player1 : float = None,
                 score_player2 : float = None):
        
        if (score_player1 is None) != (score_player2 is None):
            raise ValueError ("Impossible de ne définir qu'un des deux scores")
        
        self.player1 = player1
        self.player2 = player2
        self.score_player1 = score_player1
        self.score_player2 = score_player2

    def __str__(self):
        if self._score_player1 or self._score_player2 is None:
            return f"""
            Match à venir :
            ID : {self._player1.player_id} {self._player1._first_name} {self._player1.last_name}
            vs
            ID : {self._player1.player_id} {self._player1._first_name} {self._player1.last_name}
            """
        else:
            return f"""
            Résultats du match :
            ID : {self._player1.player_id} {self._player1._first_name} {self._player1.last_name} : {self._score_player1}
            vs
            ID : {self._player1.player_id} {self._player1._first_name} {self._player1.last_name} : {self._score_player2}
            """
        
class Player:
    
    def __init__(self,
                 first_name : str,
                 last_name : str,
                 birth_date : str,
                 player_id : str,
                 uuid_value = None):

        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.player_id = player_id
        self.uuid_value = uuid_value or str(uuid.uuid4())

    def __str__(self):
        return f"ID : {self.player_id} - {self.first_name} {self.last_name} / Date de naissance : {self.birth_date}"
    
    @property
    def first_name(self):
        return self._first_name
    
    @first_name.setter
    def first_name(self, value):
        self._first_name = value
    
    @property
    def last_name(self):
        return self._last_name
    
    @last_name.setter
    def last_name(self, value):
        self._last_name = value
    
    @property
    def birth_date(self):
        return self._birth_date
    
    @birth_date.setter
    def birth_date(self, value):
        self._birth_date = value
    
    @property
    def player_id(self):
        return self._player_id
    
    @player_id.setter
    def player_id(self, value):
        self._player_id = value

    @staticmethod
    def from_dict(json_data):
        players_list = []
        
        for element in json_data:
            player = Player(
                element["first_name"],
                element["last_name"],
                element["birth_date"],
                element["player_id"],
                element["uuid_value"]
            )
            players_list.append(player)

        return players_list

    def to_dict(self):
        return {
            "first_name" : self.first_name,
            "last_name" : self.last_name,
            "birth_date" : self.birth_date,
            "player_id" : self.player_id,
            "uuid_value" : self.uuid_value
            }