# scoreboard_app/gui/player_select_dialog.py

import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Optional


def pick_player(parent, players: List[Tuple[str, str]], team_name: str) -> Optional[Tuple[str, str]]:
    """
    Popup dialog för att välja spelare:
    - players: lista av (number, name)
    - returnerar (number, name) eller None
    """

    dialog = tk.Toplevel(parent)
    dialog.title(f"Välj spelare – {team_name}")
    dialog.geometry("420x500")
    dialog.grab_set()

    # Sortera efter nummer
    players_sorted = sorted(players, key=lambda x: int(x[0]) if x[0].isdigit() else 999)

    # UI
    frame = ttk.Frame(dialog)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    listbox = tk.Listbox(frame, font=("Segoe UI", 12))
    listbox.pack(fill="both", expand=True)

    for num, name in players_sorted:
        listbox.insert(tk.END, f"{num}  –  {name}")

    selected = {"value": None}

    def on_ok():
        try:
            idx = listbox.curselection()[0]
        except:
            selected["value"] = None
            dialog.destroy()
            return

        selected["value"] = players_sorted[idx]
        dialog.destroy()

    def on_no_player():
        selected["value"] = None
        dialog.destroy()

    btns = ttk.Frame(dialog)
    btns.pack(pady=10)

    ttk.Button(btns, text="Välj spelare", command=on_ok).grid(row=0, column=0, padx=10)
    ttk.Button(btns, text="Ok – ingen spelare", command=on_no_player).grid(row=0, column=1, padx=10)

    dialog.wait_window()

    return selected["value"]
