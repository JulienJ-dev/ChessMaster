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
        self.tournament_view = Views.TournamentView()
        self.player_repository = Repositories.PlayerRepository(self.filename_repo_players)
        self.tournament_repository = Repositories.TournamentRepository(self.filename_repo_tournament)

    def run(self):
   

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
                self.player_controller.run(self.player_view, self.player_repository)
            case "Gérer les tournois":
                self.tournament_controller.run(self.tournament_view, self.player_repository, self.tournament_repository)
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
    


class TournamentController():
    
    def __init__(self):
        self.tournament_list = []
        self.player_controller = PlayerController()

    def run(self, view: Views.TournamentView, player_repo : Repositories.PlayerRepository, tournament_repo : Repositories.TournamentRepository):
        try:
            self.tournament_list = tournament_repo.load_all()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.tournament_list = []

        options = { "1" : "Créer un tournoi",
                    "2" : "Modifier un tournoi à venir",
                    "3" : "Gérer un tournoi en cours",
                    "4" : "Voir tous les tournois",
                    "5" : "Consulter les résultats d'un tournoi",
                    "6" : "Restaurer la base de données des tournois",
                    "7" : "Retour au menu principal"}
        while True:
            view.display_menu(options)
            user_input = view.get_input()
            try:
                MainController.check_choice(user_input, list(options.keys()))
            except ValueError as e:
                view.show_message(e)
                continue
            choice = options[user_input]
            if self.handle_start_menu_tournament(choice, view, player_repo, tournament_repo) == "quit":
                return
        
    def handle_start_menu_tournament(self, choice, view: Views.TournamentView, player_repo : Repositories.PlayerRepository, tournament_repo : Repositories.TournamentRepository):
        

            match choice:
                case "Créer un tournoi":
                    self.handle_tournament_creation_menu(view, player_repo, tournament_repo)
                    return
                
                case "Modifier un tournoi à venir":
                    self.handle_modify_unfinished_tournament_interface(view, player_repo, tournament_repo)
                    return
                
                case "Gérer un tournoi en cours":
                    pass

                case "Voir tous les tournois":
                    title = "LISTE DES TOURNOIS"
                    view.show_title(title)
                    view.show_tournament_list(self.tournament_list)
                    return
                
                case "Consulter les résultats d'un tournoi":
                    return

                case "Restaurer la base de données des tournois": 
                    self.handle_restoration_database_tournament_interface(view, tournament_repo)
                    return
                
                case "Retour au menu principal":
                    return "quit"
    
    def create_tournament(self, new_tournament_data):
        try:
            new_tournament = Models.Tournament(
                name = new_tournament_data["Nom du tournoi"],
                location = new_tournament_data["Ville du tournoi"],
                start_date = new_tournament_data["Date de démarrage"],
                end_date = new_tournament_data["Date de fin"],
                description = new_tournament_data["Description"],
            )
            return new_tournament
        except ValueError:
            print("Erreur lors de la création du joueur, veuillez saisir à nouveau les données")
    
    def handle_tournament_creation_menu(self, view : Views.TournamentView, player_repo : Repositories.PlayerRepository, repo_tournament : Repositories.TournamentRepository):

        player_list = player_repo.load_all()

        data_needed = [ "Nom du tournoi",
                        "Ville du tournoi",
                        "Jour de démarrage",
                        "Mois de démarrage",
                        "Année de démarrage",
                        "Jour de fin",
                        "Mois de fin",
                        "Année de fin",
                        "Description"]
        options = ["y", "n"]
        data_new_tournament = {}
        title = "INTERFACE DE CREATION DE TOURNOI"
        view.show_title(title)
        for element in data_needed:
            while True:
                user_input = view.display_interface_tournament_data(element)
                try:
                    MainController.check_input_data(user_input, element)
                    data_new_tournament[element] = user_input.upper()
                    break
                except ValueError as e:
                    view.show_message(e)
        formatted_start_date = self.format_date_tournament(data_new_tournament["Jour de démarrage"],
                                                           data_new_tournament["Mois de démarrage"],
                                                           data_new_tournament["Année de démarrage"])
        formatted_end_date = self.format_date_tournament(data_new_tournament["Jour de fin"],
                                                         data_new_tournament["Mois de fin"],
                                                         data_new_tournament["Année de fin"])

        del data_new_tournament["Jour de démarrage"]
        del data_new_tournament["Mois de démarrage"]
        del data_new_tournament["Année de démarrage"]

        del data_new_tournament["Jour de fin"]
        del data_new_tournament["Mois de fin"]
        del data_new_tournament["Année de fin"]

        data_new_tournament["Date de démarrage"] = formatted_start_date
        data_new_tournament["Date de fin"] = formatted_end_date
        new_tournament = self.create_tournament(data_new_tournament)
        self.tournament_list.append(new_tournament)
        repo_tournament.save_tournaments(self.tournament_list)

        view.show_message(f"Tournoi {data_new_tournament["Nom du tournoi"]} crée avec succés")

        while True:
            view.show_message("Voulez vous ajouter des participants à ce tournoi ? y/n")
            input_user = view.get_input().lower()

            if input_user == "y":
                add_player_method_options = {   "1" : "Sélectionner les participants à partir de la liste des joueurs",
                                                "2" : "Rechercher manuellement"}
                while True:
                    for key, value in add_player_method_options.items():
                        view.show_message(f"{key} . {value}")
                    
                    user_input = view.get_input()
                    try:
                        MainController.check_choice(user_input, list(add_player_method_options.keys()))
                        break
                    except ValueError as e:
                        view.show_message(e)
                        continue
                
                choice = add_player_method_options[user_input]

                match choice:

                    case "Sélectionner les participants à partir de la liste des joueurs":
                        options = {}
                        selected_players = []
                        
                        for i, player in enumerate (sorted(player_list, key = lambda p : p.first_name), start = 1):
                            options[str(i)] = player
                            view.show_message(f"{i} : {player}")
                        view.show_message("Indiquez les chiffres de chaque joueur, séparés d'une virgule")
                        user_input = view.get_input()
                        user_input = user_input.split(",")
                        try:
                            for element in user_input:
                                if element not in list(options.keys()):
                                    raise ValueError("Au moins une saisie ne correspond pas aux joueurs existants, veuillez recommencer")
                                    
                        except ValueError as e:
                            view.show_message(e)
                            continue
                            
                        for element in user_input :
                            selected_players.append(options[element])
                            

                        self.tournament_list[-1].registered_players = selected_players
                        repo_tournament.save_tournaments(self.tournament_list)
                        view.show_message("Les joueurs ont bien été ajoutés pour ce tournoi")
                        view.show_message(self.tournament_list[-1])
                                    

                    case "Rechercher manuellement":
                        pass
            elif input_user == "n":
                return
            else:
                view.show_message("Veuillez entrer un choix valide (y/n)")


        return

    def handle_modify_unfinished_tournament_interface(self, view : Views.TournamentView, repo_players : Repositories.PlayerRepository, repo_tournament : Repositories.TournamentRepository):
        
        player_list = repo_players.load_all()

        if not self.tournament_list:
            view.show_message("La liste des tournois est vide")
            return


        for tournament in self.tournament_list:
            if tournament.finished == False:
                break
            else:
                raise ValueError("Il n'y a pas aucun tournoi en cours ou à venir pour l'instant")
            
        options = {"1" : "Nom",
                   "2" : "Ville",
                   "3" : "Date de démarrage",
                   "4" : "Date de fin",
                   "5" : "Joueurs participants",
                   "6" : "Description",
                   "7" : "Nombre de rounds"}
        while True:
            no_match_message = "Aucune correspondance trouvée"
            researched_tournament = view.display_tournament_research()
            try:
                self._validate_not_empty(researched_tournament)
                break
            except ValueError as e:
                view.show_message(e)
        possible_matches = self.tournament_research(researched_tournament)

        if not possible_matches:
            view.show_message(no_match_message)
            return

        elif len(possible_matches) == 1:
            selected_tournament = possible_matches[0]

        else:
            while True:
                try:
                    match = view.display_tournament_research_matches(possible_matches)
                    if int(match) in range(1, len(possible_matches) + 1):
                        selected_tournament = possible_matches[int(match) - 1]
                        break
                    else:
                        view.show_message("Entrez le chiffre correspondant à votre choix")
                except ValueError:
                    view.show_message("Entrez un nombre valide")
        input_user = view.display_submenu_tournament_modification(options, selected_tournament)
        choice = options[input_user]
        while True:
            match choice:

                case "Nom":
                    try:
                        new_tournament_name = view.display_interface_tournament_data(choice)
                        MainController.check_input_data(new_tournament_name, choice)
                        selected_tournament.name = new_tournament_name.upper()
                        view.show_message(f"Le nom du tournoi a été modifié en {selected_tournament.name}")
                        
                    except ValueError as e:
                        view.show_message(e)
                        continue

                case "Ville":
                    try:
                        new_location = view.display_interface_tournament_data(choice)
                        MainController.check_input_data(new_location, choice)
                        selected_tournament.location = new_location.upper()
                        view.show_message(f"La ville du tournoi a été modifié en {selected_tournament.location}")
                        
                    except ValueError as e:
                        view.show_message(e)
                        continue

                case "Date de démarrage":
                    new_start_date = []
                    for element in ("Jour de démarrage", "Mois de démarrage", "Année de démarrage"):
                        while True:
                            try:
                                new_data = (view.display_interface_tournament_data(element))
                                MainController.check_input_data(new_data, element)
                                new_start_date.append(new_data)
                                break
  
                            except ValueError as e:
                                view.show_message(e)
                                continue

                    new_start_date = self.format_date_tournament(new_start_date[0], new_start_date[1], new_start_date[2])
                    selected_tournament.start_date = new_start_date
                    view.show_message(f"La date de démarrage du tournoi a été modifiée en {selected_tournament.start_date}")
                    
                case "Date de fin":
                    new_end_date = []
                    for element in ("Jour de fin", "Mois de fin", "Année de fin"):
                        while True:
                            try:
                                new_data = (view.display_interface_tournament_data(element))
                                MainController.check_input_data(new_data, element)
                                new_end_date.append(new_data)
                                break
  
                            except ValueError as e:
                                view.show_message(e)
                                continue

                    new_end_date = self.format_date_tournament(new_end_date[0], new_end_date[1], new_end_date[2])
                    selected_tournament.end_date = new_end_date
                    view.show_message(f"La date de fin du tournoi a été modifiée en {selected_tournament.end_date}")

                case "Joueurs participants":
                
                    add_player_method_options = {   "1" : "Sélectionner les participants à partir de la liste des joueurs",
                                                    "2" : "Rechercher manuellement"}
                    while True:
                        for key, value in add_player_method_options.items():
                            view.show_message(f"{key} . {value}")
                        
                        user_input = view.get_input()
                        try:
                            MainController.check_choice(user_input, list(add_player_method_options.keys()))
                            break
                        except ValueError as e:
                            view.show_message(e)
                            continue
                    
                    choice = add_player_method_options[user_input]

                    match choice:

                        case "Sélectionner les participants à partir de la liste des joueurs":
                            options = {}
                            selected_players = []
                            
                            for i, player in enumerate (sorted(player_list, key = lambda p : p.first_name), start = 1):
                                options[str(i)] = player
                                view.show_message(f"{i} : {player}")
                            view.show_message("Indiquez les chiffres de chaque joueur, séparés d'une virgule")
                            user_input = view.get_input()
                            user_input = user_input.split(",")
                            try:
                                for element in user_input:
                                    if element not in list(options.keys()):
                                        raise ValueError("Au moins une saisie ne correspond pas aux joueurs existants, veuillez recommencer")
                                        
                            except ValueError as e:
                                view.show_message(e)
                                continue
                                
                            for element in user_input :
                                selected_players.append(options[element])
                                

                            self.tournament_list[-1].registered_players = selected_players
                            view.show_message("Les joueurs ont bien été ajoutés pour ce tournoi")
                            view.show_message(self.tournament_list[-1])
                                        

                        case "Rechercher manuellement":
                            pass
                                
                                
                case "Description":
                    try:
                        new_tournament_description = view.display_interface_tournament_data(choice)
                        MainController.check_input_data(new_tournament_description, choice)
                        selected_tournament.description = new_tournament_description.upper()
                        view.show_message(f"La description du tournoi a bien été modifiée")
                        
                    except ValueError as e:
                        view.show_message(e)
                        continue
            
            repo_tournament.save_tournaments(self.tournament_list)

            while True:
                view.show_message("Voulez vous modifier une autre information pour ce tournoi ? y/n")
                input_user = view.get_input().lower()

                if input_user == "y":
                    input_user = view.display_submenu_tournament_modification(options, selected_tournament)
                    choice = options[int(input_user) - 1]
                    break
                elif input_user == "n":
                    return
                else:
                    view.show_message("Veuillez entrer un choix valide (y/n)")

    def handle_restoration_database_tournament_interface(self, view: Views.TournamentView, tournament_repo : Repositories.TournamentRepository):
        options = ["y", "n"]
        view.show_message("Etes vous sûr de vouloir restaurer la base de données des tournois depuis le fichier de restauration? y/n")
        while True:
        
            choice = view.get_input()

            try :
                MainController.check_choice(choice, options)
            except ValueError as e:
                view.show_message(e)
            match choice:
                case "y":
                    if tournament_repo.load_all() == None:
                        return
                    else : 
                        self.tournament_list = tournament_repo.load_all()
                        view.show_message("La liste des tournois a bien été restaurée")
                        return
                case "n":
                    return
                
    def format_date_tournament(self, day, month, year):
        formatted_date = (day + "/" + month + "/" + year)
        return formatted_date

    def tournament_research(self, input_user: str):
        correspondances = []
        fields = ["name", "location", "start_date", "end_date"]

        if not self.tournament_list:
            raise ValueError("La liste des tournois est vide, veuillez d'abord créer un tournoi")

        for tournament in self.tournament_list:
            if tournament.finished == False:
                for element in fields:
                    if input_user.upper() in str(getattr(tournament, element)).upper():
                        correspondances.append(tournament)
                        break
            else :
                raise ValueError("Il n'y a pas aucun tournoi en cours ou à venir pour l'instant")
            
        return correspondances

    def _validate_not_empty(self, value: str, key: str = "demandé"):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Le champ {key} ne peut pas être vide")
        
class PlayerController:

    def __init__(self):
        self.player_list = []

    def run(self, view: Views.PlayerView, player_repo : Repositories.PlayerRepository):
        try:
            self.player_list = player_repo.load_all()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.player_list = []
        
        options = {"1" : "Ajouter un joueur",
                   "2" : "Modifier un joueur", 
                   "3" : "Voir la liste des joueurs",
                   "4" : "Restaurer la base de données des joueurs",
                   "5" : "Retour au menu principal"}
        while True:
            view.display_menu(options)
            input_user = view.get_input()
            try:
                MainController.check_choice(input_user, list(options.keys()))
            except ValueError as e:
                view.show_message(e)
                continue
            choice = options[input_user]
            if self.handle_start_menu_player(choice, view, player_repo) == "quit":
                return

    def handle_start_menu_player(self, choice, view: Views.PlayerView, player_repo : Repositories.PlayerRepository):

            match choice:
                case "Ajouter un joueur":
                    self.handle_add_player_menu(view, player_repo)
                    return
                case "Modifier un joueur":
                    self.handle_modify_player_menu(view, player_repo)
                    return
                case "Voir la liste des joueurs":
                    view.show_player_list(self.player_list)
                    return
                case "Restaurer la base de données des joueurs":
                    self.handle_restoration_database_player_interface(view, player_repo)
                    return
                case "Retour au menu principal": 
                    return "quit"

    def handle_add_player_menu(self, view: Views.PlayerView, player_repo : Repositories.PlayerRepository):
        new_player_data = {}

        player_data_needed = [  "Prénom",
                                "Nom",
                                "Jour de naissance",
                                "Mois de naissance",
                                "Année de naissance",
                                "Identifiant national"]
        
        title = "AJOUTER UN JOUEUR"
        view.show_title(title)
        for element in player_data_needed:
            while True:
                input_user = view.display_interface_player_data(element).upper()
                try:
                    MainController.check_input_data(input_user, element)
                    new_player_data[element] = input_user
                    break
                except ValueError as e:
                    view.show_message(e)

        formatted_birthdate = self.format_birthdate_player(new_player_data["Jour de naissance"],
                                                           new_player_data["Mois de naissance"],
                                                           new_player_data["Année de naissance"])
        del new_player_data["Jour de naissance"],
        new_player_data["Mois de naissance"],
        new_player_data["Année de naissance"]

        new_player_data["Date de naissance"] = formatted_birthdate
        
        player = self.create_player(new_player_data)
        self.player_list.append(player)
        player_repo.save_players(self.player_list)
        view.show_message(f"Le joueur {player} a été créé avec succès")

    def handle_modify_player_menu(self, view: Views.PlayerView, player_repo : Repositories.PlayerRepository):
        options = {"1" : "Prénom",
                   "2" : "Nom",
                   "3" : "Date de naissance",
                   "4" : "Identifiant national",
                   "5" : "Quitter"}
        
        no_match_message = "Aucune correspondance trouvée"
        while True:
            researched_player = view.display_player_modification_research()
            try:
                self._validate_not_empty(researched_player)
                break
            except ValueError as e:
                view.show_message(e)
        possible_match = self.player_research(researched_player)

        if not possible_match:
            view.show_message(no_match_message)
            return

        elif len(possible_match) == 1:
            selected_player = possible_match[0]

        else:
            while True:
                try:
                    match = view.display_player_research_match(possible_match)
                    if int(match) in range(1, len(possible_match) + 1):
                        selected_player = possible_match[int(match) - 1]
                        break
                    else:
                        view.show_message("Entrez le chiffre correspondant à votre choix")
                except ValueError:
                    view.show_message("Entrez un nombre valide")
        while True:
            input_user = view.display_submenu_player_modification(options, selected_player)
            try :
                MainController.check_choice(input_user, list(options.keys()))
                break
            except ValueError as e:
                view.show_message(e)
                continue
        choice = options[input_user]
        while True:
            match choice:

                case "Prénom":
                    try:
                        new_first_name = view.display_interface_player_data(choice)
                        MainController.check_input_data(new_first_name, choice)
                        selected_player.first_name = new_first_name.upper()
                        view.show_message(f"Le prénom a été modifié en {selected_player.first_name}")
                        
                    except ValueError as e:
                        view.show_message(e)
                        continue

                case "Nom":
                    try:
                        new_last_name = view.display_interface_player_data(choice)
                        MainController.check_input_data(new_last_name, choice)
                        selected_player.last_name = new_last_name.upper()
                        view.show_message(f"Le nom a été modifié en {selected_player.last_name}")
                        
                    except ValueError as e:
                        view.show_message(e)
                        continue

                case "Date de naissance":
                    new_birth_date = []
                    for element in ("Jour de naissance", "Mois de naissance", "Année de naissance"):
                        while True:
                            try:
                                new_data = (view.display_interface_player_data(element))
                                MainController.check_input_data(new_data, element)
                                new_birth_date.append(new_data)
                                break
  
                            except ValueError as e:
                                view.show_message(e)
                                continue

                    new_birth_date = self.format_birthdate_player(new_birth_date[0], new_birth_date[1], new_birth_date[2])
                    selected_player.birth_date = new_birth_date
                    view.show_message(f"La date de naissance a été modifiée en {selected_player.birth_date}")
                    
                        

                case "Identifiant national":
                    try:
                        new_id = view.display_interface_player_data(choice)
                        MainController.check_input_data(new_id, choice)
                        selected_player.player_id = new_id.upper()
                        view.show_message(f"L'identifiant a été modifié en {selected_player.player_id}")
                        
                    except ValueError as e:
                        view.show_message(e)
                        continue
                
                case "Quitter":
                    return

            player_repo.save_players(self.players_list)

            while True:
                view.show_message("Voulez vous modifier une autre information pour ce joueur ? y/n")
                input_user = view.get_input().lower()

                if input_user == "y":
                    input_user = view.display_submenu_player_modification(options, selected_player)
                    choice = options[input_user]
                    break
                elif input_user == "n":
                    return
                else:
                    view.show_message("Veuillez entrer un choix valide (y/n)")
    
    def handle_restoration_database_player_interface(self, view: Views.PlayerView, player_repo : Repositories.PlayerRepository):
        possible_choices = ["y", "n"]
        view.show_message("Etes vous sûr de vouloir restaurer la base de données des joueurs depuis le fichier de restauration? y/n")
        while True:
            choice = view.get_input()
            try :
                MainController.check_choice(choice, possible_choices)
            except ValueError as e:
                view.show_message(e)
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
            raise ValueError(f"Le champ {key} ne peut pas être vide")