# -*- coding: utf-8 -*-
from config import *
from models import Deck, Column, CardStack, Card
from utils import *


# Klasa obsługująca logikę gry
class GameLogic:
    def __init__(self):
        self.__deck = Deck()
        self.__columns = [Column() for _ in range(7)]
        self.__foundation = [CardStack() for _ in range(4)]
        self.__waste = CardStack()
        self.__history = []
        self.__turn = 0
        self.__difficulty = "Łatwy"

    def setup_board(self):
        for i in range(7):
            for j in range(i + 1):
                card = self.__deck.remove_card()
                if j == i:
                    card.reveal()
                self.__columns[i].add_card(card)

    def reset_game(self):
        self.__init__()
        self.setup_board()

    def get_turn(self):
        return self.__turn

    def get_difficulty(self):
        return self.__difficulty

    def set_difficulty(self, mode):
        self.__difficulty = mode

    def next_turn(self):
        self.__turn += 1

    def get_columns(self):
        return self.__columns[:]

    def get_column(self, index):
        return self.__columns[index]

    def get_waste(self):
        return self.__waste

    def get_foundation(self):
        return self.__foundation[:]

    def set_turn(self, turn):
        self.__turn = turn

    def set_columns(self, columns):
        self.__columns = columns

    def set_waste(self, waste):
        self.__waste = waste

    def set_foundation(self, foundation):
        self.__foundation = foundation

    def move_card_to_foundation(self, source, foundation_index):
        foundation = self.__foundation[foundation_index]
        card = source.remove_card()
        if card and self.can_move_to_foundation(card, foundation):
            foundation.add_card(card)
            was_hidden = source.top_card().is_hidden() if isinstance(source, Column) else False
            self.__history.append((source, foundation, card, was_hidden))
            if isinstance(source, Column):
                source.reveal_top_card()
        else:
            handle_error(ErrorCode.INVALID_MOVE)
            if card:
                source.add_card(card)

    @staticmethod
    def can_move(card, target):
        if target.is_empty():
            return card.get_value() == "K"
        top = target.top_card()
        return card_value(card.get_value()) == card_value(top.get_value()) - 1 and \
            (card.get_suit() in ['\u2665', '\u2666']) != (top.get_suit() in ['\u2665', '\u2666'])

    @staticmethod
    def can_move_to_foundation(card, foundation):
        if foundation.is_empty():
            return card.get_value() == "A"
        top = foundation.top_card()
        return card_value(card.get_value()) == card_value(top.get_value()) + 1 and card.get_suit() == top.get_suit()

    def check_win(self):
        if all(len(stack.get_cards()) == 13 for stack in self.__foundation):
            print("Gratulacje! Ułożyłeś pasjansa w ", self.get_turn(), " na poziomie ", self.get_columns(),
                  "! Twój wynik został zapisany do rankingu.")
            save_score(self.__turn)
            return True
        return False

    def move_card(self, source, target):
        card = source.top_card()
        if not card:
            handle_error(ErrorCode.EMPTY_COLUMN)
            return
        if self.can_move(card, target):
            was_hidden = card.is_hidden()
            target.add_card(source.remove_card())
            if isinstance(source, Column):
                source.reveal_top_card()
            self.__history.append((source, target, card, was_hidden))
        else:
            handle_error(ErrorCode.INVALID_MOVE)

    def undo_last_move(self):
        if not self.__history:
            print("\033[93mBrak ruchów do cofnięcia.\033[39m")
            return
        try:
            source, target, card, was_hidden = self.__history.pop()
            if target:
                target.remove_card()
            source.add_card(card)
            if was_hidden and isinstance(source, Column):
                source.top_card()._Card__hidden = True
        except ValueError:
            print("\033[93mNieprawidłowy zapis w historii ruchów. Cofanie nieudane.\033[39m")

    def draw_from_waste(self):
        if self.__deck.is_empty():
            if self.__waste.is_empty():
                handle_error(ErrorCode.EMPTY_WASTE)
                return
            self.__deck.refill(self.__waste.get_cards())
            self.__waste = CardStack()
        drawn = []
        n = 1 if self.__difficulty == "Łatwy" else 3
        for _ in range(n):
            card = self.__deck.remove_card()
            if card:
                drawn.append(card)
        if self.__difficulty == "Łatwy":
            if drawn:
                card = drawn[0]
                card.reveal()
                self.__waste = CardStack()
                self.__waste.add_card(card)
        elif self.__difficulty == "Trudny":
            new_waste = CardStack()
            for card in drawn[:-1]:
                new_waste.add_card(card)
            if drawn:
                drawn[-1].reveal()
                new_waste.add_card(drawn[-1])
            self.__waste = new_waste

    def move_card_from_waste(self, target):
        card = self.__waste.top_card()
        if not card:
            handle_error(ErrorCode.EMPTY_WASTE)
            return
        if self.can_move(card, target):
            target.add_card(self.__waste.remove_card())
            self.__history.append((self.__waste, target, card, False))
        else:
            handle_error(ErrorCode.INVALID_MOVE)

    def save_game(self, file):
        game_data = {
            "turn": self.get_turn(),
            "difficulty": self.get_difficulty(),
            "columns": [col.to_dict() for col in self.get_columns()],
            "waste": self.get_waste().to_dict(),
            "foundation": [stack.to_dict() for stack in self.get_foundation()]
        }

        json_string = json.dumps(game_data, ensure_ascii=False, indent=2)
        key = load_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(json_string.encode("utf-8"))

        with open(file, "wb") as f:
            f.write(encrypted)

    def load_game(self, file):
        try:
            decrypted_json = decrypt_file(file)
            game_data = json.loads(decrypted_json)

            def deserialize_column(data):
                column = Column()
                for card_data in data:
                    card = Card.from_dict(card_data)
                    column.add_card(card)
                return column

            def deserialize_stack(data):
                stack = CardStack()
                for card_data in data:
                    card = Card.from_dict(card_data)
                    stack.add_card(card)
                return stack

            self.set_turn(game_data["turn"])
            self.set_difficulty(game_data["difficulty"])
            self.set_columns([deserialize_column(col) for col in game_data["columns"]])
            self.set_waste(deserialize_stack(game_data["waste"]))
            self.set_foundation([deserialize_stack(stack) for stack in game_data["foundation"]])

        except Exception as e:
            print(f"\033[93mBłąd ładowania gry: {e}\033[39m")
