import tkinter as tk
from tkinter import ttk

from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.config.config_loader import load_config, save_config

# Controllers
from scoreboard_app.controllers.clock_controller import ClockController
from scoreboard_app.controllers.scoreboard_controller import ScoreboardController
from scoreboard_app.controllers.goal_controller import GoalController
from scoreboard_app.controllers.penalty_controller import PenaltyController

# Panels
from scoreboard_app.gui.clock_panel import ClockPanel
from scoreboard_app.gui.goal_panel import GoalPanel
from scoreboard_app.gui.penalty_panel import PenaltyPanel
from scoreboard_app.gui.settings_dialog import open_settings_dialog


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SCOREBOARD CONTROL")

        # --------------------------------------
        # Load config + Connect to vMix
        # --------------------------------------
        self.cfg = load_config()
        host = self.cfg.get("vmix", {}).get("host", "127.0.0.1")
        port = int(self.cfg.get("vmix", {}).get("port", 8088))

        self.client = VMixClient(host, port)

        # --------------------------------------
        # Initialize controllers (NO EXTRA ARG)
        # --------------------------------------
        self.clock = ClockController(self.client, self.cfg)
        self.scoreboard = ScoreboardController(self.client, self.cfg)
        self.goal = GoalController(self.client, self.cfg, self.scoreboard)
        self.penalty = PenaltyController(self.client, self.cfg, self.scoreboard)

        # --------------------------------------
        # Build UI
        # --------------------------------------
        nb = ttk.Notebook(self)
        nb.pack(expand=True, fill="both")

        nb.add(ClockPanel(self, self.clock), text="CLOCK")
        nb.add(GoalPanel(self, self.goal), text="GOALS")
        nb.add(PenaltyPanel(self, self.penalty), text="PENALTIES")

        # --------------------------------------
        # MENU + SETTINGS
        # --------------------------------------
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        settings = tk.Menu(menubar, tearoff=False)
        settings.add_command(
            label="Mappings & Settings",
            command=lambda: open_settings_dialog(self, self.cfg, self.client)
        )
        menubar.add_cascade(label="Settings", menu=settings)


def launch_app():
    app = MainWindow()
    app.mainloop()
