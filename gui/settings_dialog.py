import tkinter as tk
from tkinter import ttk

class SettingsDialog(tk.Toplevel):
    """
    Main settings popup window.
    """
    def __init__(self, master, config):
        super().__init__(master)
        self.title("Inställningar")
        self.config = config
        self.transient(master)
        self.grab_set()

        main = ttk.Frame(self, padding=10)
        main.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Example field
        ttk.Label(main, text="Host:").grid(row=0, column=0, sticky="w")
        self.host_var = tk.StringVar(value=str(self.config["vmix"]["host"]))
        ttk.Entry(main, textvariable=self.host_var, width=30).grid(row=0, column=1, pady=4)

        ttk.Label(main, text="Port:").grid(row=1, column=0, sticky="w")
        self.port_var = tk.StringVar(value=str(self.config["vmix"]["port"]))
        ttk.Entry(main, textvariable=self.port_var, width=10).grid(row=1, column=1, pady=4)

        # Buttons row
        btns = ttk.Frame(main)
        btns.grid(row=99, column=0, columnspan=2, sticky="e", pady=10)

        ttk.Button(btns, text="Spara", command=self._on_save).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Avbryt", command=self.destroy).grid(row=0, column=1, padx=5)

    def _on_save(self):
        # persist updated values
        self.config["vmix"]["host"] = self.host_var.get()
        self.config["vmix"]["port"] = int(self.port_var.get())
        self.destroy()


def open_settings_dialog(master, config):
    """
    FUNCTION WRAPPER — REQUIRED BY MAIN WINDOW IMPORT

    This function creates the dialog and blocks until user closes it.
    """
    dlg = SettingsDialog(master, config)
    master.wait_window(dlg)
