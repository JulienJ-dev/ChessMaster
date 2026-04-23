from abc import ABC, abstractmethod
import Models


class BaseView(ABC):

    @abstractmethod
    def display_menu(self, options):
        pass

    def get_input(self, prompt="> "):
        return input(prompt)

    def show_message(self, msg):
        print(msg)

    def show_title(self, title):
        print("\n" + "-" * len(title))
        print(title)
        print("-" * len(title) + "\n")


class MainView(BaseView):

    def show_welcome(self):
        text = "Bienvenue sur ChessMaster, votre logiciel de gestion de vos tournois d'échecs".upper()
        self.show_message("\n" + text)
        self.show_message("-" * len(text))

    def display_menu(self, options: dict):
        title = "MENU PRINCIPAL"
        self.show_title(title)
        for key, value in options.items():
            print(f"{key}. {value}")


class PlayerView(BaseView):

    def display_menu(self, options):
        title = "MENU DE GESTION DES JOUEURS"
        self.show_title(title)
        for key, value in options.items():
            self.show_message(f"{key}. {value}")

    def display_player_modification_research(self):
        title = "MODIFICATION D'UN JOUEUR"
        self.show_title(title)
        self.show_message("Quel est le joueur à modifier?\n")
        return self.get_input()

    def show_player_list(self, player_list):
        title = "LISTE DES JOUEURS"
        self.show_title(title)
        if player_list:
            for element in player_list:
                self.show_message(element)
        else:
            self.show_message("LA LISTE DE JOUEUR EST VIDE")

    def display_submenu_player_modification(self, options: dict, player: Models.Player):
        self.show_message(f"\n{player}\n")
        for key, value in options.items():
            self.show_message(f"{key}. {value}")
        self.show_message(f"Quelle information du joueur {player.first_name} {player.last_name} voulez vous modifier?")

    def display_player_research_match(self, matches):
        for i, match in enumerate(matches, start=1):
            self.show_message(f"{i}. {match}")
        self.show_message("Choisissez le joueur recherché")
        return self.get_input()

    def display_interface_player_data(self, data_needed):
        self.show_message(data_needed)


class TournamentView(BaseView):

    def display_menu(self, options: dict):
        for key, value in options.items():
            self.show_message(f"{key}. {value}")

    def display_interface_tournament_data(self, data_needed):
        self.show_message(data_needed)

    def display_submenu_tournament_modification(self, options, tournament: Models.Tournament):
        self.show_message(f"{tournament}\n")
        for key, value in options.items():
            self.show_message(f"{key}. {value}")
        self.show_message(f"Quelle information du tournoi '{tournament.name}' voulez vous modifier?")

    def display_interface_in_progress_tournament(self):
        title = "INTERFACE DE GESTION DES TOURNOIS EN COURS"
        self.show_title(title)

    def display_tournament_research(self):
        self.show_message("Quel tournoi recherchez vous?")
        return self.get_input()

    def display_tournament_research_matches(self, matches):
        for i, match in enumerate(matches, start=1):
            self.show_message(f"{i}. {match}")
        self.show_message("Choisissez le tournoi recherché")
        return self.get_input()

    def show_tournament_list(self, tournament_list):
        if tournament_list:
            for element in tournament_list:
                self.show_message(element)
                self.show_message("\n" + "-" * 50 + "\n")
        else:
            self.show_message("\nIl n'y a aucun tournoi enregistré\n")

    def display_match_result_input(self, match: Models.Match):
        self.show_message(f"\n  1. {match.player1.first_name} {match.player1.last_name} gagne")
        self.show_message(f"  2. {match.player2.first_name} {match.player2.last_name} gagne")
        self.show_message("  3. Match nul")
        self.show_message("Résultat de ce match ?")

    def display_round_summary(self, rnd: Models.Round):
        self.show_message(str(rnd))

    def display_scores(self, scores_display: list):
        title = "CLASSEMENT ACTUEL"
        self.show_title(title)
        for rank, (name, score) in enumerate(scores_display, start=1):
            self.show_message(f"  {rank}. {name} - {score} pt(s)")


class ReportView(BaseView):

    def display_menu(self, options: dict):
        title = "MENU DES RAPPORTS"
        self.show_title(title)
        for key, value in options.items():
            self.show_message(f"{key}. {value}")

    def display_all_players(self, players: list):
        title = "LISTE DE TOUS LES JOUEURS (ordre alphabétique)"
        self.show_title(title)
        if not players:
            self.show_message("Aucun joueur enregistré.")
            return
        for p in players:
            self.show_message(str(p))

    def display_all_tournaments(self, tournaments: list):
        title = "LISTE DE TOUS LES TOURNOIS"
        self.show_title(title)
        if not tournaments:
            self.show_message("Aucun tournoi enregistré.")
            return
        for t in tournaments:
            self.show_message(f"- {t.name} | {t.location} | {t.start_date} -> {t.end_date}")

    def display_tournament_info(self, tournament: Models.Tournament):
        title = f"INFORMATIONS : {tournament.name}"
        self.show_title(title)
        self.show_message(str(tournament))

    def display_tournament_players(self, tournament: Models.Tournament, players: list):
        title = f"JOUEURS DU TOURNOI : {tournament.name} (ordre alphabétique)"
        self.show_title(title)
        if not players:
            self.show_message("Aucun joueur inscrit.")
            return
        for p in players:
            self.show_message(str(p))

    def display_tournament_rounds(self, tournament: Models.Tournament):
        title = f"TOURS ET MATCHS : {tournament.name}"
        self.show_title(title)
        if not tournament.rounds:
            self.show_message("Aucun tour joué.")
            return
        for rnd in tournament.rounds:
            if isinstance(rnd, Models.Round):
                self.show_message(str(rnd))
                self.show_message("")

    def display_tournament_research(self):
        self.show_message("Quel tournoi recherchez vous?")
        return self.get_input()

    def display_tournament_research_matches(self, matches):
        for i, t in enumerate(matches, start=1):
            self.show_message(f"{i}. {t.name} ({t.start_date})")
        self.show_message("Choisissez le tournoi")
        return self.get_input()
