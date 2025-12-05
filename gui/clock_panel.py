# clock_panel.py
# ------------------------------------------------------------
# GUI-panel för:
#  • Start/Stop av matchklockan
#  • +1 / -1 / +5 / -5 justering av tid
#  • Visning av aktuell tid
#  • Period-knappar (1 / 2 / 3 / OT)
#
# Panelen är 100% ren GUI och anropar endast controller:
#   controller.start_clock()
#   controller.stop_clock()
#   controller.adjust_time(+/- sek)
#   controller.set_period(n)
#   controller.get_state() → för uppdatering av tid & period
# ------------------------------------------------------------

import tkinter as tk
from tkinter import ttk


class ClockPanel(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self._clock_running = False
        self._current_period = 1

        self._build_ui()

    # ---------------------------------------------------------
    # UI layout
    # ---------------------------------------------------------
    def _build_ui(self):
        self.config(padx=10, pady=10)

        # --- KNAPPRAD MED TIDJUSTERING ---
        adjust_frame = tk.Frame(self)
        adjust_frame.pack(pady=5)

        tk.Button(adjust_frame, text="-5", width=5,
                  command=lambda: self._adjust(-5)).grid(row=0, column=0, padx=3)

        tk.Button(adjust_frame, text="-1", width=5,
                  command=lambda: self._adjust(-1)).grid(row=0, column=1, padx=3)

        tk.Button(adjust_frame, text="+1", width=5,
                  command=lambda: self._adjust(+1)).grid(row=0, column=2, padx=3)

        tk.Button(adjust_frame, text="+5", width=5,
                  command=lambda: self._adjust(+5)).grid(row=0, column=3, padx=3)

        # --- STOR KLOCKKNAPP ---
        self.clock_btn = tk.Button(
            self,
            text="START\n--:--",
            width=12,
            height=4,
            font=("Segoe UI", 18, "bold"),
            bg="green",
            fg="black",
            command=self._toggle_clock
        )
        self.clock_btn.pack(pady=10)

        # --- PERIODKNAPPAR ---
        period_frame = tk.Frame(self)
        period_frame.pack(pady=5)

        self.period_buttons = {}

        labels = ["1", "2", "3", "OT"]
        for idx, label in enumerate(labels, start=1):
            b = tk.Button(
                period_frame,
                text=f"PERIOD\n{label}",
                width=8,
                height=2,
                font=("Segoe UI", 10, "bold"),
                command=lambda p=idx: self._set_period(p)
            )
            b.grid(row=0, column=idx - 1, padx=5)
            self.period_buttons[idx] = b

        self._refresh_period_buttons()

    # ---------------------------------------------------------
    # Event callbacks
    # ---------------------------------------------------------
    def _toggle_clock(self):
        """Start/Stop tidtagning"""
        if self._clock_running:
            self.controller.stop_clock()
        else:
            self.controller.start_clock()

        self._clock_running = not self._clock_running
        self._refresh_clock_button()

    def _adjust(self, seconds):
        """Justerar tid (± sekunder)"""
        self.controller.adjust_time(seconds)

    def _set_period(self, period_index):
        """Sätter period via controller"""
        self._current_period = period_index
        self.controller.set_period(period_index)
        self._refresh_period_buttons()

    # ---------------------------------------------------------
    # UI sync/update
    # ---------------------------------------------------------
    def update_from_state(self, state):
        """
        Kallas från main_window med state = controller.get_state()
        state.clock_time -> "MM:SS"
        state.clock_running -> bool
        state.period -> int
        """
        if not state:
            return

        # Tid
        self.clock_btn.config(text=f"{'STOP' if state.clock_running else 'START'}\n{state.clock_time}")

        # Knappläge
        self._clock_running = state.clock_running
        self._refresh_clock_button()

        # Period
        if state.period != self._current_period:
            self._current_period = state.period
            self._refresh_period_buttons()

    # ---------------------------------------------------------
    # UI helper
    # ---------------------------------------------------------
    def _refresh_clock_button(self):
        if self._clock_running:
            self.clock_btn.config(bg="red", fg="white", text="STOP\n" + self.clock_btn.cget("text").split("\n")[1])
        else:
            self.clock_btn.config(bg="green", fg="black", text="START\n" + self.clock_btn.cget("text").split("\n")[1])

    def _refresh_period_buttons(self):
        for idx, btn in self.period_buttons.items():
            if idx == self._current_period:
                btn.config(bg="gold")
            else:
                btn.config(bg="SystemButtonFace")
