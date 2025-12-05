import tkinter as tk
from tkinter import ttk, messagebox

from scoreboard_app.controllers.penalty_controller import PenaltyController


class PenaltyPanel(tk.LabelFrame):
    """
    GUI-panel för att kontrollera alla 4 penalty-fält:
        Home P1, Home P2, Away P1, Away P2

    - Live visar:
        nummer
        namn (om finns)
        återstående tid
    - Kan:
        starta nedräkning
        pausa nedräkning
        rensa penalty
        auto-refresh varje sekund
    """

    REFRESH_MS = 1000

    def __init__(self, parent, controller: PenaltyController):
        super().__init__(parent, text="Utv PAC (Penalties)", padx=6, pady=6)

        self.controller = controller

        # -------------------------------
        # UI LAYOUT
        # -------------------------------
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # HOME
        ttk.Label(self, text="HEMMA").grid(row=0, column=0, sticky="w")

        self.h1_label = ttk.Label(self, text="H1 – tid: --:--  nr: --")
        self.h1_label.grid(row=1, column=0, sticky="w")

        self.h2_label = ttk.Label(self, text="H2 – tid: --:--  nr: --")
        self.h2_label.grid(row=2, column=0, sticky="w")

        # AWAY
        ttk.Label(self, text="BORTE").grid(row=0, column=1, sticky="w")

        self.a1_label = ttk.Label(self, text="A1 – tid: --:--  nr: --")
        self.a1_label.grid(row=1, column=1, sticky="w")

        self.a2_label = ttk.Label(self, text="A2 – tid: --:--  nr: --")
        self.a2_label.grid(row=2, column=1, sticky="w")

        # -------------------------------
        # KONTROLLKNAPPAR
        # -------------------------------
        btns = tk.Frame(self)
        btns.grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Button(
            btns, text="Start alla", command=self.start_all
        ).grid(row=0, column=0, padx=4)

        ttk.Button(
            btns, text="Pausa alla", command=self.pause_all
        ).grid(row=0, column=1, padx=4)

        ttk.Button(
            btns, text="Rensa alla", command=self.clear_all
        ).grid(row=0, column=2, padx=4)

        # -------------------------------
        # AUTO REFRESH
        # -------------------------------
        self.after(self.REFRESH_MS, self._refresh)

    # ============================================================
    # BUTTON ACTIONS
    # ============================================================

    def start_all(self):
        try:
            self.controller.start_all_penalties()
        except Exception as e:
            messagebox.showerror("Fel", str(e))

    def pause_all(self):
        try:
            self.controller.pause_all_penalties()
        except Exception as e:
            messagebox.showerror("Fel", str(e))

    def clear_all(self):
        if not messagebox.askyesno("Bekräfta", "Rensa alla utvisningar?"):
            return

        try:
            self.controller.clear_home_penalties()
            self.controller.clear_away_penalties()
        except Exception as e:
            messagebox.showerror("Fel", str(e))

    # ============================================================
    # REFRESH DISPLAY
    # ============================================================

    def _refresh(self):
        """
        Hämtar penalty status från controller och uppdaterar UI.
        """
        try:
            status = self.controller.get_all_penalty_status()
            # status = {
            #   "home": { "p1": {...}, "p2": {...} },
            #   "away": { "p1": {...}, "p2": {...} }
            # }

            # HOME
            h1 = status["home"]["p1"]
            h2 = status["home"]["p2"]

            self.h1_label.config(
                text=f"H1 – tid: {h1['time']}  nr: {h1['number']}"
            )

            self.h2_label.config(
                text=f"H2 – tid: {h2['time']}  nr: {h2['number']}"
            )

            # AWAY
            a1 = status["away"]["p1"]
            a2 = status["away"]["p2"]

            self.a1_label.config(
                text=f"A1 – tid: {a1['time']}  nr: {a1['number']}"
            )

            self.a2_label.config(
                text=f"A2 – tid: {a2['time']}  nr: {a2['number']}"
            )

        except Exception as e:
            # visa, men krascha inte GUI
            print("[PenaltyPanel] refresh error:", e)

        finally:
            # loop
            self.after(self.REFRESH_MS, self._refresh)
