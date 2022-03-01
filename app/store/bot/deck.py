import random


class Deck:
    def __init__(self):
        self.deck = self.generate_deck()
        self.shuffle_deck()

    def generate_deck(self) -> list:
        deck = []
        cards = ["⟦6⟧ -> 6⃣", "⟦7⟧ -> 7⃣", "⟦8⟧ -> 8⃣", "⟦9⟧ -> 9⃣",
                 "⟦10⟧->🔟", "⟦B⟧ -> 🔟", "⟦D⟧ -> 🔟", "⟦K⟧ -> 🔟", "⟦T⟧ -> 🔟"]
        card_suit = "♠♣♥♦"
        for symbol in card_suit:
            for card in cards:
                deck.append(card[:3] + symbol + card)
        return deck

    def shuffle_deck(self):
        random.shuffle(self.deck)

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

        