import tkinter as tk
from tkinter import ttk

class ClockPanel(tk.Frame):
    """
    UI panel for controlling main game clock.
    NOW SPEAKS WITH NEW ClockController API:
        self.controller.start()
        self.controller.toggle_pause()
        self.controller.stop()
        self.controller.adjust(delta)
        self.controller.set_period(idx)
    """

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # --- buttons row ---
        tk.Button(self, text="-5", width=4, command=lambda: self._adjust(-5)).grid(row=0, column=0, padx=3)
        tk.Button(self, text="-1", width=4, command=lambda: self._adjust(-1)).grid(row=0, column=1, padx=3)
        tk.Button(self, text="+1", width=4, command=lambda: self._adjust(+1)).grid(row=0, column=2, padx=3)
        tk.Button(self, text="+5", width=4, command=lambda: self._adjust(+5)).grid(row=0, column=3, padx=3)

        # --- start/pause toggle ---
        self.btn_toggle = tk.Button(self, text="START", width=14, command=self._toggle_clock)
        self.btn_toggle.grid(row=1, column=0, columnspan=4, pady=8)

        # --- period buttons ---
        periods = ["PERIOD 1", "PERIOD 2", "PERIOD 3", "PERIOD OT"]
        for i, p in enumerate(periods):
            tk.Button(
                self,
                text=p,
                width=10,
                command=lambda idx=i: self._set_period(idx)
            ).grid(row=2, column=i, padx=4, pady=8)

    # ---------------------------------------------------------

    def _toggle_clock(self):
        """
        Toggle play/pause using new API.
        """
        try:
            self.controller.toggle_pause()
        except:
            print("[ClockPanel] ERROR toggle_pause")

    def _adjust(self, seconds):
        """
        +/- seconds
        """
        try:
            self.controller.adjust(seconds)
        except:
            print("[ClockPanel] ERROR adjust")

    def _set_period(self, idx: int):
        """
        Change period => resets time
        """
        try:
            self.controller.set_period(idx)
        except:
            print("[ClockPanel] ERROR set_period")
