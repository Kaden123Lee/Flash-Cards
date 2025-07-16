import random
from flashcard_models import Flashcard, CardSetManager, ReviewLogger

class FlashcardCLI:
    def __init__(self):
        self.manager = CardSetManager()
        self.logger = ReviewLogger()

    def run(self):
        while True:
            print("\nFlashcard CLI")
            print("1. Add Card")
            print("2. Study")
            print("3. Quit")
            choice = input("Choose an option: ")
            if choice == "1":
                self.add_card()
            elif choice == "2":
                self.study()
            elif choice == "3":
                break
            else:
                print("Invalid option.")

    def add_card(self):
        front = input("Enter front: ")
        back = input("Enter back: ")
        topic = input("Enter topic (default 'General'): ") or "General"
        self.manager.add_card(front, back, topic)
        print("Card added!")

    def study(self):
        cards = self.manager.get_leitner_cards()
        if not cards:
            print("No cards to study.")
            return
        random.shuffle(cards)
        for card in cards:
            print(f"\nFront: {card.front}")
            input("Press Enter to see back...")
            print(f"Back: {card.back}")
            score = int(input("Rate your recall (1-5): "))
            self.logger.log_review(card.id, score)
            self.logger.adjust_card_box(card, score)
            self.manager.save_cards()

if __name__ == "__main__":
    app = FlashcardCLI()
    app.run()