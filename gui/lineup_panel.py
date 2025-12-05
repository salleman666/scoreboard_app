import tkinter as tk
from tkinter import ttk, messagebox

from scoreboard_app.controllers.team_controller import TeamController


class LineupPanel(tk.Frame):
    """
    GUI-panel för att styra lineup-grafik för båda lagen.

    Funktioner:
    - Uppdatera hemmalagets lineup
    - Uppdatera bortalagets lineup
    - Visa lineup live
    - Dölj lineup
    """

    def __init__(self, master, controller: TeamController):
        super().__init__(master, borderwidth=2, relief="groove")
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        title = tk.Label(self, text="LINEUP", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(4, 8))

        # -----------------------------
        # HOME
        # -----------------------------
        ttk.Label(self, text="Hemmalag:", font=("Segoe UI", 11, "bold")).grid(
            row=1, column=0, sticky="w", padx=4
        )

        ttk.Button(self, text="Uppdatera Lineup (Home)",
                   command=self.update_home).grid(
            row=2, column=0, sticky="ew", padx=6, pady=2
        )

        ttk.Button(self, text="Visa HOME Lineup",
                   command=lambda: self.show("home")).grid(
            row=3, column=0, sticky="ew", padx=6, pady=2
        )

        # -----------------------------
        # AWAY
        # -----------------------------
        ttk.Label(self, text="Bortalag:", font=("Segoe UI", 11, "bold")).grid(
            row=1, column=1, sticky="w", padx=4
        )

        ttk.Button(self, text="Uppdatera Lineup (Away)",
                   command=self.update_away).grid(
            row=2, column=1, sticky="ew", padx=6, pady=2
        )

        ttk.Button(self, text="Visa AWAY Lineup",
                   command=lambda: self.show("away")).grid(
            row=3, column=1, sticky="ew", padx=6, pady=2
        )

        # -----------------------------
        # Hide lineup
        # -----------------------------
        ttk.Button(self, text="DÖLJ LINEUP",
                   command=self.hide).grid(
            row=4, column=0, columnspan=2,
            sticky="ew", padx=6, pady=(10, 4)
        )

    # ------------------------------------------------------------
    def update_home(self):
        try:
            self.controller.update_lineup(team="home")
            messagebox.showinfo("Lineup", "Hemmalagets lineup uppdaterad!")
        except Exception as e:
            messagebox.showerror("Fel", str(e))

    # ------------------------------------------------------------
    def update_away(self):
        try:
            self.controller.update_lineup(team="away")
            messagebox.showinfo("Lineup", "Bortalagets lineup uppdaterad!")
        except Exception as e:
            messagebox.showerror("Fel", str(e))

    # ------------------------------------------------------------
    def show(self, team):
        try:
            self.controller.show_lineup(team)
        except Exception as e:
            messagebox.showerror("Fel", str(e))

    # ------------------------------------------------------------
    def hide(self):
        try:
            self.controller.hide_lineup()
        except Exception as e:
            messagebox.showerror("Fel", str(e))
