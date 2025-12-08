import tkinter as tk
from tkinter import ttk

from scoreboard_app.gui.player_select_dialog import PlayerSelectDialog


class GoalPanel(ttk.Frame):
    """
    GUI for registering goals:
      - HOME goal
      - AWAY goal
      - All logic delegated to GoalController
    """

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller  # GoalController instance

        self._build_ui()

    # ==========================================================
    # UI
    # ==========================================================

    def _build_ui(self):
        ttk.Label(self, text="GOALS", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, pady=5
        )

        ttk.Button(
            self,
            text="HOME GOAL",
            command=lambda: self._register_goal("home"),
            width=20
        ).grid(row=1, column=0, padx=5, pady=5)

        ttk.Button(
            self,
            text="AWAY GOAL",
            command=lambda: self._register_goal("away"),
            width=20
        ).grid(row=1, column=1, padx=5, pady=5)

    # ==========================================================
    # EVENT
    # ==========================================================

    def _register_goal(self, team: str):
        """
        Called when either button is pressed.
        - Pops player select
        - Calls GoalController.add_goal(...)
        """

        dlg = PlayerSelectDialog(self, team)
        result = dlg.show()

        if not result:
            return  # user cancelled

        player_name = result.get("name", "").strip()
        player_number = result.get("number", "").strip()

        if not player_name:
            # minimal fallback: scorer number only
            player_name = f"#{player_number}"

        try:
            self.controller.add_goal(
                team=team,
                scorer_name=player_name,
                scorer_number=player_number
            )
        except Exception as e:
            print("[GoalPanel] ERROR add_goal:", e)
