import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

from scoreboard_app.gui.mapping_dialog import MappingDialog


class SettingsDialog(tk.Toplevel):
    """
    Modal settings window:
    - Shows connection config
    - Mapping button opens MappingDialog
    - Saves to vmix_config.json
    """

    def __init__(self, master, cfg, client):
        super().__init__(master)
        self.title("Inställningar – Scoreboard System")
        self.geometry("450x480")
        self.resizable(False, False)

        self.cfg = cfg
        self.client = client

        # -----------------------------
        # HEADER
        # -----------------------------
        header = ttk.Label(self, text="Systeminställningar", font=("Segoe UI", 14))
        header.pack(pady=10)

        # -----------------------------
        # FRAME: VMIX SETTINGS
        # -----------------------------
        vm_frame = ttk.LabelFrame(self, text="vMix Anslutning")
        vm_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(vm_frame, text="Host/IP:").pack(anchor="w", padx=4)
        self.host_var = tk.StringVar(value=self.cfg["vmix"]["host"])
        ttk.Entry(vm_frame, textvariable=self.host_var).pack(fill="x", padx=4)

        ttk.Label(vm_frame, text="Port:").pack(anchor="w", padx=4)
        self.port_var = tk.StringVar(value=self.cfg["vmix"]["port"])
        ttk.Entry(vm_frame, textvariable=self.port_var).pack(fill="x", padx=4)

        # -----------------------------
        # BUTTON AREA
        # -----------------------------
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=15, padx=10)

        # === NEW: Mapping Button ===
        def _open_mapping():
            MappingDialog(self, self.cfg, self.client)

        ttk.Button(btn_frame, text="Mapping", command=_open_mapping).pack(fill="x", pady=4)

        # SAVE BUTTON
        ttk.Button(btn_frame, text="Spara", command=self._save).pack(side="left", expand=True, padx=6)

        # CLOSE BUTTON
        ttk.Button(btn_frame, text="Stäng", command=self.destroy).pack(side="right", expand=True, padx=6)

        self.grab_set()
        self.focus_force()

    # ------------------------------------------------------------
    def _save(self):
        """Store config changes to vmix_config.json"""
        try:
            self.cfg["vmix"]["host"] = self.host_var.get()
            self.cfg["vmix"]["port"] = int(self.port_var.get())

            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "vmix_config.json")
            config_path = os.path.abspath(config_path)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.cfg, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Sparat", "Inställningarna är sparade.")
        except Exception as e:
            messagebox.showerror("Fel", str(e))


# ------------------------------------------------------------
# Public function used by MainWindow
# ------------------------------------------------------------
def open_settings_dialog(master, cfg, client):
    SettingsDialog(master, cfg, client)
