import tkinter as tk
from tkinter import ttk


class ScoreboardPanel(tk.Frame):
    """
    Shows current score, shots, period and provides manual buttons if needed.
    Very simple placeholder until auto update is integrated.
    """

    def __init__(self, master, controller):
        super().__init__(master, borderwidth=2, relief="groove")

        self.controller = controller

        tk.Label(self, text="SCOREBOARD", font=("Segoe UI", 14, "bold")).pack(pady=5)

        # HOME SCORE
        row = tk.Frame(self)
        row.pack(fill="x", pady=2)
        tk.Label(row, text="Home Score").pack(side="left")
        self.home_score = tk.Entry(row, width=4)
        self.home_score.pack(side="right")

        # AWAY SCORE
        row = tk.Frame(self)
        row.pack(fill="x", pady=2)
        tk.Label(row, text="Away Score").pack(side="left")
        self.away_score = tk.Entry(row, width=4)
        self.away_score.pack(side="right")

        # PERIOD
        row = tk.Frame(self)
        row.pack(fill="x", pady=2)
        tk.Label(row, text="Period").pack(side="left")
        self.period = tk.Entry(row, width=4)
        self.period.pack(side="right")

        # SHOTS
        row = tk.Frame(self)
        row.pack(fill="x", pady=2)
        tk.Label(row, text="Shots Home").pack(side="left")
        self.shots_home = tk.Entry(row, width=4)
        self.shots_home.pack(side="right")

        row = tk.Frame(self)
        row.pack(fill="x", pady=2)
        tk.Label(row, text="Shots Away").pack(side="left")
        self.shots_away = tk.Entry(row, width=4)
        self.shots_away.pack(side="right")

        ttk.Button(self, text="UPDATE", command=self._apply).pack(pady=10)

    def _apply(self):
        try:
            h = int(self.home_score.get())
            a = int(self.away_score.get())
            p = self.period.get()
            sh = int(self.shots_home.get())
            sa = int(self.shots_away.get())

            self.controller.update_score(
                home=h,
                away=a,
                shots_home=sh,
                shots_away=sa,
                period=p
            )
        except Exception as e:
            print("ScoreboardPanel error:", e)
