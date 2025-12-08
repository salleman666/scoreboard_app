import tkinter as tk
from tkinter import ttk, Toplevel
from tkinter import messagebox

from scoreboard_app.core.vmix_client import VMixClient
from scoreboard_app.core.config_loader import save_config


class MappingDialog(Toplevel):
    """
    FULL REBUILD OF MAPPING DIALOG
    - Penalty mappings: 4 slots (Home1, Home2, Away1, Away2)
    - Each slot has 4 filtered dropdowns:
        time.Text, bg.Source, nr.Text, bgnr.Source
    - Empty Goal block (text + bg)
    - Shots block (home nr, away nr, bg)
    - Lineup block (home input, away input only)
    - Goal Popup & After Goal block (inputs, overlay, duration)
    - save + load supported
    """

    def __init__(self, parent, cfg, client: VMixClient):
        super().__init__(parent)
        self.title("Mapping Configuration")
        self.geometry("1000x700")

        self.parent = parent
        self.cfg = cfg
        self.client = client

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self._build_penalties_tab()
        self._build_emptygoal_tab()
        self._build_shots_tab()
        self._build_lineup_tab()
        self._build_goal_tab()

        # Save button
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="SAVE", command=self._save).pack(side="right")

    # ------------- SHARED HELPERS -----------------

    def _safe_get_mapping(self, section):
        """
        Ensure mapping structure exists
        """
        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}
        if section not in self.cfg["mapping"]:
            self.cfg["mapping"][section] = {}
        return self.cfg["mapping"][section]

    def _load_inputs(self):
        try:
            return self.client.list_inputs()
        except:
            return []

    def _load_fields(self, input_name):
        """
        Return all title fields from vMix for given input
        """
        try:
            return self.client.list_title_fields(input_name)
        except:
            return []

    # ----------------- PENALTIES TAB --------------------

    def _build_penalties_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Penalties")

        m = self._safe_get_mapping("penalties")

        # If structure missing, initialize
        default_slots = ["home1", "home2", "away1", "away2"]
        for k in default_slots:
            if k not in m:
                m[k] = {
                    "time": "",
                    "time_bg": "",
                    "nr": "",
                    "nr_bg": ""
                }

        # UI
        top_row = tk.Frame(tab)
        top_row.pack(fill="x", pady=5)

        tk.Label(top_row, text="Penalty Input:").pack(side="left")

        inputs = self._load_inputs()
        self.pen_input_var = tk.StringVar(value=m.get("input", ""))
        self.pen_input_cb = ttk.Combobox(top_row, textvariable=self.pen_input_var, values=inputs, width=40)
        self.pen_input_cb.pack(side="left", padx=8)
        self.pen_input_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_penalty_rows())

        # Table headers
        hdr = tk.Frame(tab)
        hdr.pack(fill="x", pady=4)
        labels = ["SLOT", "Time.Text", "Time BG", "Nr.Text", "Nr BG"]
        for idx, t in enumerate(labels):
            tk.Label(hdr, text=t, width=20, anchor="w").grid(row=0, column=idx, padx=4)

        # Build rows
        self.penalty_rows = {}  # store references

        def make_row(row_index, slotname, initial):
            container = tk.Frame(tab)
            container.pack(fill="x", pady=2)

            tk.Label(container, text=slotname.upper(), width=20, anchor="w").grid(row=0, column=0, padx=4)

            # 4 columns
            v_time = tk.StringVar(value=initial["time"])
            v_timebg = tk.StringVar(value=initial["time_bg"])
            v_nr = tk.StringVar(value=initial["nr"])
            v_nrbg = tk.StringVar(value=initial["nr_bg"])

            cb1 = ttk.Combobox(container, textvariable=v_time, width=20)
            cb2 = ttk.Combobox(container, textvariable=v_timebg, width=20)
            cb3 = ttk.Combobox(container, textvariable=v_nr, width=20)
            cb4 = ttk.Combobox(container, textvariable=v_nrbg, width=20)

            cb1.grid(row=0, column=1, padx=4)
            cb2.grid(row=0, column=2, padx=4)
            cb3.grid(row=0, column=3, padx=4)
            cb4.grid(row=0, column=4, padx=4)

            # store
            self.penalty_rows[slotname] = {
                "v_time": v_time,
                "v_timebg": v_timebg,
                "v_nr": v_nr,
                "v_nrbg": v_nrbg,
                "cb_time": cb1,
                "cb_timebg": cb2,
                "cb_nr": cb3,
                "cb_nrbg": cb4
            }

        make_row(1, "home1", m["home1"])
        make_row(2, "home2", m["home2"])
        make_row(3, "away1", m["away1"])
        make_row(4, "away2", m["away2"])

        # initial fill
        self._refresh_penalty_rows()

    def _refresh_penalty_rows(self):
        name = self.pen_input_var.get().strip()
        if not name:
            return
        fields = self._load_fields(name)

        # Filter
        time_list = [f for f in fields if f.lower().endswith("time.text")]
        timebg_list = [f for f in fields if f.lower().endswith("bg.source")]
        nr_list = [f for f in fields if f.lower().endswith("nr.text")]
        nrbg_list = [f for f in fields if f.lower().endswith("bgnr.source")]

        for slot, row in self.penalty_rows.items():
            row["cb_time"]["values"] = time_list
            row["cb_timebg"]["values"] = timebg_list
            row["cb_nr"]["values"] = nr_list
            row["cb_nrbg"]["values"] = nrbg_list

    # ---------------- EMPTY GOAL TAB --------------------

    def _build_emptygoal_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Empty Goal")

        m = self._safe_get_mapping("emptygoal")
        if "input" not in m:
            m["input"] = ""
        if "text_field" not in m:
            m["text_field"] = ""
        if "bg_field" not in m:
            m["bg_field"] = ""

        inputs = self._load_inputs()

        row = tk.Frame(tab)
        row.pack(fill="x", pady=8)
        tk.Label(row, text="Input:").pack(side="left")
        self.eg_input_var = tk.StringVar(value=m["input"])
        self.eg_input_cb = ttk.Combobox(row, textvariable=self.eg_input_var, values=inputs, width=40)
        self.eg_input_cb.pack(side="left", padx=6)
        self.eg_input_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_emptygoal_fields())

        hdr = tk.Frame(tab)
        hdr.pack(fill="x", pady=4)
        tk.Label(hdr, text="Text Field", width=30).grid(row=0, column=0)
        tk.Label(hdr, text="BG Field", width=30).grid(row=0, column=1)

        row2 = tk.Frame(tab)
        row2.pack(fill="x", pady=4)

        self.eg_text_var = tk.StringVar(value=m["text_field"])
        self.eg_bg_var = tk.StringVar(value=m["bg_field"])

        self.eg_text_cb = ttk.Combobox(row2, textvariable=self.eg_text_var, width=30)
        self.eg_bg_cb = ttk.Combobox(row2, textvariable=self.eg_bg_var, width=30)

        self.eg_text_cb.grid(row=0, column=0, padx=4)
        self.eg_bg_cb.grid(row=0, column=1, padx=4)

        self._refresh_emptygoal_fields()

    def _refresh_emptygoal_fields(self):
        name = self.eg_input_var.get().strip()
        if not name:
            return
        f = self._load_fields(name)
        txt = [x for x in f if x.lower().endswith("text")]
        bg = [x for x in f if x.lower().endswith("bg.source")]

        self.eg_text_cb["values"] = txt
        self.eg_bg_cb["values"] = bg

    # ----------------- SHOTS TAB --------------------

    def _build_shots_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Shots")

        m = self._safe_get_mapping("shots")
        if "input" not in m:
            m["input"] = ""
        if "home_nr" not in m:
            m["home_nr"] = ""
        if "away_nr" not in m:
            m["away_nr"] = ""
        if "bg_field" not in m:
            m["bg_field"] = ""

        inputs = self._load_inputs()

        row = tk.Frame(tab)
        row.pack(fill="x", pady=8)
        tk.Label(row, text="Input:").pack(side="left")
        self.sh_input_var = tk.StringVar(value=m["input"])
        self.sh_input_cb = ttk.Combobox(row, textvariable=self.sh_input_var, values=inputs, width=40)
        self.sh_input_cb.pack(side="left", padx=6)
        self.sh_input_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_shots_fields())

        hdr = tk.Frame(tab)
        hdr.pack(fill="x", pady=4)
        for i, t in enumerate(["HOME Nr", "AWAY Nr", "BG"]):
            tk.Label(hdr, text=t, width=25).grid(row=0, column=i)

        row2 = tk.Frame(tab)
        row2.pack(fill="x", pady=4)

        self.sh_home_var = tk.StringVar(value=m["home_nr"])
        self.sh_away_var = tk.StringVar(value=m["away_nr"])
        self.sh_bg_var = tk.StringVar(value=m["bg_field"])

        self.sh_home_cb = ttk.Combobox(row2, textvariable=self.sh_home_var, width=25)
        self.sh_away_cb = ttk.Combobox(row2, textvariable=self.sh_away_var, width=25)
        self.sh_bg_cb = ttk.Combobox(row2, textvariable=self.sh_bg_var, width=25)

        self.sh_home_cb.grid(row=0, column=0, padx=4)
        self.sh_away_cb.grid(row=0, column=1, padx=4)
        self.sh_bg_cb.grid(row=0, column=2, padx=4)

        self._refresh_shots_fields()

    def _refresh_shots_fields(self):
        name = self.sh_input_var.get().strip()
        if not name:
            return
        f = self._load_fields(name)

        nr_fields = [x for x in f if x.lower().endswith("nr.text")]
        bg_fields = [x for x in f if x.lower().endswith("bg.source")]

        self.sh_home_cb["values"] = nr_fields
        self.sh_away_cb["values"] = nr_fields
        self.sh_bg_cb["values"] = bg_fields

    # ----------------- LINEUP TAB --------------------

    def _build_lineup_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Lineup")

        m = self._safe_get_mapping("lineup")

        if "home_input" not in m:
            m["home_input"] = ""
        if "away_input" not in m:
            m["away_input"] = ""

        inputs = self._load_inputs()

        tk.Label(tab, text="HOME Input:").pack(anchor="w", pady=4)
        self.lu_home_var = tk.StringVar(value=m["home_input"])
        self.lu_home_cb = ttk.Combobox(tab, textvariable=self.lu_home_var, values=inputs, width=60)
        self.lu_home_cb.pack(anchor="w")

        tk.Label(tab, text="AWAY Input:").pack(anchor="w", pady=10)
        self.lu_away_var = tk.StringVar(value=m["away_input"])
        self.lu_away_cb = ttk.Combobox(tab, textvariable=self.lu_away_var, values=inputs, width=60)
        self.lu_away_cb.pack(anchor="w")

    # ----------------- GOAL TAB --------------------

    def _build_goal_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Goals")

        m = self._safe_get_mapping("goal")

        for key in ["popup_input", "popup_overlay", "popup_duration",
                    "after_input", "after_overlay", "after_duration",
                    "pause_between"]:
            if key not in m:
                m[key] = ""

        inputs = self._load_inputs()

        # POPUP
        tk.Label(tab, text="GOAL POPUP Input:").pack(anchor="w", pady=4)
        self.gp_input_var = tk.StringVar(value=m["popup_input"])
        self.gp_input_cb = ttk.Combobox(tab, textvariable=self.gp_input_var, values=inputs, width=60)
        self.gp_input_cb.pack(anchor="w")

        tk.Label(tab, text="Overlay (1-8):").pack(anchor="w")
        self.gp_ov_var = tk.StringVar(value=m["popup_overlay"])
        self.gp_ov_entry = tk.Entry(tab, textvariable=self.gp_ov_var, width=10)
        self.gp_ov_entry.pack(anchor="w")

        tk.Label(tab, text="Duration ms:").pack(anchor="w")
        self.gp_dur_var = tk.StringVar(value=m["popup_duration"])
        self.gp_dur_entry = tk.Entry(tab, textvariable=self.gp_dur_var, width=10)
        self.gp_dur_entry.pack(anchor="w")

        # AFTER GOAL
        tk.Label(tab, text="AFTER GOAL Input:").pack(anchor="w", pady=18)
        self.ga_input_var = tk.StringVar(value=m["after_input"])
        self.ga_input_cb = ttk.Combobox(tab, textvariable=self.ga_input_var, values=inputs, width=60)
        self.ga_input_cb.pack(anchor="w")

        tk.Label(tab, text="Overlay (1-8):").pack(anchor="w")
        self.ga_ov_var = tk.StringVar(value=m["after_overlay"])
        self.ga_ov_entry = tk.Entry(tab, textvariable=self.ga_ov_var, width=10)
        self.ga_ov_entry.pack(anchor="w")

        tk.Label(tab, text="Duration ms:").pack(anchor="w")
        self.ga_dur_var = tk.StringVar(value=m["after_duration"])
        self.ga_dur_entry = tk.Entry(tab, textvariable=self.ga_dur_var, width=10)
        self.ga_dur_entry.pack(anchor="w")

        # PAUSE
        tk.Label(tab, text="Pause Between Popup/After ms:").pack(anchor="w", pady=18)
        self.ga_pause_var = tk.StringVar(value=m["pause_between"])
        self.ga_pause_entry = tk.Entry(tab, textvariable=self.ga_pause_var, width=10)
        self.ga_pause_entry.pack(anchor="w")

    # ---------------- SAVE --------------------

    def _save(self):
        # Penalties
        mp = self._safe_get_mapping("penalties")
        mp["input"] = self.pen_input_var.get().strip()

        for slot, row in self.penalty_rows.items():
            mp[slot]["time"] = row["v_time"].get().strip()
            mp[slot]["time_bg"] = row["v_timebg"].get().strip()
            mp[slot]["nr"] = row["v_nr"].get().strip()
            mp[slot]["nr_bg"] = row["v_nrbg"].get().strip()

        # Empty goal
        mg = self._safe_get_mapping("emptygoal")
        mg["input"] = self.eg_input_var.get().strip()
        mg["text_field"] = self.eg_text_var.get().strip()
        mg["bg_field"] = self.eg_bg_var.get().strip()

        # Shots
        ms = self._safe_get_mapping("shots")
        ms["input"] = self.sh_input_var.get().strip()
        ms["home_nr"] = self.sh_home_var.get().strip()
        ms["away_nr"] = self.sh_away_var.get().strip()
        ms["bg_field"] = self.sh_bg_var.get().strip()

        # Lineup
        ml = self._safe_get_mapping("lineup")
        ml["home_input"] = self.lu_home_var.get().strip()
        ml["away_input"] = self.lu_away_var.get().strip()

        # Goals
        mg2 = self._safe_get_mapping("goal")
        mg2["popup_input"] = self.gp_input_var.get().strip()
        mg2["popup_overlay"] = self.gp_ov_var.get().strip()
        mg2["popup_duration"] = self.gp_dur_var.get().strip()

        mg2["after_input"] = self.ga_input_var.get().strip()
        mg2["after_overlay"] = self.ga_ov_var.get().strip()
        mg2["after_duration"] = self.ga_dur_var.get().strip()

        mg2["pause_between"] = self.ga_pause_var.get().strip()

        # write to disk
        save_config(self.cfg)

        messagebox.showinfo("OK", "Mapping saved.")
        self.destroy()
