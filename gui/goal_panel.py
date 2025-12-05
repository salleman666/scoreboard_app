import tkinter as tk
from tkinter import ttk
from scoreboard_app.controllers.goal_controller import GoalController
from scoreboard_app.gui.player_select_dialog import PlayerSelectDialog


class GoalPanel(tk.Frame):
    """
    GUI for entering goals (home/away teams) and optionally selecting the scoring player.
    """

    def __init__(self, master, controller: GoalController):
        super().__init__(master, relief="groove", bd=2)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        title = tk.Label(self, text="MÅL", font=("Segoe UI", 12, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=5)

        # -------- HOME GOAL ---------
        self.btn_home_goal = ttk.Button(
            self,
            text="➕ HEMMA MÅL",
            command=lambda: self._register_goal("home")
        )
        self.btn_home_goal.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # -------- AWAY GOAL ---------
        self.btn_away_goal = ttk.Button(
            self,
            text="➕ BORTA MÅL",
            command=lambda: self._register_goal("away")
        )
        self.btn_away_goal.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    # ------------------------------------------------------------------
    def _register_goal(self, team: str):
        """
        When a goal button is pressed:
        - ask for optional player
        - update score
        - show scoring graphic if player is known
        """

        # Ask popup for player
        player = PlayerSelectDialog(self.master, team=team).show()

        # CASE 1: NO PLAYER SELECTED (just goal)
        if not player:
            self.controller.add_goal(team=team)
            return

        # CASE 2: PLAYER SELECTED
        self.controller.add_goal(
            team=team,
            player_number=player.get("number"),
            player_name=player.get("name"),
            player_logo=player.get("logo", None)
        )
