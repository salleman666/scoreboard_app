import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog

class PlayerSelectDialog(simpledialog.Dialog):
    """
    Popup-dialog som listar alla spelare i laget.
    Ingen rullista – en knapp per spelare.
    """
    def __init__(self, parent, title, players, slot):
        self.players = players     # list of dicts: {"number": "21", "name": "J. Karlsson"}
        self.slot = slot
        self.selected_number = ""
        self.selected_name = ""
        self.time_str = "02:00"
        super().__init__(parent, title)

    def body(self, frame):
        tk.Label(frame, text=f"Välj spelare för {self.slot}", font=("Segoe UI", 12, "bold")).pack(pady=5)

        list_frame = tk.Frame(frame)
        list_frame.pack(pady=5)

        for p in self.players:
            b = tk.Button(
                list_frame,
                text=f"{p['number']}  {p['name']}",
                width=25,
                command=lambda num=p['number'], nm=p['name']: self._select_player(num, nm)
            )
            b.pack(pady=2)

        # Ingen spelare
        tk.Button(
            frame,
            text="Ingen spelare (visa bara tid)",
            fg="red",
            command=lambda: self._select_player("", "")
        ).pack(pady=5)

        # Tidsfält
        time_row = tk.Frame(frame)
        time_row.pack(pady=5)

        tk.Label(time_row, text="Tid (MM:SS): ").grid(row=0, column=0)
        self.time_entry = tk.Entry(time_row, width=6)
        self.time_entry.insert(0, "02:00")
        self.time_entry.grid(row=0, column=1)

        return None

    def _select_player(self, num, name):
        self.selected_number = num
        self.selected_name = name

    def apply(self):
        self.time_str = self.time_entry.get()


class PenaltyPanel:
    """
    Panelen med knappar för H1, H2, A1, A2.
    Öppnar PlayerSelectDialog vid klick.
    """
    def __init__(self, parent, controller, home_players, away_players):
        self.parent = parent
        self.controller = controller
        self.home_players = home_players
        self.away_players = away_players

        self.frame = tk.Frame(parent)

        tk.Label(self.frame, text="UTVISNINGAR", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=4)

        self.buttons = {}

        col = 0
        for slot in ["H1", "H2", "A1", "A2"]:
            b = tk.Button(
                self.frame,
                text=f"{slot}\n00:00",
                width=8,
                height=3,
                command=lambda s=slot: self.open_dialog(s)
            )
            b.grid(row=1, column=col, padx=6, pady=6)
            self.buttons[slot] = b
            col += 1

    def open_dialog(self, slot):
        if slot.startswith("H"):
            players = self.home_players
        else:
            players = self.away_players

        dlg = PlayerSelectDialog(self.frame, f"Utvisning {slot}", players, slot)

        # Om användaren klickar Cancel:
        if dlg.selected_number is None:
            return

        num = dlg.selected_number
        name = dlg.selected_name
        tid = dlg.time_str

        # Uppdatera knappens text
        self.buttons[slot].config(text=f"{slot}\n{tid}")

        # Skicka till controller
        try:
            self.controller.set_penalty(slot, num, name, tid)
        except Exception as e:
            print(f"[ERROR] set_penalty misslyckades: {e}")

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
