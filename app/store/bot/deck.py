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

class Deck:
    def __init__(self):
        self.deck = []

    def generate_deck(self):
        k = 2
        for i in CardName:
            for j in Suit:
                self.deck.append(Card(j, i, k))
            if i not in [CardName.TEN, CardName.JACK, CardName.LADY]:
                k += 1

    def shuffle_deck(self):
        random.shuffle(self.deck)

# will be deprecated

"""
    def get_card_value(self, card: str) -> int:
        return self.card_values[card]

    @property
    def card_values(self):
        return {"⟦6⟧♠⟦6⟧ -> 6⃣": 6,
                "⟦7⟧♠⟦7⟧ -> 7⃣": 7,
                "⟦8⟧♠⟦8⟧ -> 8⃣": 8,
                "⟦9⟧♠⟦9⟧ -> 9⃣": 9,
                "⟦10♠⟦10⟧->🔟": 10,
                "⟦B⟧♠⟦B⟧ -> 🔟": 10,
                "⟦D⟧♠⟦D⟧ -> 🔟": 10,
                "⟦K⟧♠⟦K⟧ -> 🔟": 10,
                "⟦T⟧♠⟦T⟧ -> 🔟": 10,
                "⟦6⟧♣⟦6⟧ -> 6⃣": 6,
                "⟦7⟧♣⟦7⟧ -> 7⃣": 7,
                "⟦8⟧♣⟦8⟧ -> 8⃣": 8,
                "⟦9⟧♣⟦9⟧ -> 9⃣": 9,
                "⟦10♣⟦10⟧->🔟": 10,
                "⟦B⟧♣⟦B⟧ -> 🔟": 10,
                "⟦D⟧♣⟦D⟧ -> 🔟": 10,
                "⟦K⟧♣⟦K⟧ -> 🔟": 10,
                "⟦T⟧♣⟦T⟧ -> 🔟": 10,
                "⟦6⟧♥⟦6⟧ -> 6⃣": 6,
                "⟦7⟧♥⟦7⟧ -> 7⃣": 7,
                "⟦8⟧♥⟦8⟧ -> 8⃣": 8,
                "⟦9⟧♥⟦9⟧ -> 9⃣": 9,
                "⟦10♥⟦10⟧->🔟": 10,
                "⟦B⟧♥⟦B⟧ -> 🔟": 10,
                "⟦D⟧♥⟦D⟧ -> 🔟": 10,
                "⟦K⟧♥⟦K⟧ -> 🔟": 10,
                "⟦T⟧♥⟦T⟧ -> 🔟": 10,
                "⟦6⟧♦⟦6⟧ -> 6⃣": 6,
                "⟦7⟧♦⟦7⟧ -> 7⃣": 7,
                "⟦8⟧♦⟦8⟧ -> 8⃣": 8,
                "⟦9⟧♦⟦9⟧ -> 9⃣": 9,
                "⟦10♦⟦10⟧->🔟": 10,
                "⟦B⟧♦⟦B⟧ -> 🔟": 10,
                "⟦D⟧♦⟦D⟧ -> 🔟": 10,
                "⟦K⟧♦⟦K⟧ -> 🔟": 10,
                "⟦T⟧♦⟦T⟧ -> 🔟": 10,
                }  
"""
        