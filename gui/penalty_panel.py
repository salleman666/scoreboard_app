import tkinter as tk
from tkinter import ttk
import logging


class PenaltyPanel(tk.Frame):
    """
    Displays 2 HOME penalty slots and 2 AWAY penalty slots.

    Reads configuration as:
        cfg["penalties"]["home"] = [slot0, slot1]
        cfg["penalties"]["away"] = [slot0, slot1]

    Controller interface:
        controller.get_penalties() -> {
            "home": [slot0, slot1],
            "away": [slot0, slot1]
        }
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.cfg = controller.cfg

        # CONFIG IS HERE NOW
        self.mapping = self.cfg["penalties"]

        self._build_gui()

        # refresh loop
        self.after(1000, self._refresh)

    def _build_gui(self):
        """
        Build static layout: 4 rows (H1,H2,A1,A2)
        """
        title = tk.Label(self, text="PENALTIES", font=("Arial", 14, "bold"))
        title.pack(pady=4)

        table = tk.Frame(self)
        table.pack(fill="x", padx=4, pady=4)

        headers = ["TEAM", "TIME", "NUMBER", "NAME"]
        for c, h in enumerate(headers):
            tk.Label(table, text=h, font=("Arial", 10, "bold")).grid(row=0, column=c, padx=6)

        # HOME rows
        self.home_rows = []
        for i in range(2):
            row_widgets = self._make_row(table, 1 + i, is_home=True, index=i)
            self.home_rows.append(row_widgets)

        # AWAY rows
        self.away_rows = []
        for i in range(2):
            row_widgets = self._make_row(table, 3 + i, is_home=False, index=i)
            self.away_rows.append(row_widgets)

    def _make_row(self, parent, r, is_home, index):
        """
        Create a GUI row:
           TEAM LABEL | TIME | NUMBER | NAME
        """
        team_txt = "HOME" if is_home else "AWAY"
        team_label = tk.Label(parent, text=f"{team_txt} {index+1}")
        team_label.grid(row=r, column=0, padx=6, pady=2)

        time_var = tk.StringVar(value="")
        nr_var = tk.StringVar(value="")
        nm_var = tk.StringVar(value="")

        tk.Label(parent, textvariable=time_var).grid(row=r, column=1, padx=6)
        tk.Label(parent, textvariable=nr_var).grid(row=r, column=2, padx=6)
        tk.Label(parent, textvariable=nm_var).grid(row=r, column=3, padx=6)

        return {
            "time": time_var,
            "nr": nr_var,
            "name": nm_var
        }

    def _refresh(self):
        """
        Pull latest penalty info from controller and display it.
        """
        try:
            data = self.controller.get_penalties()

            # HOME
            for i, slot in enumerate(data["home"]):
                self.home_rows[i]["time"].set(slot["time"])
                self.home_rows[i]["nr"].set(slot["number"])
                self.home_rows[i]["name"].set(slot["name"])

            # AWAY
            for i, slot in enumerate(data["away"]):
                self.away_rows[i]["time"].set(slot["time"])
                self.away_rows[i]["nr"].set(slot["number"])
                self.away_rows[i]["name"].set(slot["name"])

        except Exception as e:
            logging.error(f"[PenaltyPanel] refresh error: {e}")

        finally:
            self.after(1000, self._refresh)
