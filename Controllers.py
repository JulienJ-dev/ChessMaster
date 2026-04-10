import Views
import Models
import Repositories
import re
from pathlib import Path
import json


class MainController:

    BASE_DIR = Path(__file__).resolve().parent
    filename_repo_players = BASE_DIR / "data" / "players.json"
    filename_repo_tournament = BASE_DIR / "data" / "tournament.json"

    def __init__(self):
        self.player_controller = PlayerController()
        self.tournament_controller = TournamentController()
        self.player_view = Views.PlayerView()
        self.player_repository = Repositories.PlayerRepository(self.filename_repo_players)
        self.tournament_repository = Repositories.TournamentRepository(self.filename_repo_tournament)

    def run(self):
        main_view = Views.MainView()
        Views.MainView.show_welcome(main_view)

        while True:
            try:
                possible_choices = Views.MainView.display_menu(main_view)
                choice = Views.MainView.get_input(main_view)
                self.handle_menu_choice(possible_choices, choice)
            except ValueError as e:
                print(e)

    def handle_menu_choice(self, possible_choices, choice):
        if choice not in possible_choices:
            raise ValueError(f"\nVous devez choisir parmi les valeurs {','.join(possible_choices)}\n".upper())

        match choice:
            case "1":
                self.player_controller.run(self.player_view, self.player_repository)
            case "2":
                pass
            case "3":
                exit()
    
    


class TournamentController:
    pass


class PlayerController:

    ID_PATTERN = r"[A-Z]{2}\d{5}"

    def __init__(self):
        self.player_list = []

    def run(self, view: Views.PlayerView, player_repo : Repositories.PlayerRepository):
        while True:
            possible_choices = view.display_menu()
            choice = view.get_input()
            action = self.handle_start_menu_player(possible_choices, choice, view, player_repo)
            if action == "quit":
                return

    def handle_start_menu_player(self, possible_choices, choice, view: Views.PlayerView, player_repo):
        if self.check_choice(choice, possible_choices):
            match choice:
                case "1":
                    self.handle_add_player_menu(view, player_repo)
                case "2":
                    self.handle_modify_player_menu(view, player_repo)
                case "3":
                    view.display_player_list(self.player_list)
                case "4":
                    self.handle_restoration_database_interface(view, player_repo)
                case "5": 
                    return "quit"

    def handle_add_player_menu(self, view: Views.PlayerView, player_repo : Repositories.PlayerRepository):
        new_player_data = {}
        add_player_title = "AJOUTER UN JOUEUR"
        line_player_title = "-" * len(add_player_title)
        title = add_player_title + "\n" + line_player_title + "\n"
        view.show_message(title)

        player_data_needed = [
            "Prénom",
            "Nom",
            "Jour de naissance",
            "Mois de naissance",
            "Année de naissance",
            "Identifiant national"
        ]

        for element in player_data_needed:
            while True:
                input_user = view.display_interface_player_data(element).upper()
                try:
                    self._validate_not_empty(input_user, element)
                    if element in ("Jour de naissance", "Mois de naissance", "Année de naissance"):
                        self.check_input_data_player(input_user, element)
                    if element == "Identifiant national":
                        self.check_input_data_player(input_user, element)
                    new_player_data[element] = input_user
                    break
                except ValueError as e:
                    print(e)

        formatted_birthdate = self.format_birthdate_player(new_player_data["Jour de naissance"], new_player_data["Mois de naissance"], new_player_data["Année de naissance"])
        del new_player_data["Jour de naissance"],new_player_data["Mois de naissance"], new_player_data["Année de naissance"]
        new_player_data["Date de naissance"] = formatted_birthdate
        
        player = self.create_player(new_player_data)
        self.player_list.append(player)
        print(f"Le joueur {player} a été créé avec succès")

    def handle_modify_player_menu(self, view: Views.PlayerView, player_repo : Repositories.PlayerRepository):
        options = ["Prénom", "Nom", "Date de naissance", "Identifiant national"]
        no_match_message = "Aucune correspondance trouvée"
        researched_player = view.display_player_modification_research()
        self._validate_not_empty(researched_player)
        possible_match = self.player_research(researched_player)

        if not possible_match:
            view.show_message(no_match_message)
            return

        elif len(possible_match) == 1:
            selected_player = possible_match[0]

        else:
            while True:
                try:
                    match = view.display_research_match(possible_match)
                    if int(match) in range(1, len(possible_match) + 1):
                        selected_player = possible_match[int(match) - 1]
                        break
                    else:
                        view.show_message("Entrez le chiffre correspondant à votre choix")
                except ValueError:
                    view.show_message("Entrez un nombre valide")
        input_user = view.display_submenu_player_modification(options, selected_player)
        choice = options[int(input_user) - 1]
        while True:
            match choice:

                case "Prénom":
                    try:
                        new_first_name = view.display_interface_player_data(choice)
                        self.check_input_data_player(new_first_name, choice)
                        selected_player.first_name = new_first_name
                        view.show_message(f"Le prénom a été modifié en {selected_player.first_name}")
                        
                    except ValueError as e:
                        print (e)

                case "Nom":
                    try:
                        new_last_name = view.display_interface_player_data(choice)
                        self.check_input_data_player(new_last_name, choice)
                        selected_player.last_name = new_last_name
                        view.show_message(f"Le nom a été modifié en {selected_player.last_name}")
                        
                    except ValueError as e:
                        print (e)

                case "Date de naissance":
                    new_birth_date = []
                    for element in ("Jour de naissance", "Mois de naissance", "Année de naissance"):
                        while True:
                            try:
                                new_data = (view.display_interface_player_data(element))
                                self.check_input_data_player(new_data, element)
                                new_birth_date.append(new_data)
                                print(new_birth_date)
                                break
  
                            except ValueError as e:
                                print (e)

                    new_birth_date = self.format_birthdate_player(new_birth_date[0], new_birth_date[1], new_birth_date[2])
                    selected_player.birth_date = new_birth_date
                    view.show_message(f"La date de naissance a été modifiée en {selected_player.birth_date}")
                    
                        

                case "Identifiant national":
                    try:
                        new_id = view.display_interface_player_data(choice)
                        self.check_input_data_player(new_id, choice)
                        selected_player.player_id = new_id
                        view.show_message(f"L'identifiant a été modifié en {selected_player.player_id}")
                        
                    except ValueError as e:
                        print (e)

            while True:
                view.show_message("Voulez vous modifier une autre information pour ce joueur ? y/n")
                input_user = view.get_input().lower()

                if input_user == "y":
                    input_user = view.display_submenu_player_modification(options, selected_player)
                    choice = options[int(input_user) - 1]
                    break
                elif input_user == "n":
                    return
                else:
                    view.show_message("Veuillez entrer un choix valide (y/n)")
    
    def handle_restoration_database_interface(self, view: Views.PlayerView, player_repo : Repositories.PlayerRepository):
        while True:
            possible_choices, choice = view.display_confirmation_restoration_database()
            try :
                self.check_choice(choice, possible_choices)
            except ValueError as e:
                print (e)
            match choice:
                case "y":
                    if player_repo.load_all() == None:
                        return
                    else : 
                        self.player_list = player_repo.load_all()
                        view.show_message("La liste des joueurs a bien été restaurée")
                        return
                case "n":
                    return


                    


    def check_choice(self, input_user, choice_possibilities):
        if input_user in choice_possibilities:
            return True
        else:
            raise ValueError(f"Vous devez choisir parmi les choix {','.join(choice_possibilities)}")
    
    def check_input_data_player(self, input, data):
        if not isinstance(input, str) or not input.strip():
            raise ValueError (f"Le champ {data} ne peut pas être vide")
        match data:
            case "Jour de naissance":
                if not re.fullmatch(r"[0-9]{2}", input):
                    raise ValueError (f"{data} invalide, format attendu '00'")
            case "Mois de naissance":
                if not re.fullmatch(r"[0-9]{2}", input):
                    raise ValueError (f"{data} invalide, format attendu '00'")
            case "Année de naissance":
                if not re.fullmatch(r"[0-9]{4}", input):
                    raise ValueError (f"{data} invalide, format attendu '0000'")
            case "Identifiant national":
                if not re.fullmatch(self.ID_PATTERN, input.upper()):
                    raise ValueError("ID invalide (format attendu : AB12345)")

    def player_research(self, input_user: str):
        correspondances = []
        fields = ["first_name", "last_name", "birth_date", "player_id"]

        if not self.player_list:
            raise ValueError("La liste des joueurs est vide, veuillez d'abord créer un joueur")

        for player in self.player_list:
            for element in fields:
                if input_user.upper() in str(getattr(player, element)).upper():
                    correspondances.append(player)
                    break
        return correspondances

    def format_birthdate_player(self, birth_day, birth_month, birth_year):
        formatted_birthdate = (birth_day + "/" + birth_month + "/" + birth_year)
        return formatted_birthdate

    def create_player(self, new_player_data):
        try:
            new_player = Models.Player(
                new_player_data["Prénom"],
                new_player_data["Nom"],
                new_player_data["Date de naissance"],
                new_player_data["Identifiant national"]
            )
            return new_player
        except ValueError:
            print("Erreur lors de la création du joueur, veuillez saisir à nouveau les données")

    def _validate_not_empty(self, value: str, key: str = "demandé"):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"ECHEC : Le champ {key} ne peut pas être vide")