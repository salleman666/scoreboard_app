import tkinter as tk
from tkinter import ttk

from scoreboard_app.gui.mapping_dialog import MappingDialog

class SettingsDialog(tk.Toplevel):
    def __init__(self, master, cfg, client):
        super().__init__(master)
        self.title("Settings")
        self.geometry("300x300")

        self.cfg = cfg
        self.client = client

        ttk.Label(self, text="Settings", font=("Arial", 12, "bold")).pack(pady=6)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", expand=True)

        ttk.Button(btn_frame, text="Mapping",
                   command=self._open_mapping).pack(fill="x", pady=4)

        ttk.Button(btn_frame, text="Close",
                   command=self.destroy).pack(fill="x", pady=4)

    def _open_mapping(self):
        MappingDialog(self, self.cfg, self.client)

def open_settings_dialog(master, cfg, client):
    SettingsDialog(master, cfg, client)
