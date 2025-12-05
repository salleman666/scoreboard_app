import tkinter as tk
from tkinter import ttk


class PlayerSelectDialog(tk.Toplevel):
    """
    Popup där operatören kan välja en spelare från ett lag.
    Return value = dict med {name, number, team}
    eller None om cancel.
    """

    def __init__(self, master, team: str, players: list[dict]):
        """
        Args:
            master: parent window
            team: 'home' or 'away'
            players: list of dicts: [{"name": "...", "number": "..."}]
        """
        super().__init__(master)
        self.title("Välj spelare")
        self.geometry("500x500")
        self.transient(master)
        self.grab_set()

        self.team = team
        self.players = players
        self.selected_player = None

        # --- UI layout ---
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text=f"{team.upper()} spelare",
                  font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=10
        )

        # listbox
        frame = ttk.Frame(self)
        frame.grid(row=1, column=0, sticky="nsew", padx=10)

        self.listbox = tk.Listbox(frame, font=("Segoe UI", 11))
        self.listbox.pack(fill="both", expand=True)

        # populate
        for p in self.players:
            self.listbox.insert("end", f"{p['number']} – {p['name']}")

        # buttons
        btns = ttk.Frame(self)
        btns.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        ttk.Button(btns, text="OK", command=self._ok).pack(side="left", padx=5)
        ttk.Button(btns, text="Avbryt", command=self._cancel).pack(side="left", padx=5)

    # -----------------------------------------
    def _ok(self):
        idx = self.listbox.curselection()
        if not idx:
            self.selected_player = None
        else:
            p = self.players[idx[0]]
            self.selected_player = {
                "name": p["name"],
                "number": p["number"],
                "team": self.team
            }
        self.destroy()

    def _cancel(self):
        self.selected_player = None
        self.destroy()

    # -----------------------------------------
    def show(self):
        """
        Block and wait
        """
        self.wait_window()
        return self.selected_player
