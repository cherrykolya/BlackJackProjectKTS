import random
from dataclasses import dataclass
from enum import Enum


class Suit(Enum):
    DIAMONDS = "♦"
    HEARTS = "♥"
    CLUBS = "♣"
    SPADES = "♠"


class CardName(Enum):
    TWO = "⟦2⟧"
    THREE = "⟦3⟧"
    FOUR = "⟦4⟧"
    FIVE = "⟦5⟧"
    SIX = "⟦6⟧"
    SEVEN = "⟦7⟧"
    EIGHT = "⟦8⟧"
    NINE = "⟦9⟧"
    TEN = "⟦10⟧"
    JACK = "⟦B⟧"
    LADY = "⟦D⟧"
    KING = "⟦K⟧"
    ACE = "⟦T⟧"


@dataclass
class Card:
    suit: Suit
    card_name: CardName
    value: int

    def __str__(self):
        return f"{self.card_name.value} {self.suit.value} -> {self.value}"
    
    def to_dict(self) -> dict:
        return {'suit': self.suit.value,
                'card_name': self.card_name.value,
                'value': self.value}

    @classmethod
    def from_dict(cls, card: dict) -> "Card":
        return cls(suit= Suit(card['suit']),
                   card_name=CardName(card['card_name']),
                   value=card['value'])


class Deck:
    def __init__(self):
        self.deck = []

    def generate_deck(self):
        value = 2
        for card in CardName:
            for suit in Suit:
                self.deck.append(Card(suit, card, value))
            if card not in [CardName.TEN, CardName.JACK, CardName.LADY]:
                value += 1

    def shuffle_deck(self):
        random.shuffle(self.deck)
