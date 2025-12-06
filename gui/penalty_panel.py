import tkinter as tk
from tkinter import ttk

class PenaltyPanel(tk.Frame):
    """
    Automatically builds a penalty status GUI based on vmix_config.json mapping.
    Supports home/away, 2 slots each.
    """

    REFRESH_MS = 500

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.cfg = controller.cfg
        self.mapping = self.cfg["mapping"]["penalties"]

        self.rows = {}  # track widgets for live updates

        self._build_layout()
        self.after(self.REFRESH_MS, self._refresh_loop)

    # --------------------------------------------------------------------

    def _build_layout(self):
        """
        Build UI dynamically using JSON mapping.
        """

        ttk.Label(self, text="🏒 PENALTIES", font=("Segoe UI", 14, "bold"))\
            .grid(row=0, column=0, columnspan=4, pady=5)

        row_index = 1

        for team in ["home", "away"]:
            for slot in ["p1", "p2"]:

                # Extract GUI fields
                name = f"{team.upper()} {slot.upper()}"
                data = self.mapping[team][slot]

                row_widgets = {}

                ttk.Label(self, text=name, width=12)\
                    .grid(row=row_index, column=0, padx=3)

                # Time label
                time_var = tk.StringVar()
                ttk.Label(self, textvariable=time_var, width=10)\
                    .grid(row=row_index, column=1, padx=3)
                row_widgets["time"] = time_var

                # Number label
                num_var = tk.StringVar()
                ttk.Label(self, textvariable=num_var, width=5)\
                    .grid(row=row_index, column=2, padx=3)
                row_widgets["number"] = num_var

                # Adjust buttons
                ttk.Button(self, text="+10",
                           command=lambda t=team, s=slot: self.controller.adjust_penalty(t, s, +10)
                           ).grid(row=row_index, column=3)

                ttk.Button(self, text="-10",
                           command=lambda t=team, s=slot: self.controller.adjust_penalty(t, s, -10)
                           ).grid(row=row_index, column=4)

                ttk.Button(self, text="CLEAR",
                           command=lambda t=team, s=slot: self.controller.clear_penalty(t, s)
                           ).grid(row=row_index, column=5)

                # Store update targets
                self.rows[(team, slot)] = row_widgets

                row_index += 1

    # --------------------------------------------------------------------

    def _refresh_loop(self):
        """
        Poll controller and update values.
        """

        try:
            status = self.controller.get_penalties()
            # Expected:
            # {
            #   "home": {"p1":{"number":..., "time":...}, "p2"...},
            #   "away": {...}
            # }
            for (team, slot), widgets in self.rows.items():
                pdata = status[team][slot]
                widgets["time"].set(pdata.get("time", ""))
                widgets["number"].set(pdata.get("number", ""))
        except Exception as e:
            print("[PenaltyPanel] refresh error:", e)

        self.after(self.REFRESH_MS, self._refresh_loop)
