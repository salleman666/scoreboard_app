import tkinter as tk
from tkinter import ttk

from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.config_loader import load_config, save_config

from scoreboard_app.controllers.clock_controller import ClockController
from scoreboard_app.controllers.penalty_controller import PenaltyController
from scoreboard_app.controllers.scoreboard_controller import ScoreboardController
from scoreboard_app.controllers.goal_controller import GoalController

from scoreboard_app.gui.clock_panel import ClockPanel
from scoreboard_app.gui.penalty_panel import PenaltyPanel
from scoreboard_app.gui.scoreboard_panel import ScoreboardPanel
from scoreboard_app.gui.goal_panel import GoalPanel
from scoreboard_app.gui.emptygoal_panel import EmptyGoalPanel
from scoreboard_app.gui.mapping_dialog import MappingDialog


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scoreboard Control")

        # ----------------------------------------------------
        # 1) ALWAYS load config before controllers start
        # ----------------------------------------------------
        self.cfg = load_config()

        # ----------------------------------------------------
        # 2) Setup vMix client
        # ----------------------------------------------------
        host = self.cfg.get("vmix", {}).get("host", "127.0.0.1")
        port = self.cfg.get("vmix", {}).get("port", 8088)
        self.client = VMixClient(host, port)

        # ----------------------------------------------------
        # 3) Create controllers WITH loaded config
        # ----------------------------------------------------
        self.clock = ClockController(self.client, self.cfg)
        self.penalties = PenaltyController(self.client, self.cfg, self.clock)
        self.scoreboard = ScoreboardController(self.client, self.cfg)
        self.goals = GoalController(self.client, self.cfg, self.scoreboard)

        # ----------------------------------------------------
        # 4) Build UI
        # ----------------------------------------------------
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # CLOCK PANEL
        self.clock_panel = ClockPanel(body, self.clock)
        self.clock_panel.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        # SCOREBOARD PANEL
        self.scoreboard_panel = ScoreboardPanel(body, self.scoreboard)
        self.scoreboard_panel.grid(row=0, column=1, padx=5, pady=5, sticky="n")

        # GOAL PANEL
        self.goal_panel = GoalPanel(body, self.goals)
        self.goal_panel.grid(row=0, column=2, padx=5, pady=5, sticky="n")

        # PENALTY PANEL
        self.penalty_panel = PenaltyPanel(body, self.penalties)
        self.penalty_panel.grid(row=1, column=0, padx=5, pady=5, sticky="n")

        # EMPTY GOAL PANEL
        self.emptygoal_panel = EmptyGoalPanel(body, self.scoreboard)
        self.emptygoal_panel.grid(row=1, column=1, padx=5, pady=5, sticky="n")

        # ----------------------------------------------------
        # SETTINGS BUTTON
        # ----------------------------------------------------
        settings_btn = ttk.Button(
            body,
            text="⚙ Settings / Mapping",
            command=self._open_mapping_dialog
        )
        settings_btn.grid(row=2, column=0, columnspan=3, pady=20)

    # ====================================================
    # OPEN MAPPING DIALOG
    # ====================================================
    def _open_mapping_dialog(self):
        dlg = MappingDialog(self, self.cfg, self.client)
        self.wait_window(dlg)

        # ALWAYS reload config after mapping dialog closes
        self.cfg = load_config()

        # RECONNECT controllers to updated cfg
        self.clock.cfg = self.cfg
        self.penalties.cfg = self.cfg
        self.scoreboard.cfg = self.cfg
        self.goals.cfg = self.cfg

        save_config(self.cfg)


def launch_app():
    win = MainWindow()
    win.mainloop()


if __name__ == "__main__":
    launch_app()
