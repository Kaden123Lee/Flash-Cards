import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

class Flashcard:
    def __init__(self, front: str, back: str, topic: str = "General", box: int = 1):
        self.id = str(uuid.uuid4())
        self.front = front
        self.back = back
        self.topic = topic
        self.box = box
        self.created_at = datetime.now().isoformat()
        self.last_reviewed = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "front": self.front,
            "back": self.back,
            "topic": self.topic,
            "box": self.box,
            "created_at": self.created_at,
            "last_reviewed": self.last_reviewed
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Flashcard':
        card = cls(data["front"], data["back"], data["topic"], data["box"])
        card.id = data["id"]
        card.created_at = data["created_at"]
        card.last_reviewed = data.get("last_reviewed")
        return card

class CardSetManager:
    def __init__(self, filename: str = "flashcards.json"):
        self.filename = filename
        self.cards: List[Flashcard] = []
        self.load_cards()

    def load_cards(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                data = json.load(f)
                self.cards = [Flashcard.from_dict(card) for card in data]
        else:
            self.cards = []

    def save_cards(self):
        with open(self.filename, "w") as f:
            json.dump([card.to_dict() for card in self.cards], f, indent=4)

    def add_card(self, front: str, back: str, topic: str = "General"):
        card = Flashcard(front, back, topic)
        self.cards.append(card)
        self.save_cards()

    def edit_card(self, card_id: str, front: Optional[str] = None, back: Optional[str] = None, topic: Optional[str] = None):
        for card in self.cards:
            if card.id == card_id:
                if front is not None:
                    card.front = front
                if back is not None:
                    card.back = back
                if topic is not None:
                    card.topic = topic
                self.save_cards()
                break

    def delete_card(self, card_id: str):
        self.cards = [card for card in self.cards if card.id != card_id]
        self.save_cards()

    def get_cards_by_topic(self, topic: str) -> List[Flashcard]:
        return [card for card in self.cards if card.topic == topic]

    def get_leitner_cards(self, max_cards: int = 10) -> List[Flashcard]:
        due_cards = sorted(self.cards, key=lambda x: x.box)
        return due_cards[:max_cards]

class ReviewLogger:
    def __init__(self, filename: str = "review_history.json"):
        self.filename = filename
        self.reviews = self.load_reviews()

    def load_reviews(self) -> List[Dict]:
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return []

    def save_reviews(self):
        with open(self.filename, "w") as f:
            json.dump(self.reviews, f, indent=4)

    def log_review(self, card_id: str, performance: int):
        review = {
            "card_id": card_id,
            "timestamp": datetime.now().isoformat(),
            "performance": performance
        }
        self.reviews.append(review)
        self.save_reviews()

    def adjust_card_box(self, card: Flashcard, performance: int):
        if performance >= 3 and card.box < 5:
            card.box += 1
        elif performance < 3 and card.box > 1:
            card.box -= 1
        card.last_reviewed = datetime.now().isoformat()