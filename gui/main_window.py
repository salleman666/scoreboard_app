import tkinter as tk
from tkinter import ttk, messagebox

from scoreboard_app.controllers.scoreboard_controller import ScoreboardController
from scoreboard_app.controllers.clock_controller import ClockController
from scoreboard_app.controllers.goal_controller import GoalController
from scoreboard_app.controllers.penalty_controller import PenaltyController
from scoreboard_app.controllers.shots_controller import ShotsController
from scoreboard_app.controllers.team_controller import TeamController

from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.config.vmix_config import load_config

from scoreboard_app.gui.goal_panel import GoalPanel
from scoreboard_app.gui.clock_panel import ClockPanel
from scoreboard_app.gui.penalty_panel import PenaltyPanel
from scoreboard_app.gui.emptygoal_panel import EmptyGoalPanel
from scoreboard_app.gui.scoreboard_panel import ScoreboardPanel
from scoreboard_app.gui.lineup_panel import LineupPanel
from scoreboard_app.gui.settings_dialog import open_settings_dialog


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scoreboard Controller – NEW ENGINE")
        self.geometry("1400x820")

        # -----------------------------
        # Load config + client
        # -----------------------------
        self.cfg = load_config()
        vm = self.cfg["vmix"]
        self.client = VMixClient(vm["host"], vm["port"])
        self.controller = ScoreboardController(self.client, self.cfg)

        # Sub-controllers
        self.clock = ClockController(self.client, self.cfg)
        self.goals = GoalController(self.client, self.cfg)
        self.penalties = PenaltyController(self.client, self.cfg)
        self.shots = ShotsController(self.client, self.cfg)
        self.teams = TeamController(self.client, self.cfg)

        # -----------------------------
        # GUI layout
        # -----------------------------
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Top bar
        top = tk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top.columnconfigure(2, weight=1)

        ttk.Button(
            top, text="⚙ INSTÄLLNINGAR",
            command=lambda: open_settings_dialog(self, self.cfg)
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            top, text="↻ Uppdatera Inputs",
            command=self.refresh_inputs
        ).grid(row=0, column=1, padx=5)

        self.status_lbl = tk.Label(
            top, text="Ej ansluten", fg="red", font=("Segoe UI", 10)
        )
        self.status_lbl.grid(row=0, column=2, sticky="e")

        # BODY
        body = tk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew", padx=10)
        for i in range(3):
            body.columnconfigure(i, weight=1)
        for i in range(2):
            body.rowconfigure(i, weight=1)

        # -----------------------------
        # GUI-Panels
        # -----------------------------
        self.goal_panel = GoalPanel(body, self.goals)
        self.goal_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.clock_panel = ClockPanel(body, self.clock)
        self.clock_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.penalty_panel = PenaltyPanel(body, self.penalties)
        self.penalty_panel.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        self.emptygoal_panel = EmptyGoalPanel(body, self.controller)
        self.emptygoal_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.scoreboard_panel = ScoreboardPanel(body, self.controller)
        self.scoreboard_panel.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.lineup_panel = LineupPanel(body, self.teams)
        self.lineup_panel.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

        # Start connection monitor
        self.after(400, self._connect_test)

    # ------------------------------------------------------------
    def _connect_test(self):
        try:
            self.client.get_status_xml()
            self.status_lbl.config(text="Ansluten till vMix", fg="green")
        except Exception as e:
            self.status_lbl.config(text=f"Fel: {e}", fg="red")

        self.after(3000, self._connect_test)

    # ------------------------------------------------------------
    def refresh_inputs(self):
        try:
            inputs = self.client.list_inputs()
            messagebox.showinfo("Inputs", f"{len(inputs)} inputs mottagna.")
        except Exception as e:
            messagebox.showerror("Fel", str(e))


def main():
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
