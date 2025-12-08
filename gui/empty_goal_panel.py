import tkinter as tk
from tkinter import ttk
from scoreboard_app.config.config_loader import save_config

class EmptyGoalPanel(ttk.Frame):

    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.cfg = controller.cfg

        # ensure mapping structure exists
        if "empty_goal" not in self.cfg["mapping"]:
            self.cfg["mapping"]["empty_goal"] = {
                "home_input": "",
                "away_input": "",
                "home_text_field": "",
                "away_text_field": "",
                "home_bg_field": "",
                "away_bg_field": "",
                "override_text": ""  # max 10 chars if used
            }
            save_config(self.cfg)

        self.mapping = self.cfg["mapping"]["empty_goal"]
        self._build_gui()

    def _build_gui(self):

        # --- HOME side ---
        home_frame = ttk.LabelFrame(self, text="HOME Empty Goal")
        home_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        ttk.Label(home_frame, text="Input").grid(row=0, column=0, sticky="w")
        self.home_input_var = tk.StringVar(value=self.mapping.get("home_input", ""))
        ttk.Entry(home_frame, textvariable=self.home_input_var).grid(row=0, column=1)

        ttk.Label(home_frame, text="TEXT Field").grid(row=1, column=0, sticky="w")
        self.home_text_var = tk.StringVar(value=self.mapping.get("home_text_field", ""))
        ttk.Entry(home_frame, textvariable=self.home_text_var).grid(row=1, column=1)

        ttk.Label(home_frame, text="BG Field").grid(row=2, column=0, sticky="w")
        self.home_bg_var = tk.StringVar(value=self.mapping.get("home_bg_field", ""))
        ttk.Entry(home_frame, textvariable=self.home_bg_var).grid(row=2, column=1)


        # --- AWAY side ---
        away_frame = ttk.LabelFrame(self, text="AWAY Empty Goal")
        away_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Label(away_frame, text="Input").grid(row=0, column=0, sticky="w")
        self.away_input_var = tk.StringVar(value=self.mapping.get("away_input", ""))
        ttk.Entry(away_frame, textvariable=self.away_input_var).grid(row=0, column=1)

        ttk.Label(away_frame, text="TEXT Field").grid(row=1, column=0, sticky="w")
        self.away_text_var = tk.StringVar(value=self.mapping.get("away_text_field", ""))
        ttk.Entry(away_frame, textvariable=self.away_text_var).grid(row=1, column=1)

        ttk.Label(away_frame, text="BG Field").grid(row=2, column=0, sticky="w")
        self.away_bg_var = tk.StringVar(value=self.mapping.get("away_bg_field", ""))
        ttk.Entry(away_frame, textvariable=self.away_bg_var).grid(row=2, column=1)


        # --- OVERRIDE TEXT (Applied to BOTH) ---
        override_frame = ttk.LabelFrame(self, text="Override Text (affects BOTH)")
        override_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        ttk.Label(override_frame, text="Override Text (max 10 chars):").grid(row=0, column=0)
        self.override_text_var = tk.StringVar(value=self.mapping.get("override_text", ""))
        ttk.Entry(override_frame, textvariable=self.override_text_var).grid(row=0, column=1)

        # --- SAVE BUTTON ---
        btn = ttk.Button(self, text="Save Mapping", command=self._save)
        btn.grid(row=2, column=0, columnspan=2, pady=10)

    def _save(self):
        self.mapping["home_input"] = self.home_input_var.get()
        self.mapping["away_input"] = self.away_input_var.get()
        self.mapping["home_text_field"] = self.home_text_var.get()
        self.mapping["away_text_field"] = self.away_text_var.get()
        self.mapping["home_bg_field"] = self.home_bg_var.get()
        self.mapping["away_bg_field"] = self.away_bg_var.get()
        self.mapping["override_text"] = self.override_text_var.get()[:10]  # enforce <= 10 chars

        save_config(self.cfg)

        print("[EMPTY GOAL] Mapping saved.")
