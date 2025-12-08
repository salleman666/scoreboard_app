import tkinter as tk
from tkinter import ttk
from scoreboard_app.config.config_loader import save_config, load_config
from scoreboard_app.core.vmix_client import VMixClient


class MappingDialog(tk.Toplevel):
    def __init__(self, parent, cfg: dict, client: VMixClient):
        super().__init__(parent)
        self.parent = parent
        self.client = client
        self.cfg = cfg

        self.title("vMix Mapping Configuration")
        self.geometry("1100x600")

        # ensure mapping structure exists
        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # build all tabs
        self._build_clock_tab()
        self._build_penalty_tab()
        self._build_goal_tab()
        self._build_empty_goal_tab()

        # bottom save button
        ttk.Button(self, text="SAVE ALL", command=self._save_all).pack(pady=10)

    # =============================================
    #                CLOCK TAB
    # =============================================
    def _build_clock_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="CLOCK")

        inner = ttk.Frame(tab)
        inner.pack(fill="x", padx=20, pady=20)

        inputs = self.client.list_inputs()

        m = self.cfg["mapping"].get("clock", {})
        clock_input = m.get("input", "")
        clock_field = m.get("field", "")

        ttk.Label(inner, text="Clock Input:").grid(row=0, column=0, padx=10, pady=5)
        self.clock_input_var = tk.StringVar(value=clock_input)
        cb1 = ttk.Combobox(inner, textvariable=self.clock_input_var, values=inputs, state="readonly")
        cb1.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(inner, text="Clock Field:").grid(row=1, column=0, padx=10, pady=5)
        self.clock_field_var = tk.StringVar(value=clock_field)
        cb2 = ttk.Combobox(inner, textvariable=self.clock_field_var,
                           values=self._list_fields(clock_input), state="readonly")
        cb2.grid(row=1, column=1, padx=10, pady=5)

        # update fields when input changes
        def refresh_clock_fields(e):
            fields = self._list_fields(self.clock_input_var.get())
            cb2["values"] = fields

        cb1.bind("<<ComboboxSelected>>", refresh_clock_fields)

    # =============================================
    #                PENALTY TAB
    # =============================================
    def _build_penalty_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="PENALTIES")

        inputs = self.client.list_inputs()

        current = self.cfg["mapping"].get("penalties", {})
        current_input = current.get("input", "")

        ttk.Label(tab, text="Penalty Input").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.pen_input_var = tk.StringVar(value=current_input)
        pen_cb = ttk.Combobox(tab, textvariable=self.pen_input_var, values=inputs, state="readonly")
        pen_cb.grid(row=0, column=1, padx=10)

        # TABLE SLOTS
        slots = ["HOME P1", "HOME P2", "AWAY P1", "AWAY P2"]
        self.pen_rows = []

        frame = ttk.Frame(tab)
        frame.grid(row=1, column=0, columnspan=8, padx=20, pady=20)

        headers = ["Slot", "Time Field", "Number Field", "BG Time", "BG Number"]
        for idx, h in enumerate(headers):
            ttk.Label(frame, text=h).grid(row=0, column=idx, padx=10, pady=5)

        for r, slot in enumerate(slots, start=1):
            stored = current.get(slot, {})
            time_val = stored.get("time", "")
            num_val = stored.get("number", "")
            bg_t = stored.get("bg_time", "")
            bg_n = stored.get("bg_number", "")

            slot_label = ttk.Label(frame, text=slot)
            slot_label.grid(row=r, column=0, padx=5)

            time_var = tk.StringVar(value=time_val)
            num_var = tk.StringVar(value=num_val)
            bg_t_var = tk.StringVar(value=bg_t)
            bg_n_var = tk.StringVar(value=bg_n)

            row_info = {
                "slot": slot,
                "time_var": time_var,
                "num_var": num_var,
                "bg_t_var": bg_t_var,
                "bg_n_var": bg_n_var,
            }
            self.pen_rows.append(row_info)

            cbA = ttk.Combobox(frame, textvariable=time_var, state="readonly")
            cbA.grid(row=r, column=1, padx=5)

            cbB = ttk.Combobox(frame, textvariable=num_var, state="readonly")
            cbB.grid(row=r, column=2, padx=5)

            cbC = ttk.Combobox(frame, textvariable=bg_t_var, state="readonly")
            cbC.grid(row=r, column=3, padx=5)

            cbD = ttk.Combobox(frame, textvariable=bg_n_var, state="readonly")
            cbD.grid(row=r, column=4, padx=5)

            row_info["cbA"] = cbA
            row_info["cbB"] = cbB
            row_info["cbC"] = cbC
            row_info["cbD"] = cbD

        def refresh_rows(e):
            fields = self._list_fields(self.pen_input_var.get())
            for row in self.pen_rows:
                row["cbA"]["values"] = fields
                row["cbB"]["values"] = fields
                row["cbC"]["values"] = fields
                row["cbD"]["values"] = fields

        pen_cb.bind("<<ComboboxSelected>>", refresh_rows)

        # initialize now:
        refresh_rows(None)

    # =============================================
    #                GOALS TAB
    # =============================================
    def _build_goal_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="GOALS")

        inputs = self.client.list_inputs()
        current = self.cfg["mapping"].get("goals", {})
        popup = current.get("popup", {})
        after = current.get("after", {})

        # POPUP AREA
        ttk.Label(tab, text="GOAL POPUP Input").grid(row=0, column=0, padx=10, pady=10)
        self.popup_input_var = tk.StringVar(value=popup.get("input", ""))
        cb1 = ttk.Combobox(tab, textvariable=self.popup_input_var, values=inputs, state="readonly")
        cb1.grid(row=0, column=1, padx=10)

        ttk.Label(tab, text="Overlay (1–8):").grid(row=1, column=0, padx=10)
        self.popup_overlay_var = tk.StringVar(value=str(popup.get("overlay", "")))
        ttk.Entry(tab, textvariable=self.popup_overlay_var).grid(row=1, column=1, padx=10)

        ttk.Label(tab, text="Duration ms:").grid(row=2, column=0, padx=10)
        self.popup_dur_var = tk.StringVar(value=str(popup.get("duration", "")))
        ttk.Entry(tab, textvariable=self.popup_dur_var).grid(row=2, column=1, padx=10)

        # AFTER-GOAL AREA
        ttk.Label(tab, text="AFTER GOAL Input").grid(row=3, column=0, padx=10, pady=25)
        self.after_input_var = tk.StringVar(value=after.get("input", ""))
        cbA = ttk.Combobox(tab, textvariable=self.after_input_var, values=inputs, state="readonly")
        cbA.grid(row=3, column=1, padx=10)

        ttk.Label(tab, text="Overlay (1–8):").grid(row=4, column=0, padx=10)
        self.after_overlay_var = tk.StringVar(value=str(after.get("overlay", "")))
        ttk.Entry(tab, textvariable=self.after_overlay_var).grid(row=4, column=1, padx=10)

        ttk.Label(tab, text="Duration ms:").grid(row=5, column=0, padx=10)
        self.after_dur_var = tk.StringVar(value=str(after.get("duration", "")))
        ttk.Entry(tab, textvariable=self.after_dur_var).grid(row=5, column=1, padx=10)

        ttk.Label(tab, text="Pause Between Popup/After ms:").grid(row=6, column=0, padx=10)
        self.after_pause_var = tk.StringVar(value=str(after.get("pause_between", "")))
        ttk.Entry(tab, textvariable=self.after_pause_var).grid(row=6, column=1, padx=10)

    # =============================================
    #                EMPTY GOAL TAB
    # =============================================
    def _build_empty_goal_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="EMPTY GOAL")

        inputs = self.client.list_inputs()
        current = self.cfg["mapping"].get("empty_goal", {})

        input_name = current.get("input", "")
        text_field = current.get("text", "")
        bg_field = current.get("bg", "")
        override_text = current.get("override_text", "")
