import tkinter as tk
from tkinter import ttk

from scoreboard_app.gui.popup_player_picker import pick_player


class GoalPanel(ttk.LabelFrame):
    """
    Goal control panel with player picker popup.
    """

    def __init__(self, app, parent):
        super().__init__(parent, text="GOAL")
        self.app = app
        self.controller = app.controller

        self.frame = ttk.Frame(self)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Buttons ---
        ttk.Button(self.frame, text="HOME GOAL", command=self._goal_home).pack(
            fill="x", pady=5
        )
        ttk.Button(self.frame, text="AWAY GOAL", command=self._goal_away).pack(
            fill="x", pady=5
        )

        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Button(self.frame, text="UNDO LAST GOAL", command=self._undo).pack(
            fill="x", pady=5
        )

    # ---------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------
    def _get_players(self, team: str):
        """
        Take lineup from controller (already parsed from XML!)
        Expect structure:
        { "home": [ {"number": "30", "name": "Adam"}, ... ],
          "away": [ {...} ]
        }
        """
        try:
            return self.controller.lineup.get(team, [])
        except:
            return []

    # ---------------------------------------------------
    # BUTTON ACTIONS
    # ---------------------------------------------------
    def _goal_home(self):
        self._handle_goal("home")

    def _goal_away(self):
        self._handle_goal("away")

    def _handle_goal(self, team: str):
        players = self._get_players(team)

        number, name = pick_player(self.app.root, players, title="Välj målskytt")

        # send None if unknown player
        self.controller.goal_scored(team, number, name)

        # log
        if number:
            self.app.log(f"Mål {team.upper()}: {number} {name}")
        else:
            self.app.log(f"Mål {team.upper()}: Okänd spelare (ingen grafik efter mål)")

    def _undo(self):
        self.controller.undo_goal()
        self.app.log("Senaste mål ångrat.")
