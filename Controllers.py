import Views
import Models
import Repositories
import re
from pathlib import Path


class MainController:

    BASE_DIR = Path(__file__).resolve().parent
    filename_repo_players = BASE_DIR / "data" / "players.json"
    filename_repo_tournament = BASE_DIR / "data" / "tournament.json"

    def __init__(self):
        self.player_view = Views.PlayerView()
        self.tournament_view = Views.TournamentView()

        self.player_repository = Repositories.PlayerRepository(self.filename_repo_players)
        self.tournament_repository = Repositories.TournamentRepository(self.filename_repo_tournament)

        self.player_controller = PlayerController(
            self.player_view,
            self.player_repository,
            self.tournament_repository
        )

        self.tournament_controller = TournamentController(
            self.tournament_view,
            self.player_repository,
            self.tournament_repository
        )

    def run(self):

        self.tournament_repository.check_is_exist()
        self.player_repository.check_is_exist()
   
        self.tournament_repository.load_all(bootload=True)
        self.player_repository.load_all(bootload=True)

        options = { "1" : "Gérer les joueurs",
                    "2" : "Gérer les tournois",
                    "3" : "Quitter"}
        
        main_view = Views.MainView()
        main_view.show_welcome()
        while True:
            while True:
                main_view.display_menu(options)
                user_input = main_view.get_input()
                try:
                    MainController.check_choice(user_input, list(options.keys()))
                    break
                except ValueError as e:
                    main_view.show_message(e)
                    continue
            choice = options[user_input]
            if self.handle_start_menu_choice(choice) == "quit":
                return

    def handle_start_menu_choice(self, choice):
        
        match choice:
            case "Gérer les joueurs":
                self.player_controller.run()
            case "Gérer les tournois":
                self.tournament_controller.run()
            case "Quitter":
                return "quit"

    @staticmethod     
    def check_input_data(input, data, ID_PATTERN = r"[A-Z]{2}\d{5}"):
        if not isinstance(input, str) or not input.strip():
            raise ValueError (f"Le champ {data} ne peut pas être vide")
        if "Jour" in data:
                if not re.fullmatch(r"[0-9]{2}", input):
                    raise ValueError (f"{data} invalide, format attendu '00'")
        elif "Mois" in data:
                if not re.fullmatch(r"[0-9]{2}", input):
                    raise ValueError (f"{data} invalide, format attendu '00'")
        elif "Année" in data:
                if not re.fullmatch(r"[0-9]{4}", input):
                    raise ValueError (f"{data} invalide, format attendu '0000'")
        elif "Identifiant" in data:
                if not re.fullmatch(ID_PATTERN, input.upper()):
                    raise ValueError("ID invalide (format attendu : AB12345)")
                
    @staticmethod
    def check_choice(input_user : str, choice_possibilities : list):
        if input_user not in choice_possibilities:
            raise ValueError(f"Vous devez choisir parmi les choix {','.join(choice_possibilities)}")
        
    @staticmethod
    def _validate_not_empty(value: str, key: str = "demandé"):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Le champ {key} ne peut pas être vide")
    
    @staticmethod
    def check_yes_no_choice(input_user : str):
        choice = ["y", "n"]

        if input_user not in choice:
            raise ValueError(f"Vous devez choisir parmi les choix {choice[0]} ou {choice[1]}")
    
    @staticmethod
    def format_date(day, month, year):
        formatted_date = (day + "/" + month + "/" + year)
        return formatted_date
    
class TournamentController():
    
    def __init__(self, tournament_view : Views.TournamentView, player_repo : Repositories.PlayerRepository, tournament_repo : Repositories.TournamentRepository):
        self.tournament_view = tournament_view
        self.player_repository = player_repo
        self.tournament_repository = tournament_repo

    def run(self):

        title = "MENU DE GESTION DES TOURNOIS"

        options = { "1" : "Créer un tournoi",
                    "2" : "Modifier un tournoi à venir",
                    "3" : "Gérer un tournoi en cours",
                    "4" : "Voir tous les tournois",
                    "5" : "Consulter les résultats d'un tournoi",
                    "6" : "Restaurer la base de données des tournois",
                    "7" : "Retour au menu principal"}

        while True:
                  
            self.tournament_view.show_title(title)
            self.tournament_view.display_menu(options)
            user_input = self.tournament_view.get_input()
            try:
                MainController.check_choice(user_input, list(options.keys()))
            except ValueError as e:
                self.tournament_view.show_message(e)
                continue
            choice = options[user_input]
            if self.handle_start_menu_tournament(choice) == "quit":
                return
        
    def handle_start_menu_tournament(self, choice):
        

            match choice:
                case "Créer un tournoi":
                    self.handle_tournament_creation_menu()
                    return
                
                case "Modifier un tournoi à venir":
                    self.handle_modify_unfinished_tournament_interface()
                    return
                
                case "Gérer un tournoi en cours":
                    pass

                case "Voir tous les tournois":
                    title = "LISTE DES TOURNOIS"
                    self.tournament_view.show_title(title)
                    self.tournament_view.show_tournament_list(self.tournament_repository.tournaments)
                    return
                
                case "Consulter les résultats d'un tournoi":
                    return

                case "Restaurer la base de données des tournois": 
                    self.handle_restoration_database_tournament_interface()
                    return
                
                case "Retour au menu principal":
                    return "quit"
    
    def handle_tournament_creation_menu(self):

        data_needed = [ "Nom du tournoi",
                        "Ville du tournoi",
                        "Jour de démarrage",
                        "Mois de démarrage",
                        "Année de démarrage",
                        "Jour de fin",
                        "Mois de fin",
                        "Année de fin",
                        "Description"]
        new_tournament_data = {}
        title = "INTERFACE DE CREATION DE TOURNOI"
        self.tournament_view.show_title(title)
        for element in data_needed:
            while True:
                self.tournament_view.display_interface_tournament_data(element)
                user_input = self.tournament_view.get_input()
                try:
                    MainController.check_input_data(user_input, element)
                    new_tournament_data[element] = user_input.upper()
                    break
                except ValueError as e:
                    self.tournament_view.show_message(e)
        formatted_start_date = MainController.format_date(new_tournament_data["Jour de démarrage"],
                                                           new_tournament_data["Mois de démarrage"],
                                                           new_tournament_data["Année de démarrage"])
        formatted_end_date = MainController.format_date(new_tournament_data["Jour de fin"],
                                                         new_tournament_data["Mois de fin"],
                                                         new_tournament_data["Année de fin"])

        del new_tournament_data["Jour de démarrage"]
        del new_tournament_data["Mois de démarrage"]
        del new_tournament_data["Année de démarrage"]

        del new_tournament_data["Jour de fin"]
        del new_tournament_data["Mois de fin"]
        del new_tournament_data["Année de fin"]

        new_tournament_data["Date de démarrage"] = formatted_start_date
        new_tournament_data["Date de fin"] = formatted_end_date
        
        new_tournament = self.create_new_tournament(new_tournament_data)
        self.tournament_repository.add_tournament(new_tournament)

        while True:
            self.tournament_view.show_message("Voulez vous ajouter des participants à ce tournoi ? y/n")
            user_input = self.tournament_view.get_input().lower()
            try:
                MainController.check_yes_no_choice(user_input)
            except ValueError as e:
                self.tournament_view.show_message(e)
                continue

            if user_input == "y":
               
                registrable_players = {}
                selected_players = []
                
                for i, player in enumerate (sorted(self.player_repository.players, key = lambda p : p.first_name), start = 1):
                    registrable_players[str(i)] = player
                    self.tournament_view.show_message(f"{i} : {player}")
                self.tournament_view.show_message("Indiquez les chiffres de chaque joueur, séparés d'une virgule")
                user_input = self.tournament_view.get_input()
                user_input = user_input.split(",")
                try:
                    for element in user_input:
                        if element not in list(registrable_players.keys()):
                            raise ValueError("Au moins une saisie ne correspond pas aux joueurs existants, veuillez recommencer")
                            
                except ValueError as e:
                    self.tournament_view.show_message(e)
                    continue
                    
                for element in user_input :
                    selected_players.append(registrable_players[element])
                    

                new_tournament_data["registered_players"] = selected_players
                new_tournament = self.modify_existing_tournament(new_tournament, new_tournament_data)
                self.tournament_repository.update_tournament(new_tournament)
                self.tournament_view.show_message(new_tournament)

                                
            elif user_input == "n":
                return
            else:
                self.tournament_view.show_message("Veuillez entrer un choix valide (y/n)")
            
            self.tournament_view.show_message(f"Le tournoi {new_tournament.name} a été créé avec succés")


            return

    def handle_modify_unfinished_tournament_interface(self):

        options = {"1" : "Nom",
            "2" : "Ville",
            "3" : "Date de démarrage",
            "4" : "Date de fin",
            "5" : "Joueurs participants",
            "6" : "Description",
            "7" : "Nombre de rounds",
            "8" : "Retour"}

        if not self.tournament_repository.tournaments:
            self.tournament_view.show_message("La liste des tournois est vide")
            return

        if not any(t.finished == False for t in self.tournament_repository.tournaments):
            self.tournament_view.show_message("Il n'y a aucun tournoi en cours ou à venir pour l'instant")
            return
            

        while True:
            no_match_message = "Aucune correspondance trouvée"
            researched_tournament = self.tournament_view.display_tournament_research()
            try:
                MainController._validate_not_empty(researched_tournament)
                break
            except ValueError as e:
                self.tournament_view.show_message(e)
        possible_matches = self.tournament_research(researched_tournament)

        if not possible_matches:
            self.tournament_view.show_message(no_match_message)
            return

        elif len(possible_matches) == 1:
            selected_tournament = possible_matches[0]

        else:
            while True:
                try:
                    match = self.tournament_view.display_tournament_research_matches(possible_matches)
                    if int(match) in range(1, len(possible_matches) + 1):
                        selected_tournament = possible_matches[int(match) - 1]
                        break
                    else:
                        self.tournament_view.show_message("Entrez le chiffre correspondant à votre choix")
                except ValueError:
                    self.tournament_view.show_message("Entrez un nombre valide")
        self.tournament_view.display_submenu_tournament_modification(options, selected_tournament)
        user_input = self.tournament_view.get_input()
        choice = options[user_input]
        while True:
            new_data = {}
            match choice:

                case "Nom":
                    try:
                        self.tournament_view.display_interface_tournament_data(choice)
                        user_input = self.tournament_view.get_input()
                        MainController.check_input_data(user_input, choice)
                        new_data["name"] = user_input.upper()
                        selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                        self.tournament_repository.update_tournament(selected_tournament)
                        self.tournament_view.show_message(f"Le nom du tournoi a été modifié en {selected_tournament.name}")
                        
                    except ValueError as e:
                        self.tournament_view.show_message(e)
                        continue

                case "Ville":
                    try:
                        self.tournament_view.display_interface_tournament_data(choice)
                        user_input = self.tournament_view.get_input()
                        MainController.check_input_data(user_input, choice)
                        new_data["location"] = user_input.upper()
                        selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                        self.tournament_repository.update_tournament(selected_tournament)
                        self.tournament_view.show_message(f"Le nom du tournoi a été modifié en {selected_tournament.location}")
                        
                    except ValueError as e:
                        self.tournament_view.show_message(e)
                        continue

                case "Date de démarrage":
                    new_start_date = []
                    for element in ("Jour de démarrage", "Mois de démarrage", "Année de démarrage"):
                        while True:
                            try:
                                self.tournament_view.display_interface_tournament_data(element)
                                user_input = self.tournament_view.get_input()
                                MainController.check_input_data(user_input, element)
                                new_start_date.append(user_input)
                                break
  
                            except ValueError as e:
                                self.tournament_view.show_message(e)
                                continue

                    new_start_date = MainController.format_date(new_start_date[0], new_start_date[1], new_start_date[2])
                    new_data["start_date"] = new_start_date
                    selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                    self.tournament_repository.update_tournament(selected_tournament)
                    self.tournament_view.show_message(f"La date de démarrage du tournoi a été modifiée en {selected_tournament.start_date}")
                    
                case "Date de fin":
                    new_end_date = []
                    for element in ("Jour de fin", "Mois de fin", "Année de fin"):
                        while True:
                            try:
                                (self.tournament_view.display_interface_tournament_data(element))
                                user_input = self.tournament_view.get_input()
                                MainController.check_input_data(user_input, element)
                                new_end_date.append(user_input)
                                break
  
                            except ValueError as e:
                                self.tournament_view.show_message(e)
                                continue

                    new_end_date = MainController.format_date(new_end_date[0], new_end_date[1], new_end_date[2])
                    new_data["end_date"] = new_end_date
                    selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                    self.tournament_repository.update_tournament(selected_tournament)
                    self.tournament_view.show_message(f"La date de fin du tournoi a été modifiée en {selected_tournament.end_date}")

                case "Joueurs participants":
                
                            registrable_players = {}
                            players_to_register = []
                            new_data = {}
                            
                            for i, player in enumerate (sorted(self.player_repository.players, key = lambda p : p.first_name), start = 1):
                                registrable_players[str(i)] = player
                                self.tournament_view.show_message(f"{i} : {player}")
                            self.tournament_view.show_message("Indiquez les chiffres de chaque joueur, séparés d'une virgule")
                            user_input = self.tournament_view.get_input()
                            formated_user_input = user_input.replace(" ", "").split(",")
                            try:
                                for element in formated_user_input:
                                    if element not in list(registrable_players.keys()):
                                        raise ValueError("Au moins une saisie ne correspond pas aux joueurs existants, veuillez recommencer")
                                        
                            except ValueError as e:
                                self.tournament_view.show_message(e)
                                continue
                                
                            for element in formated_user_input :
                                players_to_register.append(registrable_players[element])
                                
                            new_data["registered_players"] = players_to_register
                            selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                            self.tournament_repository.update_tournament(selected_tournament)
                            self.tournament_view.show_message("Les joueurs ont bien été ajoutés pour ce tournoi")
                            self.tournament_view.show_message(selected_tournament)
                                
                                
                case "Description":
                    try:
                        self.tournament_view.display_interface_tournament_data(choice)
                        user_input = self.tournament_view.get_input()
                        MainController.check_input_data(user_input, choice)
                        new_data["description"] = user_input.upper()
                        selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                        self.tournament_repository.update_tournament(selected_tournament)
                        self.tournament_view.show_message(f"La description du tournoi a bien été modifiée")
                        
                    except ValueError as e:
                        self.tournament_view.show_message(e)
                        continue
                case "Nombre de rounds":
                    try:
                        self.tournament_view.display_interface_tournament_data(choice)
                        user_input = self.tournament_view.get_input()
                        MainController.check_input_data(user_input, choice)
                        new_data["nb_rounds"] = user_input.upper()
                        selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                        self.tournament_repository.update_tournament(selected_tournament)
                        self.tournament_view.show_message(f"Le nombre de rounds du tournoi a bien été modifiée")
                        
                    except ValueError as e:
                        self.tournament_view.show_message(e)
                        continue

                case "Retour":
                    return
            

            while True:
                self.tournament_view.show_message("Voulez vous modifier une autre information pour ce tournoi ? y/n")
                user_input = self.tournament_view.get_input().lower()

                if user_input == "y":
                    self.tournament_view.display_submenu_tournament_modification(options, selected_tournament)
                    user_input = self.tournament_view.get_input()
                    choice = options[user_input]
                    break
                elif user_input == "n":
                    return
                else:
                    self.tournament_view.show_message("Veuillez entrer un choix valide (y/n)")

    def handle_restoration_database_tournament_interface(self):
        options = ["y", "n"]
        self.tournament_view.show_message("Etes vous sûr de vouloir restaurer la base de données des tournois depuis le fichier de restauration? y/n")
        while True:
        
            choice = self.tournament_view.get_input()

            try :
                MainController.check_choice(choice, options)
            except ValueError as e:
                self.tournament_view.show_message(e)
            match choice:
                case "y":
                    self.tournament_repository.load_all()
                    self.tournament_view.show_message("La liste des tournois a bien été restaurée")
                    return
                case "n":
                    return

    def tournament_research(self, input_user: str):
        correspondances = []
        fields = ["name", "location", "start_date", "end_date"]

        if not self.tournament_repository.tournaments:
            raise ValueError("La liste des tournois est vide, veuillez d'abord créer un tournoi")

        for tournament in self.tournament_repository.tournaments:
            if tournament is None:
                continue
            if tournament.finished == False:
                for element in fields:
                    if input_user.upper() in str(getattr(tournament, element)).upper():
                        correspondances.append(tournament)
                        break
            else :
                continue
            
        return correspondances

    def list_tournament_registered_players(self, tournament):
        players = self.player_repository.load_all()
        players_by_uuid = {player.uuid: player for player in players}
        registered_players = []

        for player_uuid_value in tournament.registered_players:
            player = players_by_uuid.get(player_uuid_value)
            if player:
                registered_players.append(player)
        return registered_players

    def create_new_tournament(self, new_tournament_data : list):
        
        new_tournament = Models.Tournament(
                name = new_tournament_data["Nom du tournoi"],
                location = new_tournament_data["Ville du tournoi"],
                start_date = new_tournament_data["Date de démarrage"],
                end_date = new_tournament_data["Date de fin"],
                description = new_tournament_data["Description"],
            )

        return new_tournament

    def modify_existing_tournament(self, tournament : Models.Tournament, new_tournament_data : dict):
        
        for key, value in new_tournament_data.items():
            if value:
                setattr(tournament, key, value)
        
        return tournament

class PlayerController:

    def __init__(self, player_view : Views.PlayerView, player_repo : Repositories.PlayerRepository, tournament_repo : Repositories.TournamentRepository):
        self.player_view = player_view
        self.player_repository = player_repo
        self.tournament_repository = tournament_repo

    def run(self):
        
        options = {"1" : "Ajouter un joueur",
                   "2" : "Modifier un joueur", 
                   "3" : "Voir la liste des joueurs",
                   "4" : "Restaurer la base de données des joueurs",
                   "5" : "Retour au menu principal"}
        while True:
            self.player_view.display_menu(options)
            input_user = self.player_view.get_input()
            try:
                MainController.check_choice(input_user, list(options.keys()))
            except ValueError as e:
                self.player_view.show_message(e)
                continue
            choice = options[input_user]
            if self.handle_start_menu_player(choice) == "quit":
                return

    def handle_start_menu_player(self, choice):

            match choice:
                case "Ajouter un joueur":
                    self.handle_add_player_menu()
                    return
                case "Modifier un joueur":
                    self.handle_modify_player_menu()
                    return
                case "Voir la liste des joueurs":
                    self.player_repository.load_all()
                    self.player_view.show_player_list(self.player_repository.players)
                    return
                case "Restaurer la base de données des joueurs":
                    self.handle_restoration_database_player_interface()
                    return
                case "Retour au menu principal": 
                    return "quit"

    def handle_add_player_menu(self):
        new_player_data = {}

        player_data_needed = [  "Prénom",
                                "Nom",
                                "Jour de naissance",
                                "Mois de naissance",
                                "Année de naissance",
                                "Identifiant national"]
        
        title = "AJOUTER UN JOUEUR"
        self.player_view.show_title(title)
        for element in player_data_needed:
            while True:
                self.player_view.display_interface_player_data(element)
                input_user = self.player_view.get_input()
                try:
                    MainController.check_input_data(input_user, element)
                    new_player_data[element] = input_user.upper()
                    break
                except ValueError as e:
                    self.player_view.show_message(e)

        formatted_birthdate = MainController.format_date(new_player_data["Jour de naissance"],
                                                           new_player_data["Mois de naissance"],
                                                           new_player_data["Année de naissance"])
        del new_player_data["Jour de naissance"]
        del new_player_data["Mois de naissance"]
        del new_player_data["Année de naissance"]

        new_player_data["Date de naissance"] = formatted_birthdate

        similar_players = []

        for player in self.player_repository.players:
            if new_player_data["Identifiant national"] == player.player_id:
                similar_players.append(player)
        if similar_players:
            self.player_view.show_message("Un ou plusieurs joueurs existants ont le même identifiant.")
            for i in range (0, len(similar_players)):
                self.player_view.show_message(similar_players[i])

            while True:
                self.player_view.show_message("Voulez vous tout de même créer le joueur? y/n")
                choice = self.player_view.get_input()
            
                if choice == "y":
                    break
                elif choice == "n":
                    return
                else:
                    self.player_view.show_message("Vous devez choisir entre les choix 'y' ou 'n' ")
                
        new_player = self.create_player(new_player_data)
        self.player_repository.add_player(new_player)
        self.player_view.show_message(f"Le joueur {new_player_data['Prénom']} {new_player_data['Nom']} a été créé avec succès")

    def handle_modify_player_menu(self):
        options = {"1" : "Prénom",
                   "2" : "Nom",
                   "3" : "Date de naissance",
                   "4" : "Identifiant national",
                   "5" : "Quitter"}

        
        no_match_message = "Aucune correspondance trouvée"
        impacted_tournament = []
        while True:
            researched_player = self.player_view.display_player_modification_research()                     
            try:
                MainController._validate_not_empty(researched_player)
                break
            except ValueError as e:
                self.player_view.show_message(e)
        try :
            possible_match = self.player_research(researched_player)
        except ValueError as e:
            self.player_view.show_message(e)
            return

        if not possible_match:
            self.player_view.show_message(no_match_message)
            return

        elif len(possible_match) == 1:
            selected_player = possible_match[0]

        else:
            while True:
                try:
                    match = self.player_view.display_player_research_match(possible_match)
                    if int(match) in range(1, len(possible_match) + 1):
                        selected_player = possible_match[int(match) - 1]
                        break
                    else:
                        self.player_view.show_message("Entrez le chiffre correspondant à votre choix")
                except ValueError:
                    self.player_view.show_message("Entrez un nombre valide")

        if self.tournament_repository.tournaments:
            player_to_modify = [selected_player]
            impacted_tournament = self.check_impact_modification(player_to_modify)
            if impacted_tournament:
                for tournament in impacted_tournament:
                        self.player_view.show_message(tournament.name)
            while True:
                    self.player_view.show_message(f"Changer les données du joueur {selected_player} va impacter les tournois ci dessus, voulez vous continuer? y/n")
                    input_user = self.player_view.get_input()
                
                    if input_user == "y":
                        break
                    elif input_user == "n":
                        return
                    else:
                        self.player_view.show_message("Veuillez entrer un choix valide (y/n)")
                

        while True:
            self.player_view.display_submenu_player_modification(options, selected_player)
            input_user = self.player_view.get_input()
            try :
                MainController.check_choice(input_user, list(options.keys()))
                break
            except ValueError as e:
                self.player_view.show_message(e)
                continue
        choice = options[input_user]
        while True:
            new_data = {}
            match choice:

                case "Prénom":
                    try:
                        self.player_view.display_interface_player_data(choice)
                        user_input = self.player_view.get_input()
                        MainController.check_input_data(user_input, choice)
                        new_data["first_name"] = user_input.upper()
                        selected_player = self.modify_existing_player(selected_player, new_data)
                        self.player_repository.update_player(selected_player)
                        self.player_view.show_message(f"Le prénom a été modifié en {selected_player.first_name}")
                        
                    except ValueError as e:
                        self.player_view.show_message(e)
                        continue

                case "Nom":
                    try:
                        self.player_view.display_interface_player_data(choice)
                        user_input = self.player_view.get_input()
                        MainController.check_input_data(user_input, choice)
                        new_data["last_name"] = user_input.upper()
                        selected_player = self.modify_existing_player(selected_player, new_data)
                        self.player_repository.update_player(selected_player)
                        self.player_view.show_message(f"Le nom a été modifié en {selected_player.last_name}")
                        
                    except ValueError as e:
                        self.player_view.show_message(e)
                        continue

                case "Date de naissance":
                    new_birth_date = []
                    for element in ("Jour de naissance", "Mois de naissance", "Année de naissance"):
                        while True:
                            try:
                                self.player_view.display_interface_player_data(element)
                                user_input = self.player_view.get_input()
                                MainController.check_input_data(user_input, element)
                                new_birth_date.append(user_input)
                                break
  
                            except ValueError as e:
                                self.player_view.show_message(e)
                                continue

                    new_birth_date = MainController.format_date(new_birth_date[0], new_birth_date[1], new_birth_date[2])
                    new_data["birth_date"] = new_birth_date
                    selected_player = self.modify_existing_player(selected_player, new_data)
                    self.player_repository.update_player(selected_player)
                    self.player_view.show_message(f"La date de naissance a été modifiée en {selected_player.birth_date}")
                    
                        

                case "Identifiant national":
                    try:
                        self.player_view.display_interface_player_data(choice)
                        user_input = self.player_view.get_input()
                        MainController.check_input_data(user_input, choice)
                        new_data["player_id"] = user_input.upper()
                        selected_player = self.modify_existing_player(selected_player, new_data)
                        self.player_repository.update_player(selected_player)
                        self.player_view.show_message(f"L'identifiant a été modifié en {selected_player.player_id}")
                        
                    except ValueError as e:
                        self.player_view.show_message(e)
                        continue
                
                case "Quitter":
                    return
            
            for tournament in impacted_tournament:
                players = tournament.registered_players

                if not players:
                    continue

                for i, player in enumerate(players):
                    if player.uuid_value == selected_player.uuid_value:
                        players[i] = selected_player

                self.tournament_repository.update_tournament(tournament)

            while True:
                self.player_view.show_message("Voulez vous modifier une autre information pour ce joueur ? y/n")
                input_user = self.player_view.get_input().lower()

                if input_user == "y":
                    self.player_view.display_submenu_player_modification(options, selected_player)
                    input_user = self.player_view.get_input()
                    choice = options[input_user]
                    break
                elif input_user == "n":
                    return
                else:
                    self.player_view.show_message("Veuillez entrer un choix valide (y/n)")
    
    def handle_restoration_database_player_interface(self):
        possible_choices = ["y", "n"]
        self.player_view.show_message("Etes vous sûr de vouloir restaurer la base de données des joueurs depuis le fichier de restauration? y/n")
        while True:
            choice = self.player_view.get_input()
            try :
                MainController.check_choice(choice, possible_choices)
            except ValueError as e:
                self.player_view.show_message(e)
            match choice:
                case "y":
                    old_database = self.player_repository.players
                    self.player_repository.load_all()
                    new_database = self.player_repository.players
                    if new_database == None:
                        return
                    else :
                        while True:
                            if self.check_impact_modification(new_database):
                                self.player_view.show_message("Les participants des tournois suivants vont être impactés par la restauration, voulez vous continuer?")
                                choice = self.player_view.get_input()
                                try :
                                    MainController.check_choice(choice, possible_choices)
                                except ValueError as e:
                                    self.player_view.show_message(e)
                                match choice:
                                    case "y" :
                                        self.player_view.show_message("La liste des joueurs a bien été restaurée")
                                        return
                                    case "n" :
                                        self.player_repository.players = old_database
                                        self.player_view.show_message("Restauration annulée")
                                        return
                            else :
                                self.player_repository.players = new_database
                                self.player_view.show_message("La liste des joueurs a bien été restaurée")
                                return
                case "n":
                    return
            
    def player_research(self, input_user: str):
        correspondances = []
        fields = ["first_name", "last_name", "birth_date", "player_id"]

        if not self.player_repository.players:
            raise ValueError("La liste des joueurs est vide, veuillez d'abord créer un joueur")

        for player in self.player_repository.players:
            for element in fields:
                if input_user.upper() in str(getattr(player, element)).upper():
                    correspondances.append(player)
                    break
        return correspondances

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
    
    def check_impact_modification(self, player_to_modify : list):
        impacted_tournament = []

        for tournament in self.tournament_repository.tournaments:
            if not tournament.registered_players:
                continue
            if any(player.uuid_value == registered_players.uuid_value for player in player_to_modify for registered_players in tournament.registered_players):
                 impacted_tournament.append(tournament)
        return impacted_tournament
        
    def modify_existing_player(self, player : Models.Player, new_player_data : dict):
        
        for key, value in new_player_data.items():
            if value:
                setattr(player, key, value)
        return player
