from abc import ABC, abstractmethod
import Models


class BaseView(ABC):

    @abstractmethod
    def display_menu(self):
        pass


    def get_input(self, prompt = "> "):
        return input(prompt)
    

    def show_message(self, msg):
        print(msg)


class MainView(BaseView):


    def show_welcome(self):
        text = "Bienvenue sur ChessMaster, votre logiciel de gestion de vos tournois d'échecs".upper()
        print("\n" + text)
        print("-" * len(text))
    
    def display_menu(self):
        possible_choices = []
        options = ["Gérer les joueurs", "Gérer les tournois", "Quitter"]
        title = "MENU PRINCIPAL"
        self.show_message("\n" + title)
        self.show_message("-" * len(title) + "\n")
        

        for i,  option in enumerate(options, start = 1):
            print (f"{i}. {option}")
            possible_choices.append(str(i))
        
        return possible_choices
         
            


class PlayerView(BaseView):


    def display_menu(self):
        options = ["Ajouter un joueur", "Modifier un joueur", "Voir la liste des joueurs", "Restaurer la base de données des joueurs", "Retour au menu principal"]
        possible_choices =[]
        titre_menu = "Menu de gestion des joueurs".upper()
        print("\n" + titre_menu)
        print("-" * len(titre_menu) + "\n")
        for i, option in enumerate(options, start = 1):
            print(f"{i}. {option}")
            possible_choices.append(str(i))
        
        return possible_choices
    
    def display_player_modification_research(self):
        section_title = "Modification d'un joueur".upper()
        print("\n" + section_title)
        print("-" * len(section_title) + "\n")
        print("Quel est le joueur à modifier?\n")
        return self.get_input()
    
    def display_player_list(self, player_list):
        if player_list:
            for element in player_list:
                print(element)
        else :
            print("\nLA LISTE DE JOUEUR EST VIDE")
    

    def display_submenu_player_modification(self, options, player : Models.Player):
        print(player)
        print()
        for i, option in enumerate(options, start = 1):
            print(f"{i}. {option}")
        print(f"Quelle information du joueur {player._first_name} {player._last_name} voulez vous modifier?")
        return self.get_input()



    def display_research_match(self, matchs):
        for i, match in enumerate(matchs, start = 1):
            print(f"{i}. {match}")
        print("Choisissez le joueur recherché")
        return self.get_input()

    def display_interface_player_data(self, data_needed):
        print(data_needed)
        return self.get_input()


   

    def show_edit_player_first_name(self,player : Models.Player):
        print(f"Prénom actuel : {player._first_name}")



class TournamentView(BaseView) :
    pass
