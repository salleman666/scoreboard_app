import tkinter as tk
from tkinter import ttk

class MappingDialog(tk.Toplevel):
    def __init__(self, master, cfg, client):
        super().__init__(master)
        self.title("Mapping Editor")
        self.geometry("600x400")

        self.cfg = cfg
        self.client = client

        ttk.Label(self, text="Mapping Editor", font=("Arial", 12, "bold")).pack(pady=6)

        self.tree = ttk.Treeview(self, columns=("key", "value"), show="headings")
        self.tree.heading("key", text="Config Key")
        self.tree.heading("value", text="Mapped Value")
        self.tree.pack(fill="both", expand=True)

        # load mapping
        self._populate()

        ttk.Button(self, text="Close", command=self.destroy).pack(pady=6)

    def _populate(self):
        mapping = self.cfg.get("mapping", {})
        for section, values in mapping.items():
            if isinstance(values, dict):
                for key, val in values.items():
                    self.tree.insert("", tk.END, values=(f"{section}.{key}", str(val)))
