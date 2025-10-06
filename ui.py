# -*- coding: utf-8 -*-
from logic import GameLogic
from utils import strip_ansi


class GameUI:
    def __init__(self, logic: GameLogic):
        self.logic = logic

    def display_board(self):
        terminal_width = 80
        terminal_height = 15

        board_width = terminal_width
        board_height = terminal_height

        print("\033[0m")
        print("\033[42m" + " " * board_width + "\033[0m")

        rows = []

        rows.append("\033[38;2;0;0;0mPlansza gry:")
        for i, col in enumerate(self.logic.get_columns()):
            cards = " ".join(str(c) for c in col.get_cards())
            rows.append(f"\033[38;2;0;0;0mKolumna {i + 1}: {cards}")

        rows.append("\033[38;2;0;0;0mStos rezerwowy: " + " ".join(
            strip_ansi(str(card)) for card in self.logic.get_waste().get_cards()))
        rows.append("\033[38;2;0;0;0mStosy końcowe:")

        for i, stack in enumerate(self.logic.get_foundation()):
            foundation_cards = " ".join(strip_ansi(str(card)) for card in stack.get_cards()) or "[pusty]"
            rows.append(f"\033[38;2;0;0;0mStos {i + 1}: {foundation_cards}\033[42m")

        while len(rows) < board_height - 2:
            rows.append("")

        for row in rows:
            print("\033[42m  " + row.ljust(board_width - 4) + "  \033[0m")

        print("\033[42m" + " " * board_width + "\033[0m")
