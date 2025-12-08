import tkinter as tk
from tkinter import ttk

from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.config.config_loader import load_config, save_config

from scoreboard_app.controllers.clock_controller import ClockController
from scoreboard_app.controllers.goal_controller import GoalController
from scoreboard_app.controllers.scoreboard_controller import ScoreboardController
from scoreboard_app.gui.settings_dialog import open_settings_dialog
from scoreboard_app.gui.clock_panel import ClockPanel
from scoreboard_app.gui.goal_panel import GoalPanel
from scoreboard_app.gui.empty_goal_panel import EmptyGoalPanel


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scoreboard Control")
        self.geometry("900x650")

        # --------------------------------------------
        # Load config from JSON
        # --------------------------------------------
        self.cfg = load_config()

        # --------------------------------------------
        # VMIX client
        # --------------------------------------------
        self.client = VMixClient()

        # --------------------------------------------
        # Controllers
        # --------------------------------------------
        self.clock = ClockController(self.client, self.cfg)
        self.scoreboard = ScoreboardController(self.client, self.cfg, self.clock)
        self.goal = GoalController(self.client, self.cfg, self.scoreboard)

        # --------------------------------------------
        # GUI PANELS
        # --------------------------------------------
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # CLOCK
        cp = ClockPanel(nb, self.clock)
        nb.add(cp, text="Clock")

        # GOALS
        gp = GoalPanel(nb, self.goal)
        nb.add(gp, text="Goals")

        # EMPTY GOAL
        eg = EmptyGoalPanel(nb, self.scoreboard)
        nb.add(eg, text="Empty Goal")

        # --------------------------------------------
        # SETTINGS BUTTON
        # --------------------------------------------
        settings_btn = ttk.Button(
            self,
            text="Mapping / Settings",
            command=lambda: open_settings_dialog(self, self.cfg)
        )
        settings_btn.pack(side="right", padx=10, pady=10)


def launch_app():
    app = MainWindow()
    app.mainloop()
