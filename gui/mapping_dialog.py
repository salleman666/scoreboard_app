import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import xml.etree.ElementTree as ET


class MappingDialog(tk.Toplevel):
    """
    NEW COMPLETE MAPPING DIALOG
    - Correct Combobox field refresh
    - XML parsing for fields
    - Penalties, Shots, Empty Goal, Lineup, Goal System
    """

    def __init__(self, parent, cfg, vmix_client):
        super().__init__(parent)
        self.title("Mapping Configuration")
        self.geometry("1300x700")

        self.parent = parent
        self.cfg = cfg
        self.client = vmix_client

        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)

        self._build_penalties_tab()
        self._build_empty_goal_tab()
        self._build_shots_tab()
        self._build_lineup_tab()
        self._build_goals_tab()

        # Save / Close
        bframe = ttk.Frame(self)
        bframe.pack(pady=10)
        ttk.Button(bframe, text="Save", command=self._save).grid(row=0, column=0, padx=15)
        ttk.Button(bframe, text="Close", command=self.destroy).grid(row=0, column=1, padx=15)

    ##########################################################################
    # --- PARSE VMIX FIELDS FROM SELECTED INPUT ---
    ##########################################################################

    def _load_fields_for_input(self, input_title):
        """Return list of .Text and .Source field names for a single vMix GT input."""
        fields = []
        raw = self.client.get_status_xml()
        if not raw:
            return fields

        try:
            root = ET.fromstring(raw)
        except:
            return fields

        for inp in root.findall("./inputs/input"):
            if inp.get("title") == input_title:
                for t in inp.findall("./text"):
                    nm = t.get("name")
                    if nm:
                        fields.append(nm)
                for img in inp.findall("./image"):
                    nm = img.get("name")
                    if nm:
                        fields.append(nm)
                break

        return sorted(fields)

    ##########################################################################
    # ------------- PENALTIES TAB -------------
    ##########################################################################

    def _build_penalties_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Penalties")

        m = self.cfg["mapping"].setdefault("penalties", {})
        m.setdefault("input", "")

        for side in ["home", "away"]:
            m.setdefault(side, {})
            for slot in ["p1", "p2"]:
                m[side].setdefault(slot, {})
                for key in ["time", "time_bg", "nr", "nr_bg"]:
                    m[side][slot].setdefault(key, "")

        ttk.Label(tab, text="Penalty Input:").grid(row=0, column=0, padx=5, pady=5)
        self.pen_input_var = tk.StringVar(value=m["input"])
        self.pen_input = ttk.Combobox(tab, textvariable=self.pen_input_var,
                                      values=self.client.list_inputs())
        self.pen_input.grid(row=0, column=1, padx=5)
        self.pen_input.bind("<<ComboboxSelected>>", lambda e: self._refresh_penalty_fields())

        hdr = ["Team", "Time", "Time BG", "Nr", "Nr BG"]
        for c, t in enumerate(hdr):
            ttk.Label(tab, text=t).grid(row=1, column=c, padx=5)

        self.pen_widgets = []  # store tuples of (vars, widgets, record)

        rows = [
            ("HOME", m["home"]["p1"]),
            ("HOME", m["home"]["p2"]),
            ("AWAY", m["away"]["p1"]),
            ("AWAY", m["away"]["p2"]),
        ]

        r = 2
        for team, rec in rows:
            ttk.Label(tab, text=team).grid(row=r, column=0, padx=5)

            t_var = tk.StringVar(value=rec["time"])
            t_bg_var = tk.StringVar(value=rec["time_bg"])
            n_var = tk.StringVar(value=rec["nr"])
            n_bg_var = tk.StringVar(value=rec["nr_bg"])

            # build comboboxes
            t_box = ttk.Combobox(tab, textvariable=t_var)
            t_bg_box = ttk.Combobox(tab, textvariable=t_bg_var)
            n_box = ttk.Combobox(tab, textvariable=n_var)
            n_bg_box = ttk.Combobox(tab, textvariable=n_bg_var)

            t_box.grid(row=r, column=1, padx=5)
            t_bg_box.grid(row=r, column=2, padx=5)
            n_box.grid(row=r, column=3, padx=5)
            n_bg_box.grid(row=r, column=4, padx=5)

            self.pen_widgets.append(
                (t_var, t_box, t_bg_var, t_bg_box, n_var, n_box, n_bg_var, n_bg_box, rec)
            )
            r += 1

        self._refresh_penalty_fields()

    def _refresh_penalty_fields(self):
        input_name = self.pen_input_var.get().strip()
        if not input_name:
            return
        fields = self._load_fields_for_input(input_name)

        for (t_var, t_box, tbg_var, tbg_box, n_var, n_box, nbg_var, nbg_box, rec) in self.pen_widgets:
            t_box["values"] = fields
            tbg_box["values"] = fields
            n_box["values"] = fields
            nbg_box["values"] = fields

    ##########################################################################
    # ------------- EMPTY GOAL TAB -------------
    ##########################################################################

    def _build_empty_goal_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Empty Goal")

        m = self.cfg["mapping"].setdefault("empty_goal", {})
        m.setdefault("input", "")
        for side in ["home", "away"]:
            m.setdefault(side, {})
            for f in ["text", "bg"]:
                m[side].setdefault(f, "")

        ttk.Label(tab, text="Empty Goal Input:").grid(row=0, column=0, padx=5)
        self.eg_input_var = tk.StringVar(value=m["input"])
        self.eg_input = ttk.Combobox(tab, textvariable=self.eg_input_var,
                                    values=self.client.list_inputs())
        self.eg_input.grid(row=0, column=1, padx=5)
        self.eg_input.bind("<<ComboboxSelected>>", lambda e: self._refresh_empty_goal_fields())

        hdr = ["Team", "Text", "BG"]
        for c, t in enumerate(hdr):
            ttk.Label(tab, text=t).grid(row=1, column=c, padx=5)

        self.eg_widgets = []

        r = 2
        for team in ["HOME", "AWAY"]:
            rec = m[team.lower()]
            ttk.Label(tab, text=team).grid(row=r, column=0, padx=5)

            tv = tk.StringVar(value=rec["text"])
            bv = tk.StringVar(value=rec["bg"])

            t_box = ttk.Combobox(tab, textvariable=tv)
            b_box = ttk.Combobox(tab, textvariable=bv)

            t_box.grid(row=r, column=1, padx=5)
            b_box.grid(row=r, column=2, padx=5)

            self.eg_widgets.append((tv, t_box, bv, b_box, rec))
            r += 1

        self._refresh_empty_goal_fields()

    def _refresh_empty_goal_fields(self):
        inp = self.eg_input_var.get().strip()
        if not inp:
            return

        fields = self._load_fields_for_input(inp)

        for (tv, t_box, bv, b_box, rec) in self.eg_widgets:
            t_box["values"] = fields
            b_box["values"] = fields

    ##########################################################################
    # ------------- SHOTS TAB -------------
    ##########################################################################

    def _build_shots_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Shots")

        m = self.cfg["mapping"].setdefault("shots", {})
        m.setdefault("input", "")
        for k in ["home", "away", "background"]:
            m.setdefault(k, {})
            for f in ["value", "bg"]:
                m[k].setdefault(f, "")

        ttk.Label(tab, text="Shots Input:").grid(row=0, column=0, padx=5)
        self.sh_input_var = tk.StringVar(value=m["input"])
        self.sh_input = ttk.Combobox(tab, textvariable=self.sh_input_var,
                                    values=self.client.list_inputs())
        self.sh_input.grid(row=0, column=1, padx=5)
        self.sh_input.bind("<<ComboboxSelected>>", lambda e: self._refresh_shots_fields())

        hdr = ["Team", "Value", "BG"]
        for c, t in enumerate(hdr):
            ttk.Label(tab, text=t).grid(row=1, column=c, padx=5)

        self.sh_widgets = []

        r = 2
        for team in ["home", "away", "background"]:
            rec = m[team]
            ttk.Label(tab, text=team.upper()).grid(row=r, column=0, padx=5)

            vv = tk.StringVar(value=rec["value"])
            bv = tk.StringVar(value=rec["bg"])

            v_box = ttk.Combobox(tab, textvariable=vv)
            b_box = ttk.Combobox(tab, textvariable=bv)

            v_box.grid(row=r, column=1, padx=5)
            b_box.grid(row=r, column=2, padx=5)

            self.sh_widgets.append((vv, v_box, bv, b_box, rec))
            r += 1

        self._refresh_shots_fields()

    def _refresh_shots_fields(self):
        inp = self.sh_input_var.get().strip()
        if not inp:
            return

        fields = self._load_fields_for_input(inp)

        for (vv, v_box, bv, b_box, rec) in self.sh_widgets:
            v_box["values"] = fields
            b_box["values"] = fields

    ##########################################################################
    # ------------- LINEUP TAB -------------
    ##########################################################################

    def _build_lineup_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Lineup")

        m = self.cfg["mapping"].setdefault("lineup", {})
        m.setdefault("home_input", "")
        m.setdefault("away_input", "")

        ttk.Label(tab, text="HOME Lineup Input:").grid(row=0, column=0, padx=5)
        self.lu_home_var = tk.StringVar(value=m["home_input"])
        ttk.Combobox(tab, textvariable=self.lu_home_var,
                     values=self.client.list_inputs()).grid(row=0, column=1, padx=5)

        ttk.Label(tab, text="AWAY Lineup Input:").grid(row=1, column=0, padx=5)
        self.lu_away_var = tk.StringVar(value=m["away_input"])
        ttk.Combobox(tab, textvariable=self.lu_away_var,
                     values=self.client.list_inputs()).grid(row=1, column=1, padx=5)

    ##########################################################################
    # ------------- GOALS TAB -------------
    ##########################################################################

    def _build_goals_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Goals")

        m = self.cfg["mapping"].setdefault("goals", {})

        defaults = {
            "popup_input": "",
            "popup_overlay": 1,
            "popup_duration": 2000,
            "after_input": "",
            "after_player_name": "",
            "after_player_number": "",
            "after_team_name": "",
            "after_team_logo": "",
            "after_overlay": 1,
            "after_duration": 3000,
            "pause_between": 1000
        }
        for k, v in defaults.items():
            m.setdefault(k, v)

        # Popup mapping
        ttk.Label(tab, text="Popup Input:").grid(row=0, column=0, padx=5)
        self.gp_input_var = tk.StringVar(value=m["popup_input"])
        ttk.Combobox(tab, textvariable=self.gp_input_var,
                     values=self.client.list_inputs()).grid(row=0, column=1, padx=5)

        ttk.Label(tab, text="Popup Overlay:").grid(row=1, column=0, padx=5)
        self.gp_ol_var = tk.IntVar(value=m["popup_overlay"])
        ttk.Entry(tab, textvariable=self.gp_ol_var).grid(row=1, column=1, padx=5)

        ttk.Label(tab, text="Popup Duration (ms):").grid(row=2, column=0, padx=5)
        self.gp_dur_var = tk.IntVar(value=m["popup_duration"])
        ttk.Entry(tab, textvariable=self.gp_dur_var).grid(row=2, column=1, padx=5)

        ttk.Separator(tab).grid(row=3, column=0, columnspan=5, sticky="ew", pady=15)

        # After goal mapping
        ttk.Label(tab, text="After Goal Input:").grid(row=4, column=0, padx=5)
        self.ga_input_var = tk.StringVar(value=m["after_input"])
        ga_cb = ttk.Combobox(tab, textvariable=self.ga_input_var,
                             values=self.client.list_inputs())
        ga_cb.grid(row=4, column=1, padx=5)
        ga_cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_goal_after_fields())

        hdr = ["Player Name", "Player Nr", "Team Name", "Team Logo"]
        for c, t in enumerate(hdr):
            ttk.Label(tab, text=t).grid(row=5, column=c, padx=10)

        self.ga_name_var = tk.StringVar(value=m["after_player_name"])
        self.ga_nr_var = tk.StringVar(value=m["after_player_number"])
        self.ga_team_var = tk.StringVar(value=m["after_team_name"])
        self.ga_logo_var = tk.StringVar(value=m["after_team_logo"])

        self.ga_box_name = ttk.Combobox(tab, textvariable=self.ga_name_var)
        self.ga_box_nr = ttk.Combobox(tab, textvariable=self.ga_nr_var)
        self.ga_box_team = ttk.Combobox(tab, textvariable=self.ga_team_var)
        self.ga_box_logo = ttk.Combobox(tab, textvariable=self.ga_logo_var)

        self.ga_box_name.grid(row=6, column=0, padx=5)
        self.ga_box_nr.grid(row=6, column=1, padx=5)
        self.ga_box_team.grid(row=6, column=2, padx=5)
        self.ga_box_logo.grid(row=6, column=3, padx=5)

        ttk.Label(tab, text="After Overlay:").grid(row=7, column=0, padx=5)
        self.ga_ol_var = tk.IntVar(value=m["after_overlay"])
        ttk.Entry(tab, textvariable=self.ga_ol_var).grid(row=7, column=1, padx=5)

        ttk.Label(tab, text="After Duration (ms):").grid(row=8, column=0, padx=5)
        self.ga_dur_var = tk.IntVar(value=m["after_duration"])
        ttk.Entry(tab, textvariable=self.ga_dur_var).grid(row=8, column=1, padx=5)

        ttk.Label(tab, text="Pause Between Inputs (ms):").grid(row=9, column=0, padx=5)
        self.ga_pause_var = tk.IntVar(value=m["pause_between"])
        ttk.Entry(tab, textvariable=self.ga_pause_var).grid(row=9, column=1, padx=5)

        self._refresh_goal_after_fields()

    def _refresh_goal_after_fields(self):
        inp = self.ga_input_var.get().strip()
        if not inp:
            return

        fields = self._load_fields_for_input(inp)

        self.ga_box_name["values"] = fields
        self.ga_box_nr["values"] = fields
        self.ga_box_team["values"] = fields
        self.ga_box_logo["values"] = fields

    ##########################################################################
    # ---------------- SAVE ----------------
    ##########################################################################

    def _save(self):
        m = self.cfg["mapping"]

        # penalties
        pm = m["penalties"]
        pm["input"] = self.pen_input_var.get()
        for (t_var, t_box, tbg_var, tbg_box, n_var, n_box, nbg_var, nbg_box, rec) in self.pen_widgets:
            rec["time"] = t_var.get()
            rec["time_bg"] = tbg_var.get()
            rec["nr"] = n_var.get()
            rec["nr_bg"] = nbg_var.get()

        # empty goal
        eg = m["empty_goal"]
        eg["input"] = self.eg_input_var.get()
        for (tv, t_box, bv, b_box, rec) in self.eg_widgets:
            rec["text"] = tv.get()
            rec["bg"] = bv.get()

        # shots
        sh = m["shots"]
        sh["input"] = self.sh_input_var.get()
        for (vv, v_box, bv, b_box, rec) in self.sh_widgets:
            rec["value"] = vv.get()
            rec["bg"] = bv.get()

        # lineup
        lu = m["lineup"]
        lu["home_input"] = self.lu_home_var.get()
        lu["away_input"] = self.lu_away_var.get()

        # goals
        g = m["goals"]
        g["popup_input"] = self.gp_input_var.get()
        g["popup_overlay"] = self.gp_ol_var.get()
        g["popup_duration"] = self.gp_dur_var.get()
        g["after_input"] = self.ga_input_var.get()
        g["after_player_name"] = self.ga_name_var.get()
        g["after_player_number"] = self.ga_nr_var.get()
        g["after_team_name"] = self.ga_team_var.get()
        g["after_team_logo"] = self.ga_logo_var.get()
        g["after_overlay"] = self.ga_ol_var.get()
        g["after_duration"] = self.ga_dur_var.get()
        g["pause_between"] = self.ga_pause_var.get()

        self.parent.save_config()
        self.destroy()
