# scoreboard_app/gui/emptygoal_panel.py

import tkinter as tk
from tkinter import ttk

from scoreboard_app.controllers.scoreboard_controller import ScoreboardController


class EmptyGoalPanel(tk.LabelFrame):
    """
    GUI control panel for triggering empty-net state or cancelling it.

    It talks to the ScoreboardController, which updates
    scoreboard fields and graphics via VMixClient.
    """

    def __init__(self, master: tk.Misc, controller: ScoreboardController):
        super().__init__(master, text="TOM MÅLVAKT")
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # HOME EMPTY NET
        ttk.Button(
            self,
            text="H – TOM MÅL",
            command=self.empty_home
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ttk.Button(
            self,
            text="H – AVBRYT",
            command=self.cancel_home
        ).grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # AWAY EMPTY NET
        ttk.Button(
            self,
            text="A – TOM MÅL",
            command=self.empty_away
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Button(
            self,
            text="A – AVBRYT",
            command=self.cancel_away
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    # -------------------------------------------------------

    def empty_home(self):
        """Trigger empty net for HOME team."""
        try:
            self.controller.set_empty_goal("home", enabled=True)
        except Exception as e:
            print(f"[EmptyGoalPanel] Error: {e}")

    def cancel_home(self):
        """Cancel empty net for HOME team."""
        try:
            self.controller.set_empty_goal("home", enabled=False)
        except Exception as e:
            print(f"[EmptyGoalPanel] Error: {e}")

    def empty_away(self):
        """Trigger empty net for AWAY team."""
        try:
            self.controller.set_empty_goal("away", enabled=True)
        except Exception as e:
            print(f"[EmptyGoalPanel] Error: {e}")

    def cancel_away(self):
        """Cancel empty net for AWAY team."""
        try:
            self.controller.set_empty_goal("away", enabled=False)
        except Exception as e:
            print(f"[EmptyGoalPanel] Error: {e}")
