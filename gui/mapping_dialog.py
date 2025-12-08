import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET

from scoreboard_app.core.config_loader import save_config


class MappingDialog(tk.Toplevel):
    def __init__(self, parent, cfg, client):
        super().__init__(parent)
        self.title("Mapping Configuration")

        self.parent = parent
        self.client = client
        self.cfg = cfg

        self.inputs = []
        self._load_inputs()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        # tabs
        self._build_clock_tab(nb)
        self._build_penalty_tab(nb)
        self._build_empty_goal_tab(nb)

        # SAVE + CLOSE
        bframe = tk.Frame(self)
        bframe.pack(pady=6)

        tk.Button(bframe, text="Save", command=self._save).pack(side="left", padx=4)
        tk.Button(bframe, text="Close", command=self.destroy).pack(side="left", padx=4)

    # ---------------------------------------------------
    # INPUT LIST LOADER
    # ---------------------------------------------------
    def _load_inputs(self):
        """
        Load all vMix input titles using get_status()
        """
        try:
            raw = self.client.get_status()
            xml = ET.fromstring(raw)
            titles = []

            for inp in xml.findall(".//inputs/input"):
                title = inp.get("title")
                if title:
                    titles.append(title)

            self.inputs = sorted(titles)

        except Exception as e:
            print("ERROR reading inputs:", e)
            self.inputs = []

    # ---------------------------------------------------
    # LOAD FIELDS FOR SELECTED INPUT
    # ---------------------------------------------------
    def _load_fields_for_input(self, input_name):
        """
        Returns a list of field names inside one vMix GT input
        """
        if not input_name:
            return []

        try:
            raw = self.client.get_status()
            xml = ET.fromstring(raw)

            for inp in xml.findall(".//inputs/input"):
                if inp.get("title") == input_name:
                    fields = []
                    for t in inp.findall(".//text"):
                        nm = t.get("name")
                        if nm:
                            fields.append(nm)
                    for i in inp.findall(".//image"):
                        nm = i.get("name")
                        if nm:
                            fields.append(nm)
                    return sorted(fields)

        except Exception as e:
            print("ERROR reading fields:", e)

        return []

    # ---------------------------------------------------
    # CLOCK TAB
    # ---------------------------------------------------
    def _build_clock_tab(self, nb):
        f = tk.Frame(nb)
        nb.add(f, text="Clock")

        # ensure structure
        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}
        if "clock" not in self.cfg["mapping"]:
            self.cfg["mapping"]["clock"] = {
                "input": "",
                "field": ""
            }

        m = self.cfg["mapping"]["clock"]

        tk.Label(f, text="Clock Input:").grid(row=0, column=0, sticky="w", pady=4)
        self.clock_input = tk.StringVar(value=m.get("input", ""))
        cb = ttk.Combobox(f, textvariable=self.clock_input, values=self.inputs, width=35)
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_clock_field())

        tk.Label(f, text="Clock Field:").grid(row=1, column=0, sticky="w", pady=4)
        self.clock_field = ttk.Combobox(f, width=35)
        self.clock_field.grid(row=1, column=1, sticky="w")

        # initial refresh
        self._refresh_clock_field()

    def _refresh_clock_field(self):
        input_name = self.clock_input.get()
        fields = self._load_fields_for_input(input_name)
        self.clock_field["values"] = fields

        # restore config if possible
        m = self.cfg["mapping"]["clock"]
        if m.get("field") in fields:
            self.clock_field.set(m["field"])
        else:
            self.clock_field.set("")

    # ---------------------------------------------------
    # PENALTIES TAB
    # ---------------------------------------------------
    def _build_penalty_tab(self, nb):
        f = tk.Frame(nb)
        nb.add(f, text="Penalties")

        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}
        if "penalties" not in self.cfg["mapping"]:
            self.cfg["mapping"]["penalties"] = {
                "input": "",
                "rows": {
                    "HOME1": {"time": "", "num": ""},
                    "HOME2": {"time": "", "num": ""},
                    "AWAY1": {"time": "", "num": ""},
                    "AWAY2": {"time": "", "num": ""}
                }
            }

        m = self.cfg["mapping"]["penalties"]

        tk.Label(f, text="Penalty Input:").grid(row=0, column=0, sticky="w", pady=4)
        self.pen_input = tk.StringVar(value=m.get("input", ""))
        cb = ttk.Combobox(f, textvariable=self.pen_input, values=self.inputs, width=35)
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_penalty_fields())

        # HEADER
        tk.Label(f, text="Team").grid(row=2, column=0)
        tk.Label(f, text="Time Field").grid(row=2, column=1)
        tk.Label(f, text="Nr Field").grid(row=2, column=2)

        self.pen_rows = {}

        rownames = ["HOME1", "HOME2", "AWAY1", "AWAY2"]
        for idx, name in enumerate(rownames):
            r = 3 + idx
            tk.Label(f, text=name).grid(row=r, column=0)

            tcb = ttk.Combobox(f, width=30)
            ncb = ttk.Combobox(f, width=30)

            tcb.grid(row=r, column=1)
            ncb.grid(row=r, column=2)

            self.pen_rows[name] = {
                "time": tcb,
                "num": ncb
            }

        self._refresh_penalty_fields()

    def _refresh_penalty_fields(self):
        input_name = self.pen_input.get()
        fields = self._load_fields_for_input(input_name)

        for name, row in self.pen_rows.items():
            row["time"]["values"] = fields
            row["num"]["values"] = fields

            m = self.cfg["mapping"]["penalties"]["rows"].get(name, {})
            if m.get("time") in fields:
                row["time"].set(m["time"])
            else:
                row["time"].set("")

            if m.get("num") in fields:
                row["num"].set(m["num"])
            else:
                row["num"].set("")

    # ---------------------------------------------------
    # EMPTY GOAL TAB
    # ---------------------------------------------------
    def _build_empty_goal_tab(self, nb):
        f = tk.Frame(nb)
        nb.add(f, text="Empty Goal")

        if "empty_goal" not in self.cfg["mapping"]:
            self.cfg["mapping"]["empty_goal"] = {
                "input": "",
                "home_text": "",
                "home_bg": "",
                "away_text": "",
                "away_bg": ""
            }

        m = self.cfg["mapping"]["empty_goal"]

        # INPUT
        tk.Label(f, text="Empty Goal Input:").grid(row=0, column=0, sticky="w", pady=4)
        self.eg_input = tk.StringVar(value=m.get("input", ""))
        cb = ttk.Combobox(f, textvariable=self.eg_input, values=self.inputs, width=35)
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", lambda e: self._refresh_empty_goal_fields())

        # FIELDS
        tk.Label(f, text="Team").grid(row=2, column=0)
        tk.Label(f, text="Text Field").grid(row=2, column=1)
        tk.Label(f, text="BG Field").grid(row=2, column=2)

        self.eg_home_text = ttk.Combobox(f, width=30)
        self.eg_home_bg = ttk.Combobox(f, width=30)
        self.eg_away_text = ttk.Combobox(f, width=30)
        self.eg_away_bg = ttk.Combobox(f, width=30)

        tk.Label(f, text="HOME").grid(row=3, column=0)
        self.eg_home_text.grid(row=3, column=1)
        self.eg_home_bg.grid(row=3, column=2)

        tk.Label(f, text="AWAY").grid(row=4, column=0)
        self.eg_away_text.grid(row=4, column=1)
        self.eg_away_bg.grid(row=4, column=2)

        self._refresh_empty_goal_fields()

    def _refresh_empty_goal_fields(self):
        input_name = self.eg_input.get()
        fields = self._load_fields_for_input(input_name)

        self.eg_home_text["values"] = fields
        self.eg_home_bg["values"] = fields
        self.eg_away_text["values"] = fields
        self.eg_away_bg["values"] = fields

        m = self.cfg["mapping"]["empty_goal"]

        if m.get("home_text") in fields:
            self.eg_home_text.set(m["home_text"])
        else:
            self.eg_home_text.set("")

        if m.get("home_bg") in fields:
            self.eg_home_bg.set(m["home_bg"])
        else:
            self.eg_home_bg.set("")

        if m.get("away_text") in fields:
            self.eg_away_text.set(m["away_text"])
        else:
            self.eg_away_text.set("")

        if m.get("away_bg") in fields:
            self.eg_away_bg.set(m["away_bg"])
        else:
            self.eg_away_bg.set("")

    # ---------------------------------------------------
    # SAVE
    # ---------------------------------------------------
    def _save(self):
        # CLOCK
        self.cfg["mapping"]["clock"]["input"] = self.clock_input.get()
        self.cfg["mapping"]["clock"]["field"] = self.clock_field.get()

        # PENALTIES
        pen = self.cfg["mapping"]["penalties"]
        pen["input"] = self.pen_input.get()
        for name, row in self.pen_rows.items():
            pen["rows"][name]["time"] = row["time"].get()
            pen["rows"][name]["num"] = row["num"].get()

        # EMPTY GOAL
        eg = self.cfg["mapping"]["empty_goal"]
        eg["input"] = self.eg_input.get()
        eg["home_text"] = self.eg_home_text.get()
        eg["home_bg"] = self.eg_home_bg.get()
        eg["away_text"] = self.eg_away_text.get()
        eg["away_bg"] = self.eg_away_bg.get()

        save_config(self.cfg)
        self.destroy()
