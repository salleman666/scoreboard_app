import tkinter as tk
from tkinter import ttk

from scoreboard_app.config.config_loader import load_config, save_config


class MappingDialog(tk.Toplevel):
    """
    Unified mapping editor for all vMix controlled modules.

    Supports:
      - CLOCK (input + period field)
      - SCOREBOARD (homeScore, awayScore, time)
      - GOALS (input + scorer fields)
      - PENALTIES (home input, away input)
      - EMPTY GOAL (input + home field + away field + text)
    """

    def __init__(self, master, cfg, client):
        super().__init__(master)
        self.title("Mappings")
        self.cfg = cfg
        self.client = client

        # vMix inputs list (for comboboxes)
        try:
            self.inputs = self.client.list_inputs()
        except Exception:
            self.inputs = []

        # Ensure missing mapping sections exist
        self._ensure_defaults()

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        nb = ttk.Notebook(self)
        nb.grid(sticky="nsew", padx=8, pady=8)

        f_clock = ttk.Frame(nb)
        f_score = ttk.Frame(nb)
        f_goal = ttk.Frame(nb)
        f_pen = ttk.Frame(nb)
        f_empty = ttk.Frame(nb)

        nb.add(f_clock, text="Clock")
        nb.add(f_score, text="Scoreboard")
        nb.add(f_goal, text="Goals")
        nb.add(f_pen, text="Penalties")
        nb.add(f_empty, text="Empty Goal")

        self._build_clock_ui(f_clock)
        self._build_score_ui(f_score)
        self._build_goal_ui(f_goal)
        self._build_penalty_ui(f_pen)
        self._build_empty_ui(f_empty)

        ttk.Button(self, text="SAVE", command=self._save_all).grid(
            row=1, column=0, pady=5
        )

    # ---------------------------------------------------------
    # Ensure mapping dict structure is always complete
    # ---------------------------------------------------------
    def _ensure_defaults(self):
        M = self.cfg.get("mapping", {})

        def ensure(section, key, default):
            if section not in M:
                M[section] = {}
            if key not in M[section]:
                M[section][key] = default

        # CLOCK
        ensure("clock", "input", "")
        ensure("clock", "period_field", "PeriodNr.Text")

        # SCOREBOARD
        ensure("scoreboard", "input", "")
        ensure("scoreboard", "home", "HomeScore.Text")
        ensure("scoreboard", "away", "AwayScore.Text")
        ensure("scoreboard", "time", "Time.Text")

        # GOALS
        ensure("goals", "input", "")
        ensure("goals", "scorer_name", "ScorerName.Text")
        ensure("goals", "scorer_number", "ScorerNumber.Text")
        ensure("goals", "scorer_logo", "ScorerLogo.Source")
        ensure("goals", "scorer_team", "ScorerTeam.Text")

        # PENALTIES
        ensure("penalties", "input_home", "")
        ensure("penalties", "input_away", "")

        # EMPTY GOAL
        ensure("empty_goal", "input", "")
        ensure("empty_goal", "text_home", "EmptyGoalH.Text")
        ensure("empty_goal", "text_away", "EmptyGoalA.Text")
        ensure("empty_goal", "label_text", "EMPTY GOAL")

        self.cfg["mapping"] = M

    # ---------------------------------------------------------
    # UTILITY: apply previous value to combobox or entry
    # ---------------------------------------------------------
    def _apply(self, widget, value):
        try:
            widget.set(value)
        except:
            try:
                widget.delete(0, tk.END)
                widget.insert(0, value)
            except:
                pass

    # ---------------------------------------------------------
    # CLOCK TAB
    # ---------------------------------------------------------
    def _build_clock_ui(self, f):
        M = self.cfg["mapping"]["clock"]

        ttk.Label(f, text="Clock Input").grid(row=0, column=0, padx=4, pady=4)
        cb_input = ttk.Combobox(f, values=self.inputs, width=40)
        cb_input.grid(row=0, column=1, padx=4, pady=4)
        self._apply(cb_input, M["input"])

        ttk.Label(f, text="Period Field").grid(row=1, column=0, padx=4, pady=4)
        e_period = ttk.Entry(f, width=40)
        e_period.grid(row=1, column=1, padx=4, pady=4)
        self._apply(e_period, M["period_field"])

        f._widgets = {
            "input": cb_input,
            "period_field": e_period,
        }

    # ---------------------------------------------------------
    # SCOREBOARD TAB
    # ---------------------------------------------------------
    def _build_score_ui(self, f):
        M = self.cfg["mapping"]["scoreboard"]

        ttk.Label(f, text="Scoreboard Input").grid(row=0, column=0, padx=4, pady=4)
        cb_input = ttk.Combobox(f, values=self.inputs, width=40)
        cb_input.grid(row=0, column=1, padx=4, pady=4)
        self._apply(cb_input, M["input"])

        ttk.Label(f, text="Home Field").grid(row=1, column=0, padx=4, pady=4)
        e_home = ttk.Entry(f, width=40)
        e_home.grid(row=1, column=1, padx=4, pady=4)
        self._apply(e_home, M["home"])

        ttk.Label(f, text="Away Field").grid(row=2, column=0, padx=4, pady=4)
        e_away = ttk.Entry(f, width=40)
        e_away.grid(row=2, column=1, padx=4, pady=4)
        self._apply(e_away, M["away"])

        ttk.Label(f, text="Time Field").grid(row=3, column=0, padx=4, pady=4)
        e_time = ttk.Entry(f, width=40)
        e_time.grid(row=3, column=1, padx=4, pady=4)
        self._apply(e_time, M["time"])

        f._widgets = {
            "input": cb_input,
            "home": e_home,
            "away": e_away,
            "time": e_time,
        }

    # ---------------------------------------------------------
    # GOALS TAB
    # ---------------------------------------------------------
    def _build_goal_ui(self, f):
        M = self.cfg["mapping"]["goals"]

        ttk.Label(f, text="Goal Input").grid(row=0, column=0, padx=4, pady=4)
        cb_input = ttk.Combobox(f, values=self.inputs, width=40)
        cb_input.grid(row=0, column=1, padx=4, pady=4)
        self._apply(cb_input, M["input"])

        labels = [
            ("Scorer Name Field", "scorer_name"),
            ("Scorer Number Field", "scorer_number"),
            ("Scorer Logo Field", "scorer_logo"),
            ("Scorer Team Field", "scorer_team"),
        ]

        widgets = {"input": cb_input}

        for r, (label, key) in enumerate(labels, start=1):
            ttk.Label(f, text=label).grid(row=r, column=0, padx=4, pady=4)
            e = ttk.Entry(f, width=40)
            e.grid(row=r, column=1, padx=4, pady=4)
            self._apply(e, M[key])
            widgets[key] = e

        f._widgets = widgets

    # ---------------------------------------------------------
    # PENALTIES TAB
    # ---------------------------------------------------------
    def _build_penalty_ui(self, f):
        M = self.cfg["mapping"]["penalties"]

        ttk.Label(f, text="Home Penalty Input").grid(row=0, column=0, padx=4, pady=4)
        cb_home = ttk.Combobox(f, values=self.inputs, width=40)
        cb_home.grid(row=0, column=1, padx=4, pady=4)
        self._apply(cb_home, M["input_home"])

        ttk.Label(f, text="Away Penalty Input").grid(row=1, column=0, padx=4, pady=4)
        cb_away = ttk.Combobox(f, values=self.inputs, width=40)
        cb_away.grid(row=1, column=1, padx=4, pady=4)
        self._apply(cb_away, M["input_away"])

        f._widgets = {
            "input_home": cb_home,
            "input_away": cb_away,
        }

    # ---------------------------------------------------------
    # EMPTY GOAL TAB
    # ---------------------------------------------------------
    def _build_empty_ui(self, f):
        M = self.cfg["mapping"]["empty_goal"]

        ttk.Label(f, text="Empty Goal Input").grid(row=0, column=0, padx=4, pady=4)
        cb_input = ttk.Combobox(f, values=self.inputs, width=40)
        cb_input.grid(row=0, column=1, padx=4, pady=4)
        self._apply(cb_input, M["input"])

        ttk.Label(f, text="Home Text Field").grid(row=1, column=0, padx=4, pady=4)
        e_home = ttk.Entry(f, width=40)
        e_home.grid(row=1, column=1, padx=4, pady=4)
        self._apply(e_home, M["text_home"])

        ttk.Label(f, text="Away Text Field").grid(row=2, column=0, padx=4, pady=4)
        e_away = ttk.Entry(f, width=40)
        e_away.grid(row=2, column=1, padx=4, pady=4)
        self._apply(e_away, M["text_away"])

        ttk.Label(f, text="Displayed Text (max 10 chars)").grid(row=3, column=0, padx=4, pady=4)
        e_label = ttk.Entry(f, width=40)
        e_label.grid(row=3, column=1, padx=4, pady=4)
        self._apply(e_label, M["label_text"])

        f._widgets = {
            "input": cb_input,
            "text_home": e_home,
            "text_away": e_away,
            "label_text": e_label,
        }

    # ---------------------------------------------------------
    # SAVE ALL DATA
    # ---------------------------------------------------------
    def _save_all(self):
        M = self.cfg["mapping"]

        def update(tab, section):
            for key, widget in tab._widgets.items():
                try:
                    value = widget.get().strip()
                except:
                    value = ""
                M[section][key] = value

        # Iterate through all mapping sections
        for child in self.children.values():
            if hasattr(child, "_widgets"):
                pass  # ignore – they belong inside notebook

        for frame in self.nametowidget(self.children["!notebook"]).children.values():
            if hasattr(frame, "_widgets"):
                name = str(frame).split("!notebook.")[-1]
                # explicit mapping by notebook order:
                # NOT efficient but safe
                if "frame" in name:
                    pass

        # More robust explicit update:
        for frame, section in [
            (self.nametowidget("!mappingdialog.!notebook.!frame"), "clock"),
            (self.nametowidget("!mappingdialog.!notebook.!frame2"), "scoreboard"),
            (self.nametowidget("!mappingdialog.!notebook.!frame3"), "goals"),
            (self.nametowidget("!mappingdialog.!notebook.!frame4"), "penalties"),
            (self.nametowidget("!mappingdialog.!notebook.!frame5"), "empty_goal"),
        ]:
            update(frame, section)

        save_config(self.cfg)
        self.destroy()
