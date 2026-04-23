import uuid


class Player:

    def __init__(self,
                 first_name: str,
                 last_name: str,
                 birth_date: str,
                 player_id: str,
                 uuid_value=None):

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
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_date": self.birth_date,
            "player_id": self.player_id,
            "uuid_value": self.uuid_value
        }


class Match:

    def __init__(self,
                 player1: Player,
                 player2: Player,
                 player1_result: str = None,
                 player2_result: str = None,
                 player1_score: float = None,
                 player2_score: float = None,
                 finished: bool = False):

        self.player1 = player1
        self.player2 = player2
        self.player1_result = player1_result
        self.player2_result = player2_result
        self.player1_score = player1_score
        self.player2_score = player2_score
        self.finished = finished

    def __str__(self):
        if not self.finished:
            return (
                f"Match à venir :\n"
                f"  {self.player1.player_id} {self.player1.first_name} {self.player1.last_name}\n"
                f"  vs\n"
                f"  {self.player2.player_id} {self.player2.first_name} {self.player2.last_name}"
            )
        else:
            return (
                f"Résultats du match :\n"
                f"  {self.player1.player_id} {self.player1.first_name} {self.player1.last_name}"
                f" : {self.player1_result} --> {self.player1_score} pt\n"
                f"  vs\n"
                f"  {self.player2.player_id} {self.player2.first_name} {self.player2.last_name}"
                f" : {self.player2_result} --> {self.player2_score} pt"
            )

    def to_tuple(self):
        return (
            [self.player1.to_dict(), self.player1_score],
            [self.player2.to_dict(), self.player2_score]
        )

    @staticmethod
    def from_tuple(data):
        p1_data, p1_score = data[0]
        p2_data, p2_score = data[1]
        player1 = Player(p1_data["first_name"], p1_data["last_name"],
                         p1_data["birth_date"], p1_data["player_id"], p1_data["uuid_value"])
        player2 = Player(p2_data["first_name"], p2_data["last_name"],
                         p2_data["birth_date"], p2_data["player_id"], p2_data["uuid_value"])
        finished = p1_score is not None

        def result(score):
            if score == 1.0:
                return "Victoire"
            if score == 0.5:
                return "Nul"
            if score == 0.0:
                return "Défaite"
            return None
        p1_result = result(p1_score)
        p2_result = result(p2_score)
        return Match(player1, player2, p1_result, p2_result, p1_score, p2_score, finished)


class Round:

    def __init__(self,
                 match_list: list,
                 round_number: str,
                 start_round: str,
                 end_round: str):

        self.match_list = match_list
        self.round_number = round_number
        self.start_round = start_round
        self.end_round = end_round

    def __str__(self):
        lines = [f"--- {self.round_number} ---",
                 f"Début : {self.start_round}  |  Fin : {self.end_round}"]
        for match in self.match_list:
            lines.append(str(match))
        return "\n".join(lines)

    def to_dict(self):
        return {
            "round_number": self.round_number,
            "start_round": self.start_round,
            "end_round": self.end_round,
            "match_list": [m.to_tuple() for m in self.match_list]
        }

    @staticmethod
    def from_dict(data):
        match_list = [Match.from_tuple(m) for m in data["match_list"]]
        return Round(match_list, data["round_number"], data["start_round"], data["end_round"])


class Tournament:

    def __init__(self,
                 name: str,
                 location: str,
                 start_date: str,
                 end_date: str,
                 description: str = "",
                 registered_players=None,
                 current_round: int = 0,
                 rounds=None,
                 nb_rounds: int = 4,
                 finished: bool = False,
                 uuid_value=None):

        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.current_round = current_round
        self.rounds = rounds if rounds is not None else []
        self.registered_players = registered_players if registered_players is not None else []
        self.description = description
        self.nb_rounds = nb_rounds
        self.finished = finished
        self.uuid_value = uuid_value or str(uuid.uuid4())

    def __str__(self):
        players_str = ", ".join(
            f"{p.first_name} {p.last_name}" for p in self.registered_players
        ) if self.registered_players else "Aucun joueur inscrit"
        return (
            f"Nom : {self.name}\n"
            f"Ville : {self.location}\n"
            f"Date de démarrage : {self.start_date}\n"
            f"Date de fin : {self.end_date}\n"
            f"Description : {self.description}\n"
            f"Nombre de rounds : {self.nb_rounds}\n"
            f"Round actuel : {self.current_round}\n"
            f"Statut : {'Terminé' if self.finished else 'En cours / À venir'}\n"
            f"Joueurs : {players_str}"
        )

    def get_scores(self):
        """Returns dict {uuid_value: total_score} for all registered players."""
        scores = {p.uuid_value: 0.0 for p in self.registered_players}
        for round in self.rounds:
            if not isinstance(round, Round):
                continue
            for match in round.match_list:
                if match.finished:
                    if match.player1.uuid_value in scores and match.player1_score is not None:
                        scores[match.player1.uuid_value] += match.player1_score
                    if match.player2.uuid_value in scores and match.player2_score is not None:
                        scores[match.player2.uuid_value] += match.player2_score
        return scores

    def get_played_pairs(self):
        """Returns set of frozensets of uuid pairs that already played."""
        pairs = set()
        for rnd in self.rounds:
            if not isinstance(rnd, Round):
                continue
            for match in rnd.match_list:
                pairs.add(frozenset([match.player1.uuid_value, match.player2.uuid_value]))
        return pairs

    @staticmethod
    def from_dict(data):
        registered_players = []
        if data.get("registered_players"):
            for p in data["registered_players"]:
                registered_players.append(
                    Player(p["first_name"], p["last_name"], p["birth_date"], p["player_id"], p["uuid_value"])
                )

        rounds = []
        if data.get("rounds"):
            for r in data["rounds"]:
                if isinstance(r, dict) and "match_list" in r:
                    rounds.append(Round.from_dict(r))

        return Tournament(
            data["name"],
            data["location"],
            data["start_date"],
            data["end_date"],
            data.get("description", ""),
            registered_players,
            data.get("current_round", 0),
            rounds,
            data.get("nb_rounds", 4),
            data.get("finished", False),
            data.get("uuid_value")
        )

    def to_dict(self):
        return {
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "current_round": self.current_round,
            "rounds": [r.to_dict() if isinstance(r, Round) else r for r in self.rounds],
            "registered_players": [p.to_dict() for p in self.registered_players],
            "description": self.description,
            "nb_rounds": self.nb_rounds,
            "finished": self.finished,
            "uuid_value": self.uuid_value
        }
