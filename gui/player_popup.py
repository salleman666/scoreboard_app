import tkinter as tk
from tkinter import ttk

class PlayerSelectPopup(tk.Toplevel):
    """
    Popup för att välja målskytt / assisterande spelare.
    Sorterad efter tröjnummer.
    Välj OK utan spelare = returnera None.
    """

    def __init__(self, master, team_name, players, callback):
        super().__init__(master)
        self.title(f"Välj spelare – {team_name}")
        self.callback = callback
        self.selected = None

        self.geometry("420x520")
        self.grab_set()  # Modal

        # ---- Header ----
        tk.Label(self, text=f"{team_name}", font=("Arial", 16, "bold")).pack(pady=10)

        # ---- Listbox / Tree ----
        columns = ("nr", "name")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=18)
        self.tree.heading("nr", text="Nr")
        self.tree.heading("name", text="Namn")

        self.tree.column("nr", width=60, anchor="center")
        self.tree.column("name", width=300, anchor="w")

        # Sortera spelare efter nummer
        sorted_players = sorted(players, key=lambda p: int(p["number"]) if p["number"].isdigit() else 999)

        for p in sorted_players:
            self.tree.insert("", "end", values=(p["number"], p["name"]))

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # ---- Buttons ----
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Välj spelare", command=self._choose).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="OK (ingen spelare)", command=self._choose_none).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Avbryt", command=self.destroy).grid(row=0, column=2, padx=5)

    def _choose(self):
        """
        Returnera vald spelare.
        """
        item = self.tree.selection()
        if item:
            nr, name = self.tree.item(item[0], "values")
            self.callback({"number": nr, "name": name})
        else:
            self.callback(None)
        self.destroy()

    def _choose_none(self):
        """
        Inget val → None = ingen spelare.
        """
        self.callback(None)
        self.destroy()
