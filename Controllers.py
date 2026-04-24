import Views
import Models
import Repositories
import re
import random
from datetime import datetime
from pathlib import Path


class MainController:

    BASE_DIR = Path(__file__).resolve().parent
    filename_repo_players = BASE_DIR / "data" / "players.json"
    filename_repo_tournament = BASE_DIR / "data" / "tournament.json"

    def __init__(self):
        self.player_view = Views.PlayerView()
        self.tournament_view = Views.TournamentView()
        self.report_view = Views.ReportView()

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

        self.report_controller = ReportController(
            self.report_view,
            self.player_repository,
            self.tournament_repository
        )

    def run(self):

        self.tournament_repository.load_all(bootload=True)
        self.player_repository.load_all(bootload=True)

        options = {
            "1": "Gérer les joueurs",
            "2": "Gérer les tournois",
            "3": "Rapports",
            "4": "Quitter"
        }

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
            choice = options[user_input]
            if self.handle_start_menu_choice(choice) == "quit":
                return

    def handle_start_menu_choice(self, choice):
        match choice:
            case "Gérer les joueurs":
                self.player_controller.run()
            case "Gérer les tournois":
                self.tournament_controller.run()
            case "Rapports":
                self.report_controller.run()
            case "Quitter":
                return "quit"

    @staticmethod
    def check_input_data(input, data, ID_PATTERN=r"[A-Z]{2}\d{5}"):
        if not isinstance(input, str) or not input.strip():
            raise ValueError(f"Le champ {data} ne peut pas être vide")
        if "Jour" in data:
            if not re.fullmatch(r"[0-9]{2}", input):
                raise ValueError(f"{data} invalide, format attendu '00'")
        elif "Mois" in data:
            if not re.fullmatch(r"[0-9]{2}", input):
                raise ValueError(f"{data} invalide, format attendu '00'")
        elif "Année" in data:
            if not re.fullmatch(r"[0-9]{4}", input):
                raise ValueError(f"{data} invalide, format attendu '0000'")
        elif "Identifiant" in data:
            if not re.fullmatch(ID_PATTERN, input.upper()):
                raise ValueError("ID invalide (format attendu : AB12345)")

    @staticmethod
    def check_choice(input_user: str, choice_possibilities: list):
        if input_user not in choice_possibilities:
            raise ValueError(f"Vous devez choisir parmi les choix {','.join(choice_possibilities)}")

    @staticmethod
    def _validate_not_empty(value: str, key: str = "demandé"):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Le champ {key} ne peut pas être vide")

    @staticmethod
    def check_yes_no_choice(input_user: str):
        choice = ["y", "n"]
        if input_user not in choice:
            raise ValueError(f"Vous devez choisir parmi les choix {choice[0]} ou {choice[1]}")

    @staticmethod
    def format_date(day, month, year):
        return day + "/" + month + "/" + year


class TournamentController:

    def __init__(self, tournament_view: Views.TournamentView,
                 player_repo: Repositories.PlayerRepository,
                 tournament_repo: Repositories.TournamentRepository):
        self.tournament_view = tournament_view
        self.player_repository = player_repo
        self.tournament_repository = tournament_repo

    def run(self):
        title = "MENU DE GESTION DES TOURNOIS"
        options = {
            "1": "Créer un tournoi",
            "2": "Modifier un tournoi à venir",
            "3": "Gérer un tournoi en cours",
            "4": "Sauvegarder la base de données des tournois",
            "5": "Restaurer la base de données des tournois",
            "6": "Retour au menu principal"
        }

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
            case "Modifier un tournoi à venir":
                self.handle_modify_unfinished_tournament_interface()
            case "Gérer un tournoi en cours":
                self.handle_in_progress_tournament_interface()
            case "Sauvegarder la base de données des tournois":
                self.tournament_repository.save_backup()
                self.tournament_view.show_message("Sauvegarde effectuée avec succès")
            case "Restaurer la base de données des tournois":
                self.handle_restoration_database_tournament_interface()
            case "Retour au menu principal":
                return "quit"

    # Gestion d'un tournoi en cours

    def handle_in_progress_tournament_interface(self):
        self.tournament_view.display_interface_in_progress_tournament()

        active = [t for t in self.tournament_repository.tournaments
                  if not t.finished and t.registered_players]
        if not active:
            self.tournament_view.show_message("Aucun tournoi en cours avec des joueurs inscrits.")
            return

        for i, t in enumerate(active, start=1):
            status = f"Round {t.current_round}/{t.nb_rounds}"
            self.tournament_view.show_message(f"{i}. {t.name} ({t.start_date}) - {status}")
        self.tournament_view.show_message("Choisissez un tournoi")
        while True:
            user_input = self.tournament_view.get_input()
            try:
                formatted_user_input = int(user_input)
                if 1 <= formatted_user_input <= len(active):
                    break
                self.tournament_view.show_message("Choix invalide.")
            except ValueError:
                self.tournament_view.show_message("Entrez un nombre valide.")

        tournament = active[formatted_user_input - 1]
        self.manage_tournament_rounds(tournament)

    def manage_tournament_rounds(self, tournament: Models.Tournament):
        while True:
            scores = tournament.get_scores()
            scores_display = sorted(
                [(f"{p.first_name} {p.last_name}", scores.get(p.uuid_value, 0.0))
                 for p in tournament.registered_players],
                key=lambda x: x[1], reverse=True
            )
            self.tournament_view.display_scores(scores_display)

            if tournament.current_round >= tournament.nb_rounds:
                tournament.finished = True
                self.tournament_repository.update_tournament(tournament)
                self.tournament_view.show_message(f"\nTournoi '{tournament.name}' terminé !")
                return

            current_round = None
            if tournament.rounds and tournament.current_round > 0:
                last = tournament.rounds[-1]
                if isinstance(last, Models.Round) and not all(m.finished for m in last.match_list):
                    current_round = last

            if current_round is None:
                options = {"1": "Générer le prochain round", "2": "Retour"}
                while True:
                    self.tournament_view.display_menu(options)
                    user_input = self.tournament_view.get_input()
                    if user_input not in options:
                        self.tournament_view.show_message("Choix invalide. Entrez 1 ou 2.")
                        continue
                    if user_input == "2":
                        return
                    current_round = self.generate_round(tournament)
                    tournament.rounds.append(current_round)
                    tournament.current_round += 1
                    self.tournament_repository.update_tournament(tournament)
                    self.tournament_view.show_message(f"\n{current_round.round_number} généré.")
                    break

            self.tournament_view.display_round_summary(current_round)
            self.enter_round_results(current_round, tournament)

    def generate_round(self, tournament: Models.Tournament):
        scores = tournament.get_scores()
        played_pairs = tournament.get_played_pairs()
        round_number = tournament.current_round + 1

        if round_number == 1:
            players = list(tournament.registered_players)
            random.shuffle(players)
        else:
            players = sorted(
                tournament.registered_players,
                key=lambda p: scores.get(p.uuid_value, 0.0),
                reverse=True
            )

        matches = self.pair_players(players, played_pairs)
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        return Models.Round(matches, f"Round {round_number}", now, "")

    def pair_players(self, players: list, played_pairs: set):
        matches = []
        remaining = list(players)

        while len(remaining) >= 2:
            p1 = remaining.pop(0)
            paired = False
            for i, p2 in enumerate(remaining):
                if frozenset([p1.uuid_value, p2.uuid_value]) not in played_pairs:
                    matches.append(Models.Match(p1, p2))
                    remaining.pop(i)
                    paired = True
                    break
            if not paired:
                p2 = remaining.pop(0)
                matches.append(Models.Match(p1, p2))

        return matches

    def enter_round_results(self, rnd: Models.Round, tournament: Models.Tournament):
        for match in rnd.match_list:
            if match.finished:
                continue
            self.tournament_view.show_message(
                f"\n{match.player1.first_name} {match.player1.last_name} "
                f"vs {match.player2.first_name} {match.player2.last_name}"
            )
            self.tournament_view.display_match_result_input(match)
            while True:
                choice = self.tournament_view.get_input()
                if choice == "1":
                    match.player1_score, match.player2_score = 1.0, 0.0
                    match.player1_result, match.player2_result = "Victoire", "Défaite"
                    match.finished = True
                    break
                elif choice == "2":
                    match.player1_score, match.player2_score = 0.0, 1.0
                    match.player1_result, match.player2_result = "Défaite", "Victoire"
                    match.finished = True
                    break
                elif choice == "3":
                    match.player1_score, match.player2_score = 0.5, 0.5
                    match.player1_result, match.player2_result = "Nul", "Nul"
                    match.finished = True
                    break
                else:
                    self.tournament_view.show_message("Entrez 1, 2 ou 3.")

        rnd.end_round = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.tournament_repository.update_tournament(tournament)
        self.tournament_view.show_message(f"\n{rnd.round_number} terminé et sauvegardé.")

    # Création de tournoi

    def handle_tournament_creation_menu(self):

        data_needed = [
            "Nom du tournoi", "Ville du tournoi",
            "Jour de démarrage", "Mois de démarrage", "Année de démarrage",
            "Jour de fin", "Mois de fin", "Année de fin",
            "Description"
        ]
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

        formatted_start_date = MainController.format_date(
            new_tournament_data["Jour de démarrage"],
            new_tournament_data["Mois de démarrage"],
            new_tournament_data["Année de démarrage"]
        )
        formatted_end_date = MainController.format_date(
            new_tournament_data["Jour de fin"],
            new_tournament_data["Mois de fin"],
            new_tournament_data["Année de fin"]
        )

        for key in ["Jour de démarrage", "Mois de démarrage", "Année de démarrage",
                    "Jour de fin", "Mois de fin", "Année de fin"]:
            del new_tournament_data[key]

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
                for i, player in enumerate(
                    sorted(self.player_repository.players, key=lambda p: p.first_name), start=1
                ):
                    registrable_players[str(i)] = player
                    self.tournament_view.show_message(f"{i} : {player}")
                self.tournament_view.show_message("Indiquez les chiffres de chaque joueur, séparés d'une virgule")
                user_input = self.tournament_view.get_input()
                user_input = user_input.replace(" ", "").split(",")
                try:
                    for element in user_input:
                        if element not in list(registrable_players.keys()):
                            raise ValueError("Au moins une saisie ne correspond pas aux joueurs existants")
                except ValueError as e:
                    self.tournament_view.show_message(e)
                    continue

                for element in user_input:
                    selected_players.append(registrable_players[element])

                new_tournament.registered_players = selected_players
                self.tournament_repository.update_tournament(new_tournament)
                self.tournament_view.show_message(new_tournament)

            self.tournament_view.show_message(f"Le tournoi {new_tournament.name} a été créé avec succès")
            return

    # Modification d'un tournoi

    def handle_modify_unfinished_tournament_interface(self):

        options = {
            "1": "Nom", "2": "Ville", "3": "Date de démarrage", "4": "Date de fin",
            "5": "Joueurs participants", "6": "Description", "7": "Nombre de rounds", "8": "Retour"
        }

        if not self.tournament_repository.tournaments:
            self.tournament_view.show_message("La liste des tournois est vide")
            return
        if not any(not t.finished for t in self.tournament_repository.tournaments):
            self.tournament_view.show_message("Il n'y a aucun tournoi en cours ou à venir pour l'instant")
            return

        while True:
            researched_tournament = self.tournament_view.display_tournament_research()
            try:
                MainController._validate_not_empty(researched_tournament)
                break
            except ValueError as e:
                self.tournament_view.show_message(e)
        possible_matches = self.tournament_research(researched_tournament)

        if not possible_matches:
            self.tournament_view.show_message("Aucune correspondance trouvée")
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
                        self.tournament_view.show_message(f"Nom modifié en {selected_tournament.name}")
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
                        self.tournament_view.show_message(f"Ville modifiée en {selected_tournament.location}")
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
                    new_data["start_date"] = MainController.format_date(*new_start_date)
                    selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                    self.tournament_repository.update_tournament(selected_tournament)
                    msg = f"Date de démarrage modifiée en {selected_tournament.start_date}"
                    self.tournament_view.show_message(msg)

                case "Date de fin":
                    new_end_date = []
                    for element in ("Jour de fin", "Mois de fin", "Année de fin"):
                        while True:
                            try:
                                self.tournament_view.display_interface_tournament_data(element)
                                user_input = self.tournament_view.get_input()
                                MainController.check_input_data(user_input, element)
                                new_end_date.append(user_input)
                                break
                            except ValueError as e:
                                self.tournament_view.show_message(e)
                    new_data["end_date"] = MainController.format_date(*new_end_date)
                    selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                    self.tournament_repository.update_tournament(selected_tournament)
                    self.tournament_view.show_message(f"Date de fin modifiée en {selected_tournament.end_date}")

                case "Joueurs participants":
                    registrable_players = {}
                    players_to_register = []
                    for i, player in enumerate(
                        sorted(self.player_repository.players, key=lambda p: p.first_name), start=1
                    ):
                        registrable_players[str(i)] = player
                        self.tournament_view.show_message(f"{i} : {player}")
                    self.tournament_view.show_message("Indiquez les chiffres de chaque joueur, séparés d'une virgule")
                    user_input = self.tournament_view.get_input()
                    formated_user_input = user_input.replace(" ", "").split(",")
                    try:
                        for element in formated_user_input:
                            if element not in list(registrable_players.keys()):
                                raise ValueError("Au moins une saisie ne correspond pas aux joueurs existants")
                    except ValueError as e:
                        self.tournament_view.show_message(e)
                        continue
                    for element in formated_user_input:
                        players_to_register.append(registrable_players[element])
                    new_data["registered_players"] = players_to_register
                    selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                    self.tournament_repository.update_tournament(selected_tournament)
                    self.tournament_view.show_message("Les joueurs ont bien été ajoutés pour ce tournoi")

                case "Description":
                    try:
                        self.tournament_view.display_interface_tournament_data(choice)
                        user_input = self.tournament_view.get_input()
                        MainController.check_input_data(user_input, choice)
                        new_data["description"] = user_input.upper()
                        selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                        self.tournament_repository.update_tournament(selected_tournament)
                        self.tournament_view.show_message("Description modifiée.")
                    except ValueError as e:
                        self.tournament_view.show_message(e)
                        continue

                case "Nombre de rounds":
                    try:
                        self.tournament_view.display_interface_tournament_data(choice)
                        user_input = self.tournament_view.get_input()
                        if not user_input.strip().isdigit():
                            raise ValueError("Le nombre de rounds doit être un entier.")
                        new_data["nb_rounds"] = int(user_input)
                        selected_tournament = self.modify_existing_tournament(selected_tournament, new_data)
                        self.tournament_repository.update_tournament(selected_tournament)
                        msg = f"Nombre de rounds modifié en {selected_tournament.nb_rounds}"
                        self.tournament_view.show_message(msg)
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

    def tournament_research(self, input_user: str):
        correspondances = []
        fields = ["name", "location", "start_date", "end_date"]
        if not self.tournament_repository.tournaments:
            raise ValueError("La liste des tournois est vide")
        for tournament in self.tournament_repository.tournaments:
            if tournament is None:
                continue
            if not tournament.finished:
                for element in fields:
                    if input_user.upper() in str(getattr(tournament, element)).upper():
                        correspondances.append(tournament)
                        break
        return correspondances

    def create_new_tournament(self, new_tournament_data: dict):
        return Models.Tournament(
            name=new_tournament_data["Nom du tournoi"],
            location=new_tournament_data["Ville du tournoi"],
            start_date=new_tournament_data["Date de démarrage"],
            end_date=new_tournament_data["Date de fin"],
            description=new_tournament_data["Description"],
        )

    def modify_existing_tournament(self, tournament: Models.Tournament, new_tournament_data: dict):
        for key, value in new_tournament_data.items():
            if value is not None:
                setattr(tournament, key, value)
        return tournament

    # Restauration du backup_tournaments

    def handle_restoration_database_tournament_interface(self):

        possible_choices = ["y", "n"]
        self.tournament_view.show_message(
            "Etes vous sûr de vouloir restaurer votre dernière sauvegarde des tournois ? y/n"
        )
        while True:
            choice = self.tournament_view.get_input()
            try:
                MainController.check_choice(choice, possible_choices)
            except ValueError as e:
                self.tournament_view.show_message(e)
                continue
            match choice:
                case "y":
                    try:
                        self.tournament_repository.restore_backup()
                        self.tournament_view.show_message("La liste des tournois a bien été restaurée")
                    except FileNotFoundError as e:
                        self.tournament_view.show_message(str(e))
                    return
                case "n":
                    return


class PlayerController:

    def __init__(self, player_view: Views.PlayerView,
                 player_repo: Repositories.PlayerRepository,
                 tournament_repo: Repositories.TournamentRepository):
        self.player_view = player_view
        self.player_repository = player_repo
        self.tournament_repository = tournament_repo

    def run(self):
        options = {
            "1": "Ajouter un joueur",
            "2": "Modifier un joueur",
            "3": "Sauvegarder la base de données des joueurs",
            "4": "Restaurer la base de données des joueurs",
            "5": "Retour au menu principal"
        }
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
            case "Modifier un joueur":
                self.handle_modify_player_menu()
            case "Sauvegarder la base de données des joueurs":
                self.player_repository.save_backup()
                self.player_view.show_message("Sauvegarde effectuée avec succès")
            case "Restaurer la base de données des joueurs":
                self.handle_restoration_database_player_interface()
            case "Retour au menu principal":
                return "quit"

    # Création d'un joueur

    def handle_add_player_menu(self):
        new_player_data = {}
        player_data_needed = [
            "Prénom", "Nom",
            "Jour de naissance", "Mois de naissance", "Année de naissance",
            "Identifiant national"
        ]
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

        formatted_birthdate = MainController.format_date(
            new_player_data["Jour de naissance"],
            new_player_data["Mois de naissance"],
            new_player_data["Année de naissance"]
        )
        del new_player_data["Jour de naissance"]
        del new_player_data["Mois de naissance"]
        del new_player_data["Année de naissance"]
        new_player_data["Date de naissance"] = formatted_birthdate

        similar_players = [p for p in self.player_repository.players
                           if new_player_data["Identifiant national"] == p.player_id]
        if similar_players:
            self.player_view.show_message("Un ou plusieurs joueurs existants ont le même identifiant.")
            for p in similar_players:
                self.player_view.show_message(p)
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
        self.player_view.show_message(
            f"Le joueur {new_player_data['Prénom']} {new_player_data['Nom']} a été créé avec succès"
        )

    def create_player(self, new_player_data):
        try:
            return Models.Player(
                new_player_data["Prénom"],
                new_player_data["Nom"],
                new_player_data["Date de naissance"],
                new_player_data["Identifiant national"]
            )
        except ValueError:
            print("Erreur lors de la création du joueur")

    # Modification d'un joueur

    def handle_modify_player_menu(self):
        options = {
            "1": "Prénom", "2": "Nom", "3": "Date de naissance",
            "4": "Identifiant national", "5": "Quitter"
        }
        impacted_tournament = []

        while True:
            researched_player = self.player_view.display_player_modification_research()
            try:
                MainController._validate_not_empty(researched_player)
                break
            except ValueError as e:
                self.player_view.show_message(e)
        try:
            possible_match = self.player_research(researched_player)
        except ValueError as e:
            self.player_view.show_message(e)
            return

        if not possible_match:
            self.player_view.show_message("Aucune correspondance trouvée")
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
                self.player_view.show_message(
                    f"Changer les données du joueur {selected_player} va impacter les tournois ci-dessus, "
                    f"voulez vous continuer? y/n"
                )
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
            try:
                MainController.check_choice(input_user, list(options.keys()))
                break
            except ValueError as e:
                self.player_view.show_message(e)

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
                        self.player_view.show_message(f"Prénom modifié en {selected_player.first_name}")
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
                        self.player_view.show_message(f"Nom modifié en {selected_player.last_name}")
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
                    new_data["birth_date"] = MainController.format_date(*new_birth_date)
                    selected_player = self.modify_existing_player(selected_player, new_data)
                    self.player_repository.update_player(selected_player)
                    self.player_view.show_message(f"Date de naissance modifiée en {selected_player.birth_date}")

                case "Identifiant national":
                    try:
                        self.player_view.display_interface_player_data(choice)
                        user_input = self.player_view.get_input()
                        MainController.check_input_data(user_input, choice)
                        new_data["player_id"] = user_input.upper()
                        selected_player = self.modify_existing_player(selected_player, new_data)
                        self.player_repository.update_player(selected_player)
                        self.player_view.show_message(f"Identifiant modifié en {selected_player.player_id}")
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

    def check_impact_modification(self, player_to_modify: list):
        impacted_tournament = []
        for tournament in self.tournament_repository.tournaments:
            if not tournament.registered_players:
                continue
            if any(
                player.uuid_value == rp.uuid_value
                for player in player_to_modify
                for rp in tournament.registered_players
            ):
                impacted_tournament.append(tournament)
        return impacted_tournament

    def modify_existing_player(self, player: Models.Player, new_player_data: dict):
        for key, value in new_player_data.items():
            if value:
                setattr(player, key, value)
        return player

    # Restauration du backup_players

    def handle_restoration_database_player_interface(self):
        possible_choices = ["y", "n"]
        self.player_view.show_message(
            "Etes vous sûr de vouloir restaurer votre dernière sauvegarde des joueurs ? y/n"
        )
        while True:
            choice = self.player_view.get_input()
            try:
                MainController.check_choice(choice, possible_choices)
            except ValueError as e:
                self.player_view.show_message(e)
                continue
            match choice:
                case "y":
                    try:
                        self.player_repository.restore_backup()
                        self.player_view.show_message("La liste des joueurs a bien été restaurée")
                    except FileNotFoundError as e:
                        self.player_view.show_message(str(e))
                    return
                case "n":
                    return


class ReportController:

    def __init__(self, report_view: Views.ReportView,
                 player_repo: Repositories.PlayerRepository,
                 tournament_repo: Repositories.TournamentRepository):
        self.report_view = report_view
        self.player_repository = player_repo
        self.tournament_repository = tournament_repo

    def run(self):
        options = {
            "1": "Liste de tous les joueurs (alphabétique)",
            "2": "Liste de tous les tournois",
            "3": "Nom et dates d'un tournoi donné",
            "4": "Liste des joueurs d'un tournoi (alphabétique)",
            "5": "Tours et matchs d'un tournoi",
            "6": "Retour au menu principal"
        }
        while True:
            self.report_view.display_menu(options)
            user_input = self.report_view.get_input()
            try:
                MainController.check_choice(user_input, list(options.keys()))
            except ValueError as e:
                self.report_view.show_message(e)
                continue
            choice = options[user_input]
            if self.handle_report_choice(choice) == "quit":
                return

    def handle_report_choice(self, choice):
        match choice:
            case "Liste de tous les joueurs (alphabétique)":
                sorted_players = sorted(self.player_repository.players, key=lambda p: p.last_name)
                self.report_view.display_all_players(sorted_players)
            case "Liste de tous les tournois":
                self.report_view.display_all_tournaments(self.tournament_repository.tournaments)
            case "Nom et dates d'un tournoi donné":
                tournament = self.select_tournament()
                if tournament:
                    self.report_view.display_tournament_info(tournament)
            case "Liste des joueurs d'un tournoi (alphabétique)":
                tournament = self.select_tournament()
                if tournament:
                    sorted_players = sorted(tournament.registered_players, key=lambda p: p.last_name)
                    self.report_view.display_tournament_players(tournament, sorted_players)
            case "Tours et matchs d'un tournoi":
                tournament = self.select_tournament()
                if tournament:
                    self.report_view.display_tournament_rounds(tournament)
            case "Retour au menu principal":
                return "quit"

    def select_tournament(self):
        if not self.tournament_repository.tournaments:
            self.report_view.show_message("Aucun tournoi enregistré.")
            return None

        researched = self.report_view.display_tournament_research()
        try:
            MainController._validate_not_empty(researched)
        except ValueError as e:
            self.report_view.show_message(e)
            return None

        matches = [
            t for t in self.tournament_repository.tournaments
            if researched.upper() in t.name.upper() or researched.upper() in t.location.upper()
        ]
        if not matches:
            self.report_view.show_message("Aucune correspondance trouvée.")
            return None
        if len(matches) == 1:
            return matches[0]

        choice = self.report_view.display_tournament_research_matches(matches)
        try:
            idx = int(choice)
            if 1 <= idx <= len(matches):
                return matches[idx - 1]
        except ValueError:
            pass
        self.report_view.show_message("Choix invalide.")
        return None
