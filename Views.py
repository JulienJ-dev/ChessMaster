from abc import ABC, abstractmethod
import Models


class BaseView(ABC):

    @abstractmethod
    def display_menu(self, options):
        pass

    def get_input(self, prompt = "> "):
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
    
    def display_menu(self, options : dict):
        title = "MENU PRINCIPAL"
        self.show_title(title)
        
        for key, value in options.items():
            print (f"{key}. {value}")
        
        return
         
            
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
        else :
            self.show_message("LA LISTE DE JOUEUR EST VIDE")
    
    def display_submenu_player_modification(self, options : dict, player : Models.Player):
        self.show_message(f"\n{player}\n")
        for key, value in options.items():
            self.show_message(f"{key}. {value}")
        self.show_message(f"Quelle information du joueur {player.first_name} {player.last_name} voulez vous modifier?")
        return self.get_input()

    def display_player_research_match(self, matches):
        for i, match in enumerate(matches, start = 1):
            self.show_message(f"{i}. {match}")
        self.show_message("Choisissez le joueur recherché")
        return self.get_input()

    def display_interface_player_data(self, data_needed):
        self.show_message(data_needed)
        return self.get_input()


class TournamentView(BaseView) :
    
    def display_menu(self, options : dict):
        title = "MENU DE GESTION DES TOURNOIS"
        self.show_title(title)
        for key,value in options.items():
            self.show_message(f"{key}. {value}")
    
    def display_interface_tournament_data(self, data_needed):
            self.show_message(data_needed)
            return self.get_input()
    
    def display_submenu_tournament_modification(self, options, tournament : Models.Tournament):
        self.show_message(f"{tournament}\n")
        for key, value in options.items():
            self.show_message(f"{key}. {value}")
        self.show_message(f"Quelle information du tournoi '{tournament.name}' voulez vous modifier?")
        return self.get_input()

    def display_interface_in_progress_tournament(self, options):
        title = "INTERFACE DE GESTION DES TOURNOIS EN COURS"
        self.show_title(title)
        
    def display_tournament_research(self):
        self.show_message("Quel tournoi recherchez vous?")
        return self.get_input()
    
    def display_tournament_research_matches(self, matches):
        for i, match in enumerate(matches, start = 1):
            self.show_message(f"{i}. {match}")
        self.show_message("Choisissez le tournoi recherché")
        return self.get_input()
    
    def show_tournament_list(self, tournament_list):
        if tournament_list:
            for element in tournament_list:
                self.show_message(element)
                self.show_message("\n" + "-" * 50 + "\n")