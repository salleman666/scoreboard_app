import tkinter as tk
from tkinter import ttk

class PlayerSelectDialog(tk.Toplevel):
    """
    Popup för att välja spelare.
    - Visar alla spelare i sorterad lista (tröjnummer).
    - OK utan val => returnerar None.
    """

    def __init__(self, parent, title, players, team_logo=None, team_name=None):
        """
        players = list of dicts:
        [
            {
                "number": "22",
                "name": "Johan Lindholm",
                "team": "SUN",     # optional
                "logo": "https://..."  # optional
            },
            ...
        ]
        """
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry("420x500")
        self.resizable(False, True)

        self.selected_player = None  # None = ingen vald, OK = No-Player logic

        # Sortera spelare på nummer
        players_sorted = sorted(players, key=lambda p: int(p["number"]) if p["number"].isdigit() else 999)

        # ----- UI -----
        header = tk.Label(self, text=title, font=("Segoe UI", 16, "bold"))
        header.pack(pady=10)

        # Team info (om finns)
        if team_name:
            tk.Label(self, text=f"Lag: {team_name}", font=("Segoe UI", 11)).pack()

        # Lista
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.listbox = tk.Listbox(frame, font=("Segoe UI", 12), height=20)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Lägg in alla spelare i listan
        for p in players_sorted:
            num = p["number"]
            name = p["name"]
            display = f"{num:>2}   {name}"
            self.listbox.insert(tk.END, display)

        # Knappar
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="OK", width=12, command=self._ok).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Avbryt", width=12, command=self._cancel).grid(row=0, column=1, padx=5)

        # Modal
        self.grab_set()
        self.wait_window()

    # ---------------------------------------------------------------------

    def _ok(self):
        """OK tryckt — returnera vald spelare eller None."""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            text = self.listbox.get(index)

            # Extract number + name
            number = text.split()[0]
            name = " ".join(text.split()[1:])

            self.selected_player = {
                "number": number,
                "name": name
            }
        else:
            # Ingen vald → betyder No-player mode
            self.selected_player = None

        self.destroy()

    def _cancel(self):
        self.selected_player = None
        self.destroy()
