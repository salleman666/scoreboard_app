import tkinter as tk
from tkinter import ttk
from scoreboard_app.config.config_loader import load_config, save_config
from scoreboard_app.gui.mapping_dialog import MappingDialog


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, cfg, client):
        super().__init__(parent)
        self.parent = parent
        self.cfg = cfg
        self.client = client

        self.title("Settings")
        self.geometry("400x200")

        # ======================
        # ALWAYS FIX STRUCTURE BEFORE UI
        # ======================
        self._ensure_global_mapping()

        ttk.Button(self, text="Open Mapping", command=self._open_mapping).pack(pady=15)
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=15)

    # ==================================================
    # CREATE STRUCTURE IF MISSING OR INVALID
    # ==================================================
    def _ensure_global_mapping(self):

        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}

        m = self.cfg["mapping"]

        # CLOCK
        if "clock" not in m or not isinstance(m["clock"], dict):
            m["clock"] = {"input": None, "time": None, "period": None}

        # PENALTIES
        if "penalties" not in m or not isinstance(m["penalties"], dict):
            m["penalties"] = {
                "input": None,
                "home": {"p1_time": None, "p1_nr": None, "p2_time": None, "p2_nr": None},
                "away": {"p1_time": None, "p1_nr": None, "p2_time": None, "p2_nr": None},
            }
        else:
            # BAD TYPE FIXER – list → dict
            if not isinstance(m["penalties"], dict):
                m["penalties"] = {
                    "input": None,
                    "home": {"p1_time": None, "p1_nr": None, "p2_time": None, "p2_nr": None},
                    "away": {"p1_time": None, "p1_nr": None, "p2_time": None, "p2_nr": None},
                }

        # GOALS
        if "goals" not in m or not isinstance(m["goals"], dict):
            m["goals"] = {
                "input": None,
                "name": None,
                "number": None,
                "logo": None,
                "team": None,
            }

        save_config(self.cfg)

    # ==================================================
    # OPEN MAPPING
    # ==================================================
    def _open_mapping(self):
        # MappingDialog ALWAYS gets fully corrected config here
        MappingDialog(self, self.cfg, self.client)


def open_settings_dialog(parent, cfg, client):
    SettingsDialog(parent, cfg, client)
