import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from scoreboard_app.core.vmix_client import VMixClient


class PenaltySelectDialog(tk.Toplevel):
    """
    Shows roster list + duration options.
    Returns dict:
        {
            "number": str or "",
            "name": str or "",
            "duration": minutes (int)
        }
    """
    def __init__(self, parent, input_title):
        super().__init__(parent)
        self.title("Penalty Selection")
        self.geometry("600x800")

        self.client = VMixClient()
        self.input_title = input_title

        self.result = None

        # parsed roster = list of (number,name)
        self.players = self._load_players()
        self.selected_player = None
        self.selected_duration = None

        self._build_gui()

    def _load_players(self):
        """Parse lineup XML and extract (number,name) pairs sorted"""
        xml = self.client.get_status_xml()
        if xml is None:
            return []

        # find input
        for inp in xml.findall(".//input"):
            if inp.get("title") == self.input_title:
                # scan text fields
                texts = inp.findall(".//text")
                numbers = {}
                names = {}
                for t in texts:
                    nm = t.get("name")
                    val = (t.text or "").strip()
                    if nm.endswith("_number.Text"):
                        key = nm.replace("_number.Text", "")
                        numbers[key] = val
                    elif nm.endswith("_name.Text"):
                        key = nm.replace("_name.Text", "")
                        names[key] = val

                roster = []
                for k, nr in numbers.items():
                    nm = names.get(k, "")
                    if nr:
                        roster.append((nr, nm))

                # sort numeric
                roster.sort(key=lambda x: int(x[0]))
                return roster

        return []

    def _build_gui(self):
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.listbox = tk.Listbox(list_frame, font=("Arial", 14))
        self.listbox.pack(fill="both", expand=True)

        for nr, nm in self.players:
            self.listbox.insert("end", f"{nr}  {nm}")

        self.listbox.bind("<<ListboxSelect>>", self._on_select_player)

        # Duration buttons
        dur_frame = tk.Frame(self)
        dur_frame.pack(pady=10)
        for mins in [2, 4, 5, 10]:
            btn = tk.Button(dur_frame, text=f"{mins} MIN",
                            command=lambda m=mins: self._on_select_duration(m))
            btn.pack(side="left", padx=10)

        # Bottom buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="OK (Player + Time)",
                  command=self._ok_player_and_time).pack(side="left", padx=10)

        tk.Button(btn_frame, text="OK (Time Only)",
                  command=self._ok_time_only).pack(side="left", padx=10)

        tk.Button(btn_frame, text="Cancel",
                  command=self._cancel).pack(side="left", padx=10)

    def _on_select_player(self, _):
        sel = self.listbox.curselection()
        if not sel:
            self.selected_player = None
            return
        idx = sel[0]
        nr, nm = self.players[idx]
        self.selected_player = (nr, nm)

    def _on_select_duration(self, mins):
        self.selected_duration = mins

    def _ok_player_and_time(self):
        if not self.selected_duration:
            return
        nr = ""
        nm = ""
        if self.selected_player:
            nr, nm = self.selected_player
        self.result = {
            "number": nr,
            "name": nm,
            "duration": self.selected_duration,
        }
        self.destroy()

    def _ok_time_only(self):
        if not self.selected_duration:
            return
        self.result = {
            "number": "",
            "name": "",
            "duration": self.selected_duration,
        }
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

    def run(self):
        self.grab_set()
        self.wait_window()
        return self.result
