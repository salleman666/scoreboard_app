import tkinter as tk
from tkinter import ttk

class PlayerSelectDialog(tk.Toplevel):
    """
    Dialog for selecting player number + player name.
    Supports HOME or AWAY side via team parameter.
    """
    def __init__(self, parent, team="home"):
        super().__init__(parent)
        self.parent = parent
        self.team = team  # <-- IMPORTANT
        self.title(f"Select Player ({team.upper()})")

        # store result here
        self.result = None

        # modal dialog behavior
        self.grab_set()
        self.focus_force()

        # layout
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Player Number:").grid(row=0, column=0, sticky="w")
        self.num_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.num_var, width=10).grid(row=0, column=1, sticky="w")

        ttk.Label(frm, text="Player Name:").grid(row=1, column=0, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.name_var, width=25).grid(row=1, column=1, sticky="w")

        btn = ttk.Frame(frm)
        btn.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(btn, text="OK", command=self._on_ok).pack(side="left", padx=5)
        ttk.Button(btn, text="Cancel", command=self._on_cancel).pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_ok(self):
        """
        Returns a dict with player data:

        {
            "team": "home" | "away",
            "number": "12",
            "name": "John Doe"
        }
        """
        number = self.num_var.get().strip()
        name = self.name_var.get().strip()

        if number or name:
            self.result = {
                "team": self.team,
                "number": number,
                "name": name
            }

        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    def show(self):
        """
        Make dialog blocking and return result
        """
        self.wait_window()
        return self.result
