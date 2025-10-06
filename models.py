# -*- coding: utf-8 -*-
from config import *
import random


# Klasa reprezentująca pojedynczą kartę
class Card:
    def __init__(self, value, suit, hidden=True):
        self.__value = value
        self.__suit = suit
        self.__hidden = hidden

    def __str__(self):
        if self.__hidden:
            return "\033[38;2;0;0;0m[Zakryte]"
        color = '\033[31m\033[47m' if self.__suit in ['\u2665', '\u2666'] else '\033[47m\033[38;2;0;0;39m'
        return f"{color}{self.__value}{self.__suit}\033[39m\033[42m"

    def reveal(self):
        self.__hidden = False

    def is_hidden(self):
        return self.__hidden

    def get_value(self):
        return self.__value

    def get_suit(self):
        return self.__suit

    def to_dict(self):
        return {
            "value": self.get_value(),
            "suit": self.get_suit(),
            "hidden": self.is_hidden()
        }

    @staticmethod
    def from_dict(data):
        card = Card(data["value"], data["suit"], data.get("hidden", True))
        return card


# Klasa reprezentująca stos kart
class CardStack:
    def __init__(self):
        self._cards = []

    def add_card(self, card):
        self._cards.append(card)

    def remove_card(self):
        return self._cards.pop() if self._cards else None

    def top_card(self):
        return self._cards[-1] if self._cards else None

    def get_cards(self):
        return self._cards[:]

    def is_empty(self):
        return not self._cards

    def to_dict(self):
        return [card.to_dict() for card in self.get_cards()]


# Klasa reprezentująca kolumnę kart na planszy
class Column(CardStack):
    def reveal_top_card(self):
        if self._cards and self._cards[-1].is_hidden():
            self._cards[-1].reveal()


# Klasa reprezentująca talię kart
class Deck(CardStack):
    def __init__(self):
        super().__init__()
        suits = ['\u2665', '\u2666', '\u2660', '\u2663']
        values = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']
        self._cards = [Card(value, suit) for suit in suits for value in values]
        random.shuffle(self._cards)

    def reshuffle(self):
        random.shuffle(self._cards)

    def refill(self, cards):
        unique_cards = set(cards)
        if len(unique_cards) != len(cards):
            raise ValueError("\n\033[92mTalia zawiera powtarzające się karty!\n\033[39m")
        self._cards = list(unique_cards)
        self.reshuffle()
