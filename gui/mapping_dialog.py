import tkinter as tk
from tkinter import ttk
from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.config.config_loader import load_config, save_config


class MappingDialog(tk.Toplevel):
    """
    Mapping configuration dialog.

    - Loads config.json on startup
    - Shows current mappings in UI
    - Any combobox change updates config dict
    - SAVE button writes immediately to JSON
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("VMix Mapping Setup")
        self.geometry("900x650")

        self.parent = parent
        self.client = VMixClient()

        # ----------------------------
        # Load config from file
        # ----------------------------
        self.cfg = load_config()  # entire system config
        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}  # safety

        # Fetch available VMIX inputs & fields
        self.client.refresh_status()
        self.inputs = self.client.list_inputs()

        # Panels / notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Create notebook pages
        self.clock_page = ttk.Frame(nb)
        self.penalty_page = ttk.Frame(nb)
        self.goal_page = ttk.Frame(nb)
        self.empty_page = ttk.Frame(nb)

        nb.add(self.clock_page, text="Clock")
        nb.add(self.penalty_page, text="Penalties")
        nb.add(self.goal_page, text="Goal Graphics")
        nb.add(self.empty_page, text="Empty Goal")

        # -------------------------
        # Build each page
        # -------------------------
        self._build_clock_page()
        self._build_penalty_page()
        self._build_goal_page()
        self._build_empty_goal_page()

        # -------------------------
        # SAVE BUTTON
        # -------------------------
        ttk.Button(self, text="SAVE & CLOSE", command=self._save_all).pack(pady=10)

    # =============================================================
    # CLOCK MAPPING PAGE
    # =============================================================
    def _build_clock_page(self):
        frm = ttk.Frame(self.clock_page)
        frm.pack(fill="x", pady=10)

        ttk.Label(frm, text="CLOCK Input").grid(row=0, column=0, sticky="w", padx=10)
        self.clock_input_cb = ttk.Combobox(frm, values=self.inputs, state="readonly", width=40)
        self.clock_input_cb.grid(row=0, column=1, padx=10)

        ttk.Label(frm, text="CLOCK Field (e.g. Time.Text)").grid(row=1, column=0, sticky="w", padx=10)
        self.clock_field_cb = ttk.Combobox(frm, state="readonly", width=40)
        self.clock_field_cb.grid(row=1, column=1, padx=10)

        # If input changes, load fields
        self.clock_input_cb.bind("<<ComboboxSelected>>", self._reload_clock_fields)

        # Load saved values
        m = self.cfg["mapping"].get("clock", {})
        if "input" in m:
            self.clock_input_cb.set(m["input"])
            self.clock_field_cb["values"] = self.client.list_title_fields(m["input"])
            if "field" in m:
                self.clock_field_cb.set(m["field"])

    def _reload_clock_fields(self, evt=None):
        inp = self.clock_input_cb.get()
        fields = self.client.list_title_fields(inp)
        self.clock_field_cb["values"] = fields

    # =============================================================
    # PENALTIES PAGE
    # =============================================================
    def _build_penalty_page(self):
        frm = ttk.Frame(self.penalty_page)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Penalty MASTER Input").grid(row=0, column=0, sticky="w", padx=10, pady=3)
        self.penalty_input_cb = ttk.Combobox(frm, values=self.inputs, state="readonly", width=40)
        self.penalty_input_cb.grid(row=0, column=1, padx=10)

        # table of 8 mappings
        self.penalty_rows = []
        ttk.Label(frm, text="Penalty Field Mappings").grid(row=1, column=0, columnspan=2, pady=5)

        for idx, label in enumerate([
            "HomeP1time", "HomeP1nr",
            "HomeP2time", "HomeP2nr",
            "AwayP1time", "AwayP1nr",
            "AwayP2time", "AwayP2nr"
        ]):
            r = ttk.Frame(frm)
            r.grid(row=idx + 2, column=0, columnspan=2, sticky="w", pady=2)
            ttk.Label(r, text=label, width=20).pack(side="left")
            cb = ttk.Combobox(r, state="readonly", width=40)
            cb.pack(side="left", padx=10)
            self.penalty_rows.append((label, cb))

        # Reload fields when master input changes
        self.penalty_input_cb.bind("<<ComboboxSelected>>", self._reload_penalty_fields)

        # Load config
        pm = self.cfg["mapping"].get("penalties", {})
        if "input" in pm:
            self.penalty_input_cb.set(pm["input"])
            fields = self.client.list_title_fields(pm["input"])
            for _, cb in self.penalty_rows:
                cb["values"] = fields

            if "fields" in pm:
                for label, cb in self.penalty_rows:
                    if label in pm["fields"]:
                        cb.set(pm["fields"][label])

    def _reload_penalty_fields(self, evt=None):
        inp = self.penalty_input_cb.get()
        fields = self.client.list_title_fields(inp)
        for _, cb in self.penalty_rows:
            cb["values"] = fields

    # =============================================================
    # GOAL GRAPHICS PAGE
    # =============================================================
    def _build_goal_page(self):
        frm = ttk.Frame(self.goal_page)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="AFTER GOAL Input").grid(row=0, column=0, sticky="w", padx=10)
        self.goal_input_cb = ttk.Combobox(frm, values=self.inputs, state="readonly", width=40)
        self.goal_input_cb.grid(row=0, column=1, padx=10)

        ttk.Label(frm, text="Home Player Name Field").grid(row=1, column=0, sticky="w", padx=10)
        self.goal_home_name_cb = ttk.Combobox(frm, state="readonly", width=40)
        self.goal_home_name_cb.grid(row=1, column=1, padx=10)

        ttk.Label(frm, text="Home Player Nr Field").grid(row=2, column=0, sticky="w", padx=10)
        self.goal_home_nr_cb = ttk.Combobox(frm, state="readonly", width=40)
        self.goal_home_nr_cb.grid(row=2, column=1, padx=10)

        ttk.Label(frm, text="Home Logo Field").grid(row=3, column=0, sticky="w", padx=10)
        self.goal_home_logo_cb = ttk.Combobox(frm, state="readonly", width=40)
        self.goal_home_logo_cb.grid(row=3, column=1, padx=10)

        ttk.Label(frm, text="Home Team Text Field").grid(row=4, column=0, sticky="w", padx=10)
        self.goal_home_team_cb = ttk.Combobox(frm, state="readonly", width=40)
        self.goal_home_team_cb.grid(row=4, column=1, padx=10)

        # When input changes, update fields
        self.goal_input_cb.bind("<<ComboboxSelected>>", self._reload_goal_fields)

        gm = self.cfg["mapping"].get("after_goal", {})
        if "input" in gm:
            self.goal_input_cb.set(gm["input"])
            fields = self.client.list_title_fields(gm["input"])
            for cb in [
                self.goal_home_name_cb,
                self.goal_home_nr_cb,
                self.goal_home_logo_cb,
                self.goal_home_team_cb
            ]:
                cb["values"] = fields

            if "home" in gm:
                if "name" in gm["home"]: self.goal_home_name_cb.set(gm["home"]["name"])
                if "nr" in gm["home"]: self.goal_home_nr_cb.set(gm["home"]["nr"])
                if "logo" in gm["home"]: self.goal_home_logo_cb.set(gm["home"]["logo"])
                if "team" in gm["home"]: self.goal_home_team_cb.set(gm["home"]["team"])

    def _reload_goal_fields(self, evt=None):
        inp = self.goal_input_cb.get()
        fields = self.client.list_title_fields(inp)
        for cb in [
            self.goal_home_name_cb,
            self.goal_home_nr_cb,
            self.goal_home_logo_cb,
            self.goal_home_team_cb
        ]:
            cb["values"] = fields

    # =============================================================
    # EMPTY GOAL PAGE
    # =============================================================
    def _build_empty_goal_page(self):
        frm = ttk.Frame(self.empty_page)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Empty Goal MASTER Input").grid(row=0, column=0, sticky="w", padx=10)
        self.empty_input_cb = ttk.Combobox(frm, values=self.inputs, state="readonly", width=40)
        self.empty_input_cb.grid(row=0, column=1, padx=10)

        ttk.Label(frm, text="Home Empty Goal Text Field").grid(row=1, column=0, sticky="w", padx=10)
        self.empty_home_text_cb = ttk.Combobox(frm, state="readonly", width=40)
        self.empty_home_text_cb.grid(row=1, column=1, padx=10)

        ttk.Label(frm, text="Away Empty Goal Text Field").grid(row=2, column=0, sticky="w", padx=10)
        self.empty_away_text_cb = ttk.Combobox(frm, state="readonly", width=40)
        self.empty_away_text_cb.grid(row=2, column=1, padx=10)

        # Field reload when input changes
        self.empty_input_cb.bind("<<ComboboxSelected>>", self._reload_empty_fields)

        em = self.cfg["mapping"].get("empty_goal", {})
        if "input" in em:
            self.empty_input_cb.set(em["input"])
            fields = self.client.list_title_fields(em["input"])
            self.empty_home_text_cb["values"] = fields
            self.empty_away_text_cb["values"] = fields

            if "home" in em:
                if "field" in em["home"]: self.empty_home_text_cb.set(em["home"]["field"])
            if "away" in em:
                if "field" in em["away"]: self.empty_away_text_cb.set(em["away"]["field"])

    def _reload_empty_fields(self, evt=None):
        inp = self.empty_input_cb.get()
        fields = self.client.list_title_fields(inp)
        self.empty_home_text_cb["values"] = fields
        self.empty_away_text_cb["values"] = fields

    # =============================================================
    # SAVE ALL MAPPINGS
    # =============================================================
    def _save_all(self):
        # CLOCK
        self.cfg["mapping"]["clock"] = {
            "input": self.clock_input_cb.get(),
            "field": self.clock_field_cb.get()
        }

        # PENALTIES
        pmap = {
            "input": self.penalty_input_cb.get(),
            "fields": {}
        }
        for label, cb in self.penalty_rows:
            val = cb.get()
            if val:  # empty means disabled
                pmap["fields"][label] = val
        self.cfg["mapping"]["penalties"] = pmap

        # AFTER GOAL
        self.cfg["mapping"]["after_goal"] = {
            "input": self.goal_input_cb.get(),
            "home": {
                "name": self.goal_home_name_cb.get(),
                "nr": self.goal_home_nr_cb.get(),
                "logo": self.goal_home_logo_cb.get(),
                "team": self.goal_home_team_cb.get()
            }
        }

        # EMPTY GOAL
        self.cfg["mapping"]["empty_goal"] = {
            "input": self.empty_input_cb.get(),
            "home": {
                "field": self.empty_home_text_cb.get()
            },
            "away": {
                "field": self.empty_away_text_cb.get()
            }
        }

        save_config(self.cfg)
        self.destroy()
