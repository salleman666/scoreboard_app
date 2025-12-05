import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class PenaltyPanel(tk.LabelFrame):
    """
    Auto-generated penalty GUI panel based on config mapping.
    Supports:
      - Unlimited penalty slots for home and away if config expands
      - Automatic refresh of values
      - Buttons for manual override
    """

    REFRESH_MS = 800

    def __init__(self, master, controller, cfg: Dict[str, Any]):
        super().__init__(master, text="PENALTIES", padx=10, pady=10, font=("Segoe UI", 12, "bold"))

        self.controller = controller
        self.cfg = cfg

        # penalty mapping reference
        self.mapping = cfg["mapping"]["penalties"]

        # storage of GUI widgets
        self.rows: Dict[str, Dict[str, tk.Label]] = {}

        # build dynamic UI
        self._build_layout()

        # start auto refresh
        self.after(self.REFRESH_MS, self._refresh)

    # ----------------------------------------------------------------------
    def _build_layout(self):
        row = 0

        ttk.Label(self, text="TEAM", width=10).grid(row=row, column=0, sticky="w")
        ttk.Label(self, text="#", width=6).grid(row=row, column=1, sticky="w")
        ttk.Label(self, text="TIME", width=8).grid(row=row, column=2, sticky="w")
        ttk.Label(self, text="", width=10).grid(row=row, column=3)
        row += 1

        for side in ["home", "away"]:
            slots = self.mapping[side]

            for slot_key, slot_fields in slots.items():
                row_id = f"{side}_{slot_key}"

                team_lbl = ttk.Label(self, text=side.upper(), width=10)
                team_lbl.grid(row=row, column=0, sticky="w")

                num_lbl = ttk.Label(self, text="", width=6)
                num_lbl.grid(row=row, column=1, sticky="w")

                time_lbl = ttk.Label(self, text="", width=8)
                time_lbl.grid(row=row, column=2, sticky="w")

                btn = ttk.Button(
                    self,
                    text="✖ CLEAR",
                    width=8,
                    command=lambda s=side, k=slot_key: self._clear(s, k)
                )
                btn.grid(row=row, column=3, sticky="e")

                self.rows[row_id] = {
                    "number": num_lbl,
                    "time": time_lbl,
                }

                row += 1

        # bottom actions
        ttk.Button(self, text="➕ ADD PENALTY", command=self._start_penalty)\
            .grid(row=row, column=0, pady=10)

        ttk.Button(self, text="✖ CLEAR ALL", command=self._clear_all)\
            .grid(row=row, column=1, pady=10)

    # ----------------------------------------------------------------------
    def _refresh(self):
        """ Read current penalty values from controller and update GUI """
        try:
            status = self.controller.get_status()  # MUST RETURN mapping like {home:{p1:{time:"",number:""},...}}
        except Exception as e:
            print("[PenaltyPanel] refresh error:", e)
            self.after(self.REFRESH_MS, self._refresh)
            return

        for row_id, widgets in self.rows.items():
            side, slot = row_id.split("_")
            slot_data = status.get(side, {}).get(slot, {})

            widgets["number"].config(text=slot_data.get("number", ""))
            widgets["time"].config(text=slot_data.get("time", ""))

        self.after(self.REFRESH_MS, self._refresh)

    # ----------------------------------------------------------------------
    def _start_penalty(self):
        """ Open a dialog to select team, player and time """
        try:
            self.controller.start_penalty_dialog(self.master)
        except Exception as e:
            print("[PenaltyPanel] start_penalty error:", e)

    # ----------------------------------------------------------------------
    def _clear(self, side: str, slot_key: str):
        try:
            self.controller.clear_penalty(side, slot_key)
        except Exception as e:
            print("[PenaltyPanel] clear_penalty error:", e)

    # ----------------------------------------------------------------------
    def _clear_all(self):
        try:
            self.controller.clear_all_penalties()
        except Exception as e:
            print("[PenaltyPanel] clear_all error:", e)
