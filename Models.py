class Tournament:

    def __init__(self,
                name : str,
                location : str,
                start_date : str,
                end_date : str,
                registered_players : list,
                description : str = "",
                rounds : list = [],
                nb_rounds : int = 4,
                finished : bool = False):
        
        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.current_round = 0
        self.rounds = rounds
        self.registered_players = registered_players
        self.description = description
        self.nb_rounds = nb_rounds
        self.finished = finished

    def __str__(self):
        return f"""
        Nom : {self.name}
        Ville : {self.location}
        Date de démarrage : {self.start_date}
        Date de fin : {self.end_date}
        Participants : {self.registered_players}
        Description : {self.description}
        Nombre de rounds : {self.nb_rounds}
        Rounds : {self.rounds}
        """



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
                 player_id : str):

        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.player_id = player_id

    def __str__(self):
        return f"ID : {self._player_id} - {self._first_name} {self._last_name} / Date de naissance : {self._birth_date}"
    
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

    def from_dict(self, json_data):
        for element in json_data:
            player = Player(
                element["first_name"],
                element["last_name"],
                element["birth_date"],
                element["player_id"]
            )
        return player

    def to_dict(self):
        return {
            "first_name" : self.first_name,
            "last_name" : self.last_name,
            "birth_date" : self.birth_date,
            "player_id" : self._player_id
            }