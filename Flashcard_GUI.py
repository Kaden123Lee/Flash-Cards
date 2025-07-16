import tkinter as tk
from tkinter import ttk, messagebox
import random
from flashcard_models import Flashcard, CardSetManager, ReviewLogger

class FlashcardApp(tk.Tk):
    def __init__(self, manager: CardSetManager, logger: ReviewLogger):
        super().__init__()
        self.title("Flashcard App")
        self.geometry("600x400")
        self.manager = manager
        self.logger = logger
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self.add_page = AddCardPage(self.notebook, self.manager)
        self.view_page = ViewCardsPage(self.notebook, self.manager)
        self.study_page = StudyPage(self.notebook, self.manager, self.logger)
        self.quiz_page = QuizPage(self.notebook, self.manager, self.logger)
        self.notebook.add(self.add_page, text="Add Card")
        self.notebook.add(self.view_page, text="View Cards")
        self.notebook.add(self.study_page, text="Study")
        self.notebook.add(self.quiz_page, text="Quiz")

class AddCardPage(tk.Frame):
    def __init__(self, parent, manager: CardSetManager):
        super().__init__(parent)
        self.manager = manager
        tk.Label(self, text="Front:").pack()
        self.front_entry = tk.Entry(self)
        self.front_entry.pack()
        tk.Label(self, text="Back:").pack()
        self.back_entry = tk.Entry(self)
        self.back_entry.pack()
        tk.Label(self, text="Topic:").pack()
        self.topic_entry = tk.Entry(self)
        self.topic_entry.pack()
        tk.Button(self, text="Add", command=self.add_card).pack()

    def add_card(self):
        front = self.front_entry.get()
        back = self.back_entry.get()
        topic = self.topic_entry.get() or "General"
        if front and back:
            self.manager.add_card(front, back, topic)
            messagebox.showinfo("Success", "Card added!")
            self.front_entry.delete(0, tk.END)
            self.back_entry.delete(0, tk.END)
            self.topic_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Front and back are required.")

class ViewCardsPage(tk.Frame):
    def __init__(self, parent, manager: CardSetManager):
        super().__init__(parent)
        self.manager = manager
        self.tree = ttk.Treeview(self, columns=("Front", "Back", "Box"), show="headings")
        self.tree.heading("Front", text="Front")
        self.tree.heading("Back", text="Back")
        self.tree.heading("Box", text="Box")
        self.tree.pack(fill="both", expand=True)
        tk.Button(self, text="Refresh", command=self.refresh).pack()
        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for card in self.manager.cards:
            self.tree.insert("", tk.END, values=(card.front, card.back, card.box))

class StudyPage(tk.Frame):
    def __init__(self, parent, manager: CardSetManager, logger: ReviewLogger):
        super().__init__(parent)
        self.manager = manager
        self.logger = logger
        self.cards = self.manager.get_leitner_cards()
        self.current_card = None
        self.label = tk.Label(self, text="Press 'Next' to start")
        self.label.pack()
        self.back_label = tk.Label(self, text="")
        self.back_label.pack()
        tk.Button(self, text="Next", command=self.next_card).pack()
        tk.Button(self, text="Show Back", command=self.show_back).pack()
        self.score_var = tk.IntVar()
        tk.Label(self, text="Score (1-5):").pack()
        tk.Entry(self, textvariable=self.score_var).pack()
        tk.Button(self, text="Submit", command=self.submit_score).pack()

    def next_card(self):
        if not self.cards:
            self.label.config(text="No cards to study.")
            return
        self.current_card = random.choice(self.cards)
        self.cards.remove(self.current_card)
        self.label.config(text=f"Front: {self.current_card.front}")
        self.back_label.config(text="")
        self.score_var.set(0)

    def show_back(self):
        if self.current_card:
            self.back_label.config(text=f"Back: {self.current_card.back}")

    def submit_score(self):
        if self.current_card:
            score = self.score_var.get()
            if 1 <= score <= 5:
                self.logger.log_review(self.current_card.id, score)
                self.logger.adjust_card_box(self.current_card, score)
                self.manager.save_cards()
                self.next_card()
            else:
                messagebox.showerror("Error", "Score must be between 1 and 5.")

class QuizPage(StudyPage):
    def __init__(self, parent, manager: CardSetManager, logger: ReviewLogger):
        super().__init__(parent, manager, logger)
        self.correct = 0
        self.total = 0
        self.label.config(text="Press 'Next' to start quiz")

    def submit_score(self):
        if self.current_card:
            score = self.score_var.get()
            if 1 <= score <= 5:
                self.total += 1
                if score >= 3:
                    self.correct += 1
                self.logger.log_review(self.current_card.id, score)
                self.logger.adjust_card_box(self.current_card, score)
                self.manager.save_cards()
                self.label.config(text=f"Score: {self.correct}/{self.total}")
                self.next_card()
            else:
                messagebox.showerror("Error", "Score must be between 1 and 5.")

if __name__ == "__main__":
    manager = CardSetManager()
    logger = ReviewLogger()
    app = FlashcardApp(manager, logger)
    app.mainloop()