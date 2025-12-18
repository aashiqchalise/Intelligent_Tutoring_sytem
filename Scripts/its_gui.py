import tkinter as tk
from tkinter import ttk, messagebox
from owlready2 import get_ontology
import os

class ModernITS:
    def __init__(self, root, onto):
        self.APP_BG = "#f0fdf4"
        self.root = root
        self.onto = onto
        self.root.title("ITS – Area of Shapes (Modern)")
        self.root.geometry("920x560")
        self.root.minsize(860, 520)
        self.root.configure(bg=self.APP_BG)

        self._center_window()

        # ---- Style ----

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("Main.TFrame", background=self.APP_BG)
        self.style.configure("Card.TFrame", background="white", relief="ridge", borderwidth=1)
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), background=self.APP_BG)
        self.style.configure("Sub.TLabel", font=("Segoe UI", 10), background=self.APP_BG, foreground="#555")
        self.style.configure("Q.TLabel", font=("Segoe UI", 12), background="white", wraplength=820, justify="left")
        self.style.configure("Meta.TLabel", font=("Segoe UI", 10), background="white", foreground="#666")
        self.style.configure("Score.TLabel", font=("Segoe UI", 11, "bold"), background=self.APP_BG, foreground="#1d5c2f")
        self.style.configure("TButton", font=("Segoe UI", 11))
        self.style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))
        self.style.configure("TCombobox", font=("Segoe UI", 11))
        self.style.configure("TEntry", font=("Segoe UI", 11))

        # ---- Load individuals ----
        self.shapes = list(getattr(self.onto, "Shape").instances()) if hasattr(self.onto, "Shape") else []
        self.levels = list(getattr(self.onto, "SkillLevel").instances()) if hasattr(self.onto, "SkillLevel") else []
        self.questions_all = list(getattr(self.onto, "Question").instances()) if hasattr(self.onto, "Question") else []

        if not self.questions_all:
            messagebox.showerror("Ontology error", "No Question individuals found.")
            root.destroy()
            return

        self.shape_map = {self.get_data(s, "hasName", s.name): s for s in self.shapes}
        self.level_map = {self.get_data(l, "hasName", l.name): l for l in self.levels}

        # ---- Quiz state ----
        self.filtered_questions = []
        self.current_index = 0
        self.score = 0
        self.correct_questions = set()
        self.attempts = {}  # question -> attempt count

        # ---- Build UI ----
        self.build_ui()
        self.apply_filters()  # initial load

    # ---------------- UI helpers ----------------
    def _center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = int((sw - w) / 2), int((sh - h) / 2.6)
        self.root.geometry(f"+{x}+{y}")

    def build_ui(self):
        main = ttk.Frame(self.root, style="Main.TFrame", padding=18)
        main.pack(fill="both", expand=True)

        # Header
        header = ttk.Frame(main, style="Main.TFrame")
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(header, text="Intelligent Tutoring System", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Area of Shapes (Rectangle, Circle, Triangle, Square)", style="Sub.TLabel").pack(anchor="w")

        # Filters row (Shape + Level)
        filters = ttk.Frame(main, style="Main.TFrame")
        filters.pack(fill="x", pady=(6, 12))

        ttk.Label(filters, text="Shape:", background=self.APP_BG, font=("Segoe UI", 11)).pack(side="left")
        self.shape_var = tk.StringVar(value=(sorted(self.shape_map.keys())[1] if self.shape_map else ""))
        self.shape_combo = ttk.Combobox(filters, state="readonly", width=18,
                                        values=sorted(self.shape_map.keys()), textvariable=self.shape_var)
        self.shape_combo.pack(side="left", padx=(8, 18))
        self.shape_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(filters, text="Skill Level:", background=self.APP_BG, font=("Segoe UI", 11)).pack(side="left")
        self.level_var = tk.StringVar(value=(sorted(self.level_map.keys())[1] if self.level_map else ""))
        self.level_combo = ttk.Combobox(filters, state="readonly", width=18,
                                        values=sorted(self.level_map.keys()), textvariable=self.level_var)
        self.level_combo.pack(side="left", padx=(8, 18))
        self.level_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Button(filters, text="Reload Questions", command=self.apply_filters).pack(side="right")

        # Question card
        self.q_card = ttk.Frame(main, style="Card.TFrame", padding=16)
        self.q_card.pack(fill="x")

        self.q_top = ttk.Frame(self.q_card, style="Card.TFrame")
        self.q_top.pack(fill="x")

        self.q_counter_label = ttk.Label(self.q_top, text="", style="Meta.TLabel")
        self.q_counter_label.pack(side="left")

        self.attempt_label = ttk.Label(self.q_top, text="", style="Meta.TLabel")
        self.attempt_label.pack(side="right")

        self.q_text_label = ttk.Label(self.q_card, text="", style="Q.TLabel")
        self.q_text_label.pack(anchor="w", pady=(10, 0))

        # Progress bar
        self.progress = ttk.Progressbar(main, mode="determinate")
        self.progress.pack(fill="x", pady=(12, 0))

        # Answer row
        ans = ttk.Frame(main, style="Main.TFrame")
        ans.pack(fill="x", pady=(12, 6))

        ttk.Label(ans, text="Your answer:", background=self.APP_BG, font=("Segoe UI", 11)).pack(side="left")
        self.answer_var = tk.StringVar()
        self.answer_entry = ttk.Entry(ans, width=20, textvariable=self.answer_var)
        self.answer_entry.pack(side="left", padx=(10, 0))

        # Buttons row
        btns = ttk.Frame(main, style="Main.TFrame")
        btns.pack(fill="x", pady=(6, 6))

        ttk.Button(btns, text="Check Answer", style="Accent.TButton", command=self.check_answer).pack(side="left", padx=(0, 10))
        ttk.Button(btns, text="Hint", command=self.show_hint).pack(side="left", padx=(0, 10))
        ttk.Button(btns, text="Show Formula", command=self.show_formula).pack(side="left", padx=(0, 10))
        ttk.Button(btns, text="Next ▶", command=self.next_question).pack(side="left", padx=(0, 10))

        ttk.Button(btns, text="Submit Quiz", command=self.submit_quiz).pack(side="right")

        # Feedback card
        fb = ttk.Frame(main, style="Card.TFrame", padding=12)
        fb.pack(fill="x", pady=(10, 0))

        self.feedback_label = tk.Label(
            fb, text="", bg=self.APP_BG, fg="#333",
            font=("Segoe UI", 11), justify="left", wraplength=820
        )
        self.feedback_label.pack(anchor="w")

        # Status
        status = ttk.Frame(main, style="Main.TFrame")
        status.pack(fill="x", pady=(10, 0))

        self.score_label = ttk.Label(status, text="Score: 0", style="Score.TLabel")
        self.score_label.pack(side="right")

    # ---------------- Ontology helper methods ----------------
    def get_data(self, indiv, prop, default=""):
        if not hasattr(self.onto, prop):
            return default
        p = getattr(self.onto, prop)
        vals = getattr(indiv, p.python_name, [])
        return str(vals[0]) if vals else default

    def get_targets(self, indiv, prop):
        if not hasattr(self.onto, prop):
            return []
        p = getattr(self.onto, prop)
        return list(getattr(indiv, p.python_name, []))

    # ---------------- Quiz logic ----------------
    def apply_filters(self):
        # reset
        self.current_index = 0
        self.score = 0
        self.correct_questions.clear()
        self.attempts.clear()
        self.score_label.config(text="Score: 0")
        self.feedback_label.config(text="", fg="#333")

        # selected individuals
        shape_name = self.shape_var.get()
        level_name = self.level_var.get()

        shape_ind = self.shape_map.get(shape_name)
        level_ind = self.level_map.get(level_name)

        # filter questions: must match BOTH shape + level
        self.filtered_questions = []
        for q in self.questions_all:
            if shape_ind and shape_ind not in self.get_targets(q, "hasShape"):
                continue
            if level_ind and level_ind not in self.get_targets(q, "hasSkillLevel"):
                continue
            self.filtered_questions.append(q)

        if not self.filtered_questions:
            self.q_text_label.config(text="No questions found for this Shape + Skill Level.")
            self.q_counter_label.config(text="")
            self.attempt_label.config(text="")
            self.progress["value"] = 0
            return

        # init attempts = 0 for each q
        for q in self.filtered_questions:
            self.attempts[q] = 0

        self.show_question()

    def show_question(self):
        q = self.filtered_questions[self.current_index]
        qtext = self.get_data(q, "hasText", "(No question text)")
        total = len(self.filtered_questions)

        self.q_counter_label.config(text=f"Question {self.current_index + 1} of {total}")
        self.q_text_label.config(text=qtext)

        # attempts display
        self.attempt_label.config(text=f"Attempts: {self.attempts.get(q, 0)}")

        # progress bar
        self.progress["maximum"] = total
        self.progress["value"] = self.current_index + 1

        # reset input
        self.answer_var.set("")
        self.answer_entry.focus()

    def check_answer(self):
        q = self.filtered_questions[self.current_index]
        correct = self.get_data(q, "hasCorrectAnswer", "")

        # update attempt count
        self.attempts[q] = self.attempts.get(q, 0) + 1
        self.attempt_label.config(text=f"Attempts: {self.attempts[q]}")

        user = self.answer_var.get().strip()

        if not correct:
            self.feedback_label.config(text="No correct answer stored for this question.", fg="#b00020")
            return

        # compare numeric if possible
        is_correct = False
        try:
            is_correct = float(user) == float(correct.strip('"'))
        except Exception:
            is_correct = user.lower() == correct.lower()

        if is_correct:
            if q not in self.correct_questions:
                self.correct_questions.add(q)
                self.score += 1
                self.score_label.config(text=f"Score: {self.score}")

            self.feedback_label.config(text="Correct! Great job.", fg="#1b5e20")
        else:
            self.feedback_label.config(text="Incorrect. Click Hint or Formula and try again.", fg="#b00020")

    def show_hint(self):
        q = self.filtered_questions[self.current_index]
        hints = self.get_targets(q, "hasHint")
        if not hints:
            self.feedback_label.config(text="No hint available for this question.", fg="#444")
            return
        hint_text = self.get_data(hints[0], "hasText", "(Hint has no text)")
        self.feedback_label.config(text=f"Hint: {hint_text}", fg="#0d47a1")

    def show_formula(self):
        q = self.filtered_questions[self.current_index]
        formulas = self.get_targets(q, "usesFormula")
        if not formulas:
            self.feedback_label.config(text="No formula linked to this question.", fg="#444")
            return
        ftext = self.get_data(formulas[0], "hasText", "(Formula has no text)")
        self.feedback_label.config(text=f"Formula: {ftext}", fg="#6a1b9a")

    def next_question(self):
        if not self.filtered_questions:
            return
        self.feedback_label.config(text="", fg="#333")
        self.current_index = (self.current_index + 1) % len(self.filtered_questions)
        self.show_question()

    def submit_quiz(self):
        total = len(self.filtered_questions)
        if total == 0:
            messagebox.showinfo("Submit", "No questions to submit.")
            return

        score = self.score
        percent = (score / total) * 100

        # performance feedback
        if percent >= 80:
            level = "Excellent"
            msg = "Outstanding work! You have strong understanding of area formulas."
        elif percent >= 50:
            level = "Good"
            msg = "Good effort! Practice a little more to improve accuracy."
        else:
            level = "Needs Improvement"
            msg = "Keep practicing. Use hints and formulas to learn step-by-step."

        # attempts stats
        total_attempts = sum(self.attempts.values())
        avg_attempts = total_attempts / total if total else 0

        summary = (
            f"Quiz Submitted \n\n"
            f"Score: {score}/{total} ({percent:.1f}%)\n"
            f"Performance: {level}\n"
            f"Total Attempts: {total_attempts}\n"
            f"Average Attempts per Question: {avg_attempts:.2f}\n\n"
            f"{msg}"
        )

        messagebox.showinfo("Final Feedback", summary)
        self.feedback_label.config(text=summary, fg="#0d47a1")


def main():
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ONTO_PATH = os.path.join(BASE_DIR, "itsformath_ontology.rdf")

    onto = get_ontology(f"file://{ONTO_PATH}").load()
    root = tk.Tk()
    ModernITS(root, onto)
    root.mainloop()


if __name__ == "__main__":
    main()

