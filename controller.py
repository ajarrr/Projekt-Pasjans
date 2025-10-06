# -*- coding: utf-8 -*-
from config import *
from config import __debug
from logic import GameLogic
from ui import GameUI
from utils import display_scores


# Klasa zarządzająca główną logiką aplikacji
class GameController:
    def __init__(self):
        self.logic = GameLogic()
        self.ui = GameUI(self.logic)
        self.last_autosave = 2

    def run(self):
        self.logic.setup_board()
        print("Rozpoczynamy grę w Pasjansa!")

        while True:
            self.logic.check_win()
            os.system('cls')

            if self.logic.get_turn() > 0:
                if self.last_autosave == 0:
                    self.logic.save_game(save_file)
                    self.last_autosave = 2
                else:
                    self.last_autosave -= 1
                print("-" * 50)
            self.ui.display_board()
            self.logic.next_turn()

            print(f'\nObecna Tura: \033[1m{self.logic.get_turn()}\033[22m')
            if self.logic.get_turn() > 1:
                print(f"Poziom Trudności: {self.logic.get_difficulty()}")
            if self.logic.get_turn() == 1:
                print("\033[91mUWAGA:\033[39m Poziom trudności można wybrać tylko w 1 turze")
                print("0. Wybierz poziom trudności (Obecnie: ", self.logic.get_difficulty(), ")")
            print("1. Dobierz kartę ze stosu")
            print("2. Przenieś kartę")
            print("3. Przenieś kartę na stos końcowy")
            print("4. Cofnij ruch")
            print("5. Zakończ grę")
            print("6. Zasady gry")
            print("7. Wyświetl ranking graczy")
            if save_file_exist:
                print("8. Wczytaj ostani zapis gry")
            choice = input("Wybierz akcję: ")

            if self.logic.get_turn() == 1:
                if choice == "0":
                    level = input(
                        "1. Łatwy"
                        "\n2. Trudny"
                        "\nWybierz: ")
                    if level == "1":
                        self.logic.set_difficulty("Łatwy")
                    elif level == "2":
                        self.logic.set_difficulty("Trudny")
                    else:
                        handle_error(ErrorCode.INVALID_DIFFICULTY)
            elif choice == "1":
                self.logic.draw_from_waste()
            elif choice == "2":
                self._handle_move_card()
            elif choice == "3":
                self._handle_move_to_foundation()
            elif choice == "4":
                self.logic.undo_last_move()
            elif choice == "5":
                restart = input('Czy planujesz zagrać ponownie? (Tak/Nie): ')
                if restart == "Nie":
                    print("Dziękuję za grę!")
                    break
                else:
                    self.logic.reset_game()
            elif choice == '6':
                print('\n')
                self.show_rules()
            elif choice == "7":
                display_scores()
            if save_file_exist:
                if choice == '8':
                    self.logic.load_game(save_file)

    @staticmethod
    def show_rules():
        try:
            with open('./data/rules.txt', 'r', encoding='utf-8') as file:
                print(file.read())
        except FileNotFoundError:
            print(
                "Zasady gry: W tej grze musisz uporządkować wszystkie karty na stosach końcowych. Użyj kart z rezerwy i strefy gry.")
        except UnicodeDecodeError:
            if __debug:
                print("\033[93mBłąd dekodowania pliku. Upewnij się, że plik jest zapisany w formacie UTF-8.\033[39m")
            else:
                print(
                    "Zasady gry: W tej grze musisz uporządkować wszystkie karty na stosach końcowych. Użyj kart z rezerwy i strefy gry.")

    def _handle_move_card(self):
        src = input("Wybierz źródło (K: Kolumna, R: Rezerwa): ")
        try:
            tgt_index = int(input("Podaj numer kolumny docelowej (1-7): ")) - 1
            if 0 <= tgt_index < 7:
                tgt = self.logic.get_columns()[tgt_index]
                if src == "K":
                    src_index = int(input("Podaj numer kolumny źródłowej (1-7): ")) - 1
                    if 0 <= src_index < 7:
                        self.logic.move_card(self.logic.get_columns()[src_index], tgt)
                elif src == "R":
                    self.logic.move_card_from_waste(tgt)
        except ValueError:
            handle_error(ErrorCode.INVALID_INPUT)

    def _handle_move_to_foundation(self):
        src = input("Wybierz źródło (K: Kolumna, R: Rezerwa): ")
        try:
            index = int(input("Podaj numer stosu końcowego (1-4): ")) - 1
            if 0 <= index < 4:
                if src == "K":
                    col = int(input("Numer kolumny (1-7): ")) - 1
                    self.logic.move_card_to_foundation(self.logic.get_columns()[col], index)
                elif src == "R":
                    self.logic.move_card_to_foundation(self.logic.get_waste(), index)
        except ValueError:
            handle_error(ErrorCode.INVALID_INPUT)


if __name__ == "__main__":
    if not __debug:

        znaki = ("\033[91m(♥)\033[39m", "\033[91m(♦)\033[39m", "\033[39m(♠)\033[39m", "\033[39m(♣)\033[39m")

        os.system('cls')
        for _ in range(5):
            losowanie_znaku = znaki[random.randint(0, len(znaki) - 1)]
            print(f"{losowanie_znaku} Startuję grę\033[39m.\033[91m.\033[39m.")
            sleep(0.5)
            os.system('cls')

            losowanie_znaku = znaki[random.randint(0, len(znaki) - 1)]
            print(f"{losowanie_znaku} Startuję grę\033[91m.\033[m.\033[91m.\033[39m")
            sleep(0.5)
            os.system('cls')
    try:
        GameController().run()
    except KeyboardInterrupt:
        print("\nGra została przerwana. Dziękuję za grę!")
