# vmix_gui_tk.py – Version 15.1
# ------------------------------------------------------------
# GUI för vMix Scoreboard-kontroll
#
# Nytt i 15.1:
#  • Målgrafik-input (MÅÅL) är nu en dropdown med alla vMix-inputs.
#  • Efter-mål grafik-input är också dropdown med alla vMix-inputs.
#  • Overlay-kanaler för MÅÅL + Efter-mål är dropdown (1–8).
#  • Nya + / – knappar för att justera mål utan att trigga MÅÅL-grafik.
#
# 15.0:
#  • Inställningar-fönster med flikar: BAS / AVANCERAT
#  • BAS:
#       - Scoreboard-input
#       - Målgrafik-input + overlay-kanal + duration (ms)
#       - Standard periodtid
#       - OT-tid
#  • AVANCERAT:
#       - Efter-mål grafik input + duration (ms)
#       - Overlay follow clock
#       - Fältmapping för utvisningar (H1/H2/A1/A2) via dropdown
#       - Mobile-permissions för framtida webb-GUI
# ------------------------------------------------------------

import time
import tkinter as tk
from tkinter import ttk, messagebox

from vmix_client import VMixClient
from vmix_config import load_config, save_config
from scoreboard_controller import ScoreboardController, _parse_time_to_seconds

POLL_INTERVAL_MS = 1100
DEFAULT_PERIOD_TIME = "20:00"
DEFAULT_OT_TIME = "05:00"


class ScoreboardApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Scoreboard Controller – Version 15.1")
        self.geometry("1000x700")

        # Config / vMix / controller
        self.cfg = load_config()
        self.client: VMixClient | None = None
        self.controller: ScoreboardController | None = None
        self._connected = False

        # Internal UI-state
        self._clock_running_ui = False
        self._scoreboard_visible = False
        self._empty_home_active = False
        self._empty_away_active = False
        self._current_period = 1
        self._zero_handled = False

        # Ladda ev. sparade periodtider
        sb_cfg = self.cfg.get("scoreboard", {})
        global DEFAULT_PERIOD_TIME, DEFAULT_OT_TIME
        DEFAULT_PERIOD_TIME = sb_cfg.get("default_period_time", DEFAULT_PERIOD_TIME)
        DEFAULT_OT_TIME = sb_cfg.get("ot_time", DEFAULT_OT_TIME)

        self._build_login()
        self.after(POLL_INTERVAL_MS, self._poll_loop)

    # --------------------------------------------------------
    def _log(self, msg: str) -> None:
        print(f"[LOG] {msg}")

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------
    def _build_login(self) -> None:
        self.login_frame = tk.Frame(self)
        self.login_frame.pack(expand=True)

        tk.Label(
            self.login_frame,
            text="Anslut till vMix",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=20)

        row = tk.Frame(self.login_frame)
        row.pack(pady=5)

        tk.Label(row, text="IP:").grid(row=0, column=0, padx=4)
        self.ip_entry = tk.Entry(row, width=15)
        self.ip_entry.insert(0, self.cfg["vmix"].get("host", "127.0.0.1"))
        self.ip_entry.grid(row=0, column=1, padx=4)

        tk.Label(row, text="Port:").grid(row=0, column=2, padx=4)
        self.port_entry = tk.Entry(row, width=6)
        self.port_entry.insert(0, str(self.cfg["vmix"].get("port", 8088)))
        self.port_entry.grid(row=0, column=3, padx=4)

        ttk.Button(
            self.login_frame,
            text="Anslut",
            command=self._on_connect_clicked,
        ).pack(pady=15)

    def _on_connect_clicked(self) -> None:
        try:
            host = self.ip_entry.get().strip() or "127.0.0.1"
            port = int(self.port_entry.get().strip() or "8088")
        except ValueError:
            messagebox.showerror("Fel", "Ogiltig port.")
            return

        try:
            self.client = VMixClient(host, port)
            self.client.get_status_xml()  # test-anrop
            self.controller = ScoreboardController(self.client, self.cfg)
        except Exception as e:
            messagebox.showerror("Fel", f"Kunde inte ansluta till vMix: {e}")
            return

        self._connected = True
        self.login_frame.destroy()
        self._build_main_ui()

        # Läs overlay-läge från vMix och synka knappen
        try:
            if self.controller.is_scoreboard_overlay_active():
                self._scoreboard_visible = True
            else:
                self._scoreboard_visible = False
            self._update_scoreboard_button()
        except Exception as e:
            self._log(f"Kunde inte läsa overlay-state: {e}")

    # --------------------------------------------------------
    # HUVUD-UI
    # --------------------------------------------------------
    def _build_main_ui(self) -> None:
        main = tk.Frame(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # MÅL-knappar
        goal = tk.Frame(main)
        goal.pack(pady=10)

        self._goal_home_btn = tk.Button(
            goal,
            text="MÅL\n0\nHEMMA",
            width=10,
            height=3,
            font=("Segoe UI", 11, "bold"),
            command=lambda: self._on_goal(True),
        )
        self._goal_home_btn.grid(row=0, column=0, padx=20)

        self._goal_away_btn = tk.Button(
            goal,
            text="MÅL\n0\nBORTA",
            width=10,
            height=3,
            font=("Segoe UI", 11, "bold"),
            command=lambda: self._on_goal(False),
        )
        self._goal_away_btn.grid(row=0, column=2, padx=20)

        tk.Label(goal, text="").grid(row=0, column=1, padx=30)

        # POÄNG-JUSTERING (utan MÅÅL-grafik)
        score_adj = tk.Frame(main)
        score_adj.pack(pady=2)

        tk.Label(score_adj, text="Justera mål (utan grafik):").grid(
            row=0, column=0, columnspan=4, pady=(0, 2)
        )

        tk.Button(
            score_adj,
            text="H -",
            width=4,
            command=lambda: self._on_adjust_score(True, -1),
        ).grid(row=1, column=0, padx=3)

        tk.Button(
            score_adj,
            text="H +",
            width=4,
            command=lambda: self._on_adjust_score(True, +1),
        ).grid(row=1, column=1, padx=3)

        tk.Button(
            score_adj,
            text="B -",
            width=4,
            command=lambda: self._on_adjust_score(False, -1),
        ).grid(row=1, column=2, padx=3)

        tk.Button(
            score_adj,
            text="B +",
            width=4,
            command=lambda: self._on_adjust_score(False, +1),
        ).grid(row=1, column=3, padx=3)

        # START/STOP + justering
        center = tk.Frame(main)
        center.pack(pady=10)

        tk.Button(center, text="-5", width=6, height=2,
                  command=lambda: self._on_adjust(-5)).grid(row=0, column=0, padx=5)
        tk.Button(center, text="-1", width=6, height=2,
                  command=lambda: self._on_adjust(-1)).grid(row=1, column=0, padx=5)

        self._clock_btn = tk.Button(
            center,
            text="START\n--:--",
            width=12,
            height=5,
            font=("Segoe UI", 16, "bold"),
            bg="green",
            fg="black",
            command=self._on_toggle_clock,
        )
        self._clock_btn.grid(row=0, column=1, rowspan=2, padx=20)

        tk.Button(center, text="+1", width=6, height=2,
                  command=lambda: self._on_adjust(+1)).grid(row=0, column=2, padx=5)
        tk.Button(center, text="+5", width=6, height=2,
                  command=lambda: self._on_adjust(+5)).grid(row=1, column=2, padx=5)

        # EMPTY GOAL
        empty = tk.Frame(main)
        empty.pack(pady=10)

        self._empty_home_btn = tk.Button(
            empty,
            text="EMPTY\nGOAL\nHEMMA",
            width=10,
            height=3,
            font=("Segoe UI", 10, "bold"),
            command=self._on_empty_home_toggle,
        )
        self._empty_home_btn.grid(row=0, column=0, padx=20)

        self._empty_away_btn = tk.Button(
            empty,
            text="EMPTY\nGOAL\nBORTA",
            width=10,
            height=3,
            font=("Segoe UI", 10, "bold"),
            command=self._on_empty_away_toggle,
        )
        self._empty_away_btn.grid(row=0, column=2, padx=20)

        tk.Label(empty, text="").grid(row=0, column=1, padx=30)

        # PERIOD-knappar
        per = tk.Frame(main)
        per.pack(pady=5)

        self._period_buttons: dict[int, tk.Button] = {}
        for idx, label in enumerate(["1", "2", "3", "OT"], start=1):
            b = tk.Button(
                per,
                text=f"PERIOD\n{label}",
                width=8,
                height=2,
                font=("Segoe UI", 10, "bold"),
                command=lambda p=idx: self._on_set_period(p),
            )
            b.grid(row=0, column=idx - 1, padx=5)
            self._period_buttons[idx] = b
        self._update_period_buttons()

        # UTVISNINGAR
        pen = tk.Frame(main)
        pen.pack(pady=15)

        tk.Label(pen, text="UTVISNINGAR",
                 font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=4, pady=5)

        self._penalty_buttons: dict[str, tk.Button] = {}
        for idx, slot in enumerate(["H1", "H2", "A1", "A2"]):
            b = tk.Button(
                pen,
                text=f"{slot}\n00:00",
                width=8,
                height=3,
                font=("Segoe UI", 10),
                command=lambda s=slot: self._on_penalty_button(s),
            )
            b.grid(row=1, column=idx, padx=10, pady=5)
            self._penalty_buttons[slot] = b

        # SCOREBOARD overlay-knapp
        self._sb_toggle_btn = tk.Button(
            main,
            text="VISA SCOREBOARD",
            width=20,
            height=2,
            font=("Segoe UI", 11, "bold"),
            command=self._on_toggle_scoreboard,
        )
        self._sb_toggle_btn.pack(pady=10)

        # INSTÄLLNINGAR
        tk.Button(
            main,
            text="INSTÄLLNINGAR",
            width=20,
            height=2,
            font=("Segoe UI", 11),
            command=self._open_settings,
        ).pack(pady=5)

    # --------------------------------------------------------
    # POLL-LOOP
    # --------------------------------------------------------
    def _poll_loop(self) -> None:
        if self._connected and self.controller:
            try:
                state = self.controller.get_state()
                self._update_from_state(state)
            except Exception as e:
                self._log(f"Fel vid Poll: {e}")

        self.after(POLL_INTERVAL_MS, self._poll_loop)

    # --------------------------------------------------------
    # STATE → GUI
    # --------------------------------------------------------
    def _update_from_state(self, state: dict) -> None:
        clock_raw = state.get("clock_raw", "") or "--:--"
        secs = state.get("clock_secs")
        running = bool(state.get("clock_running", False))

        # uppdatera START/STOP-knapp
        self._update_clock_button(clock_raw, running)

        # 00:00-hantering (periodslut)
        if secs == 0:
            if not self._zero_handled:
                self._zero_handled = True

                # Dölj scoreboard-overlay vid periodslut
                try:
                    self.controller.set_scoreboard_overlay(False)
                    self._scoreboard_visible = False
                    self._update_scoreboard_button()
                except Exception as e:
                    self._log(f"Fel vid dölja scoreboard vid 00:00: {e}")

                # Stoppa matchur + pausa utvisningar
                try:
                    self.controller.stop_clock_and_penalties_at_zero()
                except Exception as e:
                    self._log(f"Fel vid stop_clock_and_penalties_at_zero: {e}")

                # Fråga om ny period
                self.after(200, self._ask_new_period)
        else:
            self._zero_handled = False

        # Utvisningar
        for slot, pdata in state.get("penalties", {}).items():
            btn = self._penalty_buttons.get(slot)
            if not btn:
                continue
            t_raw = pdata.get("time_raw") or "00:00"
            active = bool(pdata.get("active"))
            btn.configure(text=f"{slot}\n{t_raw}")
            btn.configure(bg="yellow" if active else "lightgrey")

        # Period (från grafik)
        per = state.get("period")
        if per:
            try:
                idx = 4 if str(per).upper() == "OT" else int(per)
                if idx in self._period_buttons:
                    self._current_period = idx
                    self._update_period_buttons()
            except Exception:
                pass

        # Målställning
        try:
            hs = str(state.get("home_score") or "0")
            aw = str(state.get("away_score") or "0")
            self._goal_home_btn.config(text=f"MÅL\n{hs}\nHEMMA")
            self._goal_away_btn.config(text=f"MÅL\n{aw}\nBORTA")
        except Exception:
            pass

    # --------------------------------------------------------
    # Klock-knapp
    # --------------------------------------------------------
    def _update_clock_button(self, value: str, running: bool) -> None:
        self._clock_running_ui = running
        if not value:
            value = "--:--"

        if running:
            self._clock_btn.config(text=f"STOPP\n{value}", bg="red", fg="white")
        else:
            self._clock_btn.config(text=f"START\n{value}", bg="green", fg="black")

        self._update_penalty_buttons_state()

    def _on_toggle_clock(self) -> None:
        if not self._require_controller():
            return

        # Kolla aktuell tid direkt från title-fältet
        try:
            sb_input = self.controller.sb_input
            clock_field = self.cfg["scoreboard"]["clock_field"]
            cur_raw = self.controller.client.get_text_from_title(
                self.controller.client.find_input_number(sb_input) or sb_input,
                clock_field,
            )
        except Exception:
            cur_raw = "00:00"

        secs = _parse_time_to_seconds(cur_raw)

        # Försök starta med 00:00 -> blockera, tvinga användaren sätta tid
        if not self._clock_running_ui and (secs is None or secs == 0):
            messagebox.showwarning(
                "Ingen tid",
                "Matchuret står på 00:00.\nSätt matchtid i Inställningar eller via perioddialogen innan du startar.",
            )
            return

        was_running = self._clock_running_ui

        try:
            self.controller.toggle_clock()
        except Exception as e:
            messagebox.showerror("Fel", f"Kunde inte toggla klocka: {e}")
            self._log(f"ToggleClock-fel: {e}")
            return

        # Om vi gick från stopp → start: tänd scoreboard automatiskt
        if not was_running:
            try:
                if not self._scoreboard_visible:
                    self.controller.set_scoreboard_overlay(True)
                    self._scoreboard_visible = True
                    self._update_scoreboard_button()
            except Exception as e:
                self._log(f"Fel vid auto-tända scoreboard vid start: {e}")

    # --------------------------------------------------------
    # Justera mål utan MÅÅL-grafik
    # --------------------------------------------------------
    def _on_adjust_score(self, home: bool, delta: int) -> None:
        if not self._require_controller():
            return
        try:
            # Använd controllerns interna score-funktion utan grafik
            field = (
                self.controller.sb_cfg["home_score_field"]
                if home
                else self.controller.sb_cfg["away_score_field"]
            )
            # _increment_score finns i ScoreboardController
            self.controller._increment_score(field, delta)
            self._log(
                f"Justering av {'HEMMA' if home else 'BORTA'}-mål med {delta:+d} (utan grafik)."
            )
        except Exception as e:
            self._log(f"Kunde inte justera mål: {e}")
            messagebox.showerror("Fel", f"Kunde inte justera mål: {e}")

    # --------------------------------------------------------
    # Period
    # --------------------------------------------------------
    def _on_set_period(self, idx: int) -> None:
        self._current_period = idx
        self._update_period_buttons()
        if not self._require_controller():
            return

        val = "OT" if idx == 4 else str(idx)
        try:
            self.controller.set_period(val)
            self._log(f"Period satt till {val}.")
        except Exception as e:
            self._log(f"Kunde inte sätta period: {e}")
            messagebox.showerror("Fel", f"Kunde inte sätta period: {e}")

    def _update_period_buttons(self) -> None:
        for idx, btn in self._period_buttons.items():
            if idx == self._current_period:
                btn.config(bg="blue", fg="white")
            else:
                btn.config(bg="SystemButtonFace", fg="black")

    # --------------------------------------------------------
    # SCOREBOARD overlay-knapp
    # --------------------------------------------------------
    def _on_toggle_scoreboard(self) -> None:
        if not self._require_controller():
            return

        self._scoreboard_visible = not self._scoreboard_visible
        try:
            self.controller.set_scoreboard_overlay(self._scoreboard_visible)
            self._log(
                "Scoreboard overlay PÅ" if self._scoreboard_visible else "Scoreboard overlay AV"
            )
        except Exception as e:
            self._log(f"Kunde inte toggla scoreboard: {e}")
            messagebox.showerror("Fel", f"Kunde inte toggla scoreboard: {e}")

        self._update_scoreboard_button()

    def _update_scoreboard_button(self) -> None:
        if self._scoreboard_visible:
            self._sb_toggle_btn.config(text="DÖLJ SCOREBOARD", bg="orange")
        else:
            self._sb_toggle_btn.config(text="VISA SCOREBOARD", bg="SystemButtonFace")

    # --------------------------------------------------------
    # Justera tid
    # --------------------------------------------------------
    def _on_adjust(self, delta: int) -> None:
        if not self._require_controller():
            return
        try:
            self.controller.adjust_times(delta)
            self._log(f"Justering {delta:+d} sek på klocka och utvisningar.")
        except Exception as e:
            self._log(f"Kunde inte justera tid: {e}")
            messagebox.showerror("Fel", f"Kunde inte justera tid: {e}")

    # --------------------------------------------------------
    # MÅL
    # --------------------------------------------------------
    def _on_goal(self, home: bool) -> None:
        if not self._require_controller():
            return
        try:
            self.controller.pause_clock_and_penalties()
            if home:
                self.controller.home_goal()
            else:
                self.controller.away_goal()
            # Här används fortfarande trigger_goal_graphic (MÅÅL),
            # efter-mål-grafik kopplas in via graphics_controller.
            self.controller.trigger_goal_graphic()
            self._log("MÅL HEMMA" if home else "MÅL BORTA")
        except Exception as e:
            self._log(f"Fel vid MÅL: {e}")
            messagebox.showerror("Fel", f"Fel vid MÅL: {e}")

    # --------------------------------------------------------
    # EMPTY GOAL
    # --------------------------------------------------------
    def _on_empty_home_toggle(self) -> None:
        if not self._require_controller():
            return
        self._empty_home_active = not self._empty_home_active
        try:
            self.controller.set_empty_net_home(self._empty_home_active)
        except Exception as e:
            self._log(f"Fel vid Empty goal hemma: {e}")
            messagebox.showerror("Fel", f"Empty goal hemma misslyckades: {e}")
        self._update_empty_buttons()

    def _on_empty_away_toggle(self) -> None:
        if not self._require_controller():
            return
        self._empty_away_active = not self._empty_away_active
        try:
            self.controller.set_empty_net_away(self._empty_away_active)
        except Exception as e:
            self._log(f"Fel vid Empty goal borta: {e}")
            messagebox.showerror("Fel", f"Empty goal borta misslyckades: {e}")
        self._update_empty_buttons()

    def _update_empty_buttons(self) -> None:
        if getattr(self, "_empty_home_btn", None):
            if self._empty_home_active:
                self._empty_home_btn.config(bg="blue", fg="white")
            else:
                self._empty_home_btn.config(bg="SystemButtonFace", fg="black")
        if getattr(self, "_empty_away_btn", None):
            if self._empty_away_active:
                self._empty_away_btn.config(bg="blue", fg="white")
            else:
                self._empty_away_btn.config(bg="SystemButtonFace", fg="black")

    # --------------------------------------------------------
    # Utvisningar
    # --------------------------------------------------------
    def _update_penalty_buttons_state(self) -> None:
        state = "disabled" if self._clock_running_ui else "normal"
        for btn in self._penalty_buttons.values():
            try:
                btn.config(state=state)
            except Exception:
                pass

    def _on_penalty_button(self, slot: str) -> None:
        if not self._require_controller():
            return

        win = tk.Toplevel(self)
        win.title(f"Utvisning {slot}")
        win.grab_set()

        tk.Label(win, text=f"Slot {slot}").grid(row=0, column=0, columnspan=2, pady=5)

        tk.Label(win, text="Nummer:").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        num_entry = tk.Entry(win, width=8)
        num_entry.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        tk.Label(win, text="Tid (MM:SS):").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        time_entry = tk.Entry(win, width=8)
        time_entry.insert(0, "02:00")
        time_entry.grid(row=2, column=1, sticky="w", padx=4, pady=2)

        def on_ok() -> None:
            num = num_entry.get().strip()
            tval = time_entry.get().strip()
            if not tval:
                tval = "02:00"
            if _parse_time_to_seconds(tval) is None:
                messagebox.showerror(
                    "Fel", "Ogiltig tid – skriv t.ex. 2:00 eller 02:00."
                )
                return
            try:
                # name lämnas tomt (hanteras inte i SCOREBOARD UPPE)
                self.controller.set_penalty(slot, num, "", tval)
                self._log(f"Utvisning {slot}: {num} {tval}")
            except Exception as e:
                self._log(f"Kunde inte sätta utvisning: {e}")
                messagebox.showerror("Fel", f"Kunde inte sätta utvisning: {e}")
            win.destroy()

        def on_clear() -> None:
            try:
                self.controller.clear_penalty(slot)
                self._log(f"Utvisning {slot} rensad.")
            except Exception as e:
                self._log(f"Kunde inte rensa utvisning: {e}")
                messagebox.showerror("Fel", f"Kunde inte rensa utvisning: {e}")
            win.destroy()

        btn_row = tk.Frame(win)
        btn_row.grid(row=3, column=0, columnspan=2, pady=8)

        ttk.Button(btn_row, text="OK", command=on_ok).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Rensa", command=on_clear).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Avbryt", command=win.destroy).pack(side="left", padx=5)

    # --------------------------------------------------------
    # Inställningar (BAS / AVANCERAT)
    # --------------------------------------------------------
    def _open_settings(self) -> None:
        win = tk.Toplevel(self)
        win.title("Inställningar – Version 15.1")
        win.geometry("650x540")
        win.grab_set()

        # Hämta lista med alla input-titlar från vMix (för dropdowns)
        input_names: list[str] = []
        try:
            if self.controller:
                root = self.controller.client.get_status_xml()
                for inp in root.findall("./inputs/input"):
                    title = inp.get("title") or inp.get("shortTitle") or inp.get("number")
                    if title:
                        input_names.append(title)
            input_names = sorted(set(input_names))
        except Exception as e:
            self._log(f"Kunde inte läsa input-lista från vMix: {e}")
            input_names = []

        overlay_channels = [str(i) for i in range(1, 9)]

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        base_frame = tk.Frame(notebook)
        adv_frame = tk.Frame(notebook)

        notebook.add(base_frame, text="Bas")
        notebook.add(adv_frame, text="Avancerat")

        sb_cfg = self.cfg.get("scoreboard", {})

        # ---------------- BAS-FLIKEN ----------------
        # SCOREBOARD INPUT
        tk.Label(base_frame, text="Scoreboard-input",
                 font=("Segoe UI", 11, "bold")).pack(pady=5, anchor="w", padx=5)
        sb_frame = tk.Frame(base_frame)
        sb_frame.pack(pady=5, fill="x")

        tk.Label(sb_frame, text="Input-namn/nummer:").grid(row=0, column=0, padx=5, sticky="e")
        sb_var = tk.StringVar(value=sb_cfg.get("input", ""))
        tk.Entry(sb_frame, textvariable=sb_var, width=30).grid(row=0, column=1, padx=5, sticky="w")

        # MÅLGRAFIK (MÅÅL)
        tk.Label(base_frame, text="Målgrafik (MÅÅL)",
                 font=("Segoe UI", 11, "bold")).pack(pady=5, anchor="w", padx=5)
        goal_frame = tk.Frame(base_frame)
        goal_frame.pack(pady=5, fill="x")

        tk.Label(goal_frame, text="Input-namn:").grid(row=0, column=0, padx=5, sticky="e")
        goal_var = tk.StringVar(value=sb_cfg.get("goal_graphic_input", ""))
        ttk.Combobox(
            goal_frame,
            textvariable=goal_var,
            values=input_names,
            state="readonly",
            width=27,
        ).grid(row=0, column=1, padx=5, sticky="w")

        tk.Label(goal_frame, text="Overlay-kanal:").grid(row=1, column=0, padx=5, sticky="e")
        goal_ch_var = tk.StringVar(value=str(sb_cfg.get("goal_overlay_channel", 2)))
        ttk.Combobox(
            goal_frame,
            textvariable=goal_ch_var,
            values=overlay_channels,
            state="readonly",
            width=5,
        ).grid(row=1, column=1, padx=5, sticky="w")

        tk.Label(goal_frame, text="MÅL-duration (ms):").grid(row=2, column=0, padx=5, sticky="e")
        goal_dur_var = tk.StringVar(value=str(sb_cfg.get("goal_duration_ms", 5000)))
        tk.Entry(goal_frame, textvariable=goal_dur_var, width=8).grid(row=2, column=1, padx=5, sticky="w")

        # MATCHTIDER
        tk.Label(base_frame, text="Matchtider",
                 font=("Segoe UI", 11, "bold")).pack(pady=5, anchor="w", padx=5)
        time_frame = tk.Frame(base_frame)
        time_frame.pack(pady=5, fill="x")

        global DEFAULT_PERIOD_TIME, DEFAULT_OT_TIME
        period_time_var = tk.StringVar(value=sb_cfg.get("default_period_time", DEFAULT_PERIOD_TIME))
        ot_time_var = tk.StringVar(value=sb_cfg.get("ot_time", DEFAULT_OT_TIME))

        tk.Label(time_frame, text="Periodtid (MM:SS):").grid(row=0, column=0, padx=5, sticky="e")
        tk.Entry(time_frame, textvariable=period_time_var, width=8).grid(row=0, column=1, padx=5, sticky="w")

        tk.Label(time_frame, text="OT-tid (MM:SS):").grid(row=1, column=0, padx=5, sticky="e")
        tk.Entry(time_frame, textvariable=ot_time_var, width=8).grid(row=1, column=1, padx=5, sticky="w")

        # Snabbknappar periodtid
        def set_period_time(val: str) -> None:
            period_time_var.set(val)
            try:
                if self._require_controller():
                    self.controller.set_match_time(val)
                    self._log(f"Matchtid satt via snabbknapp: {val}")
            except Exception as e:
                self._log(f"Fel vid set_match_time i settings: {e}")

        btns = tk.Frame(time_frame)
        btns.grid(row=0, column=2, rowspan=2, padx=8)
        ttk.Button(btns, text="20:00", width=6,
                   command=lambda: set_period_time("20:00")).grid(row=0, column=0, padx=2, pady=1)
        ttk.Button(btns, text="15:00", width=6,
                   command=lambda: set_period_time("15:00")).grid(row=0, column=1, padx=2, pady=1)
        ttk.Button(btns, text="05:00", width=6,
                   command=lambda: set_period_time("05:00")).grid(row=1, column=0, padx=2, pady=1)

        # ---------------- AVANCERAD-FLIKEN ----------------
        adv_inner = tk.Frame(adv_frame)
        adv_inner.pack(fill="both", expand=True, padx=5, pady=5)

        # Efter-mål grafik
        tk.Label(adv_inner, text="Efter-mål grafik",
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 5))

        tk.Label(adv_inner, text="Input-namn:").grid(row=1, column=0, padx=5, sticky="e")
        after_goal_var = tk.StringVar(value=sb_cfg.get("after_goal_graphic_input", ""))
        ttk.Combobox(
            adv_inner,
            textvariable=after_goal_var,
            values=input_names,
            state="readonly",
            width=27,
        ).grid(row=1, column=1, padx=5, sticky="w")

        tk.Label(adv_inner, text="Overlay-kanal:").grid(row=1, column=2, padx=5, sticky="e")
        after_goal_ch_var = tk.StringVar(value=str(sb_cfg.get("after_goal_overlay_channel", 2)))
        ttk.Combobox(
            adv_inner,
            textvariable=after_goal_ch_var,
            values=overlay_channels,
            state="readonly",
            width=5,
        ).grid(row=1, column=3, padx=5, sticky="w")

        tk.Label(adv_inner, text="Efter-mål duration (ms):").grid(row=2, column=0, padx=5, sticky="e")
        after_goal_dur_var = tk.StringVar(value=str(sb_cfg.get("after_goal_duration_ms", 4000)))
        tk.Entry(adv_inner, textvariable=after_goal_dur_var, width=8).grid(
            row=2, column=1, padx=5, sticky="w"
        )

        # Overlay follow clock
        tk.Label(adv_inner, text="Overlay följer klocka",
                 font=("Segoe UI", 11, "bold")).grid(row=3, column=0, columnspan=4, sticky="w", pady=(10, 5))
        overlay_var = tk.BooleanVar(value=bool(sb_cfg.get("overlay_follow_clock", False)))
        tk.Checkbutton(adv_inner, text="Aktivera", variable=overlay_var).grid(
            row=4, column=0, columnspan=4, sticky="w", padx=10
        )

        # Penalty-field mapping
        tk.Label(adv_inner, text="Utvisnings-fält (mapping från SCOREBOARD UPPE)",
                 font=("Segoe UI", 11, "bold")).grid(row=5, column=0, columnspan=4, sticky="w", pady=(10, 5))

        pen_frame = tk.Frame(adv_inner, borderwidth=1, relief="groove")
        pen_frame.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)

        for i in range(5):
            pen_frame.columnconfigure(i, weight=1)

        tk.Label(pen_frame, text="Slot").grid(row=0, column=0, padx=3, pady=2)
        tk.Label(pen_frame, text="Tid (Text)").grid(row=0, column=1, padx=3, pady=2)
        tk.Label(pen_frame, text="Nummer (Text)").grid(row=0, column=2, padx=3, pady=2)
        tk.Label(pen_frame, text="BG tid (Image)").grid(row=0, column=3, padx=3, pady=2)
        tk.Label(pen_frame, text="BG nr (Image)").grid(row=0, column=4, padx=3, pady=2)

        # Försök läsa alla text/image-fält från SCOREBOARD-inputen
        text_fields = []
        image_fields = []
        slot_vars: dict[str, dict[str, tk.StringVar]] = {}

        try:
            if self.controller:
                root = self.controller.client.get_status_xml()
                sb_input_name = sb_var.get().strip() or sb_cfg.get("input", "")
                sb_inp_num = self.controller.client.find_input_number(sb_input_name) or sb_input_name

                sb_node = None
                for inp in root.findall("./inputs/input"):
                    if inp.get("number") == str(sb_inp_num) or inp.get("title") == sb_input_name:
                        sb_node = inp
                        break

                if sb_node is not None:
                    for t in sb_node.findall("text"):
                        name = t.get("name")
                        if name:
                            text_fields.append(name)
                    for im in sb_node.findall("image"):
                        name = im.get("name")
                        if name:
                            image_fields.append(name)

            text_fields = sorted(set(text_fields))
            image_fields = sorted(set(image_fields))
        except Exception as e:
            self._log(f"Kunde inte läsa fält från SCOREBOARD-input: {e}")
            text_fields = []
            image_fields = []

        penalties_cfg = sb_cfg.get("penalties", {})
        slots = ["H1", "H2", "A1", "A2"]

        for r, slot in enumerate(slots, start=1):
            tk.Label(pen_frame, text=slot).grid(row=r, column=0, padx=3, pady=2)

            slot_vars[slot] = {
                "time": tk.StringVar(),
                "nr": tk.StringVar(),
                "bg_time": tk.StringVar(),
                "bg_nr": tk.StringVar(),
            }

            # Förifyll med befintlig config eller defaults från controller
            try:
                if self.controller:
                    fields = self.controller._penalty_fields(slot)
                    pen_cfg_slot = penalties_cfg.get(slot, {})
                    slot_vars[slot]["time"].set(
                        pen_cfg_slot.get("time_field", fields.get("time_field") or "")
                    )
                    slot_vars[slot]["nr"].set(
                        pen_cfg_slot.get("number_field", fields.get("number_field") or "")
                    )
                    slot_vars[slot]["bg_time"].set(
                        pen_cfg_slot.get("time_bg_field", fields.get("time_bg_field") or "")
                    )
                    slot_vars[slot]["bg_nr"].set(
                        pen_cfg_slot.get("number_bg_field", fields.get("number_bg_field") or "")
                    )
                else:
                    pen_cfg_slot = penalties_cfg.get(slot, {})
                    slot_vars[slot]["time"].set(pen_cfg_slot.get("time_field", ""))
                    slot_vars[slot]["nr"].set(pen_cfg_slot.get("number_field", ""))
                    slot_vars[slot]["bg_time"].set(pen_cfg_slot.get("time_bg_field", ""))
                    slot_vars[slot]["bg_nr"].set(pen_cfg_slot.get("number_bg_field", ""))
            except Exception:
                pass

            # Comboboxar
            ttk.Combobox(
                pen_frame,
                textvariable=slot_vars[slot]["time"],
                values=text_fields,
                state="readonly",
                width=20,
            ).grid(row=r, column=1, padx=3, pady=2)

            ttk.Combobox(
                pen_frame,
                textvariable=slot_vars[slot]["nr"],
                values=text_fields,
                state="readonly",
                width=20,
            ).grid(row=r, column=2, padx=3, pady=2)

            ttk.Combobox(
                pen_frame,
                textvariable=slot_vars[slot]["bg_time"],
                values=image_fields,
                state="readonly",
                width=20,
            ).grid(row=r, column=3, padx=3, pady=2)

            ttk.Combobox(
                pen_frame,
                textvariable=slot_vars[slot]["bg_nr"],
                values=image_fields,
                state="readonly",
                width=20,
            ).grid(row=r, column=4, padx=3, pady=2)

        # Mobile permissions (för framtida webb-UI)
        tk.Label(adv_inner, text="Mobil-/webb-behörigheter",
                 font=("Segoe UI", 11, "bold")).grid(row=7, column=0, columnspan=4, sticky="w", pady=(10, 5))

        perms_cfg = sb_cfg.get("mobile_permissions", {})
        perm_defs = [
            ("Start/Stop klocka", "clock_control"),
            ("Justera tid", "adjust_time"),
            ("MÅL hemma", "goal_home"),
            ("MÅL borta", "goal_away"),
            ("Sätta utvisning", "set_penalty"),
            ("Rensa utvisning", "clear_penalty"),
            ("Empty goal", "empty_goal"),
            ("Byta period", "set_period"),
            ("Toggle scoreboard", "toggle_scoreboard"),
        ]

        perm_vars: dict[str, tk.BooleanVar] = {}
        perm_frame = tk.Frame(adv_inner)
        perm_frame.grid(row=8, column=0, columnspan=4, sticky="w", padx=10)

        for i, (label, key) in enumerate(perm_defs):
            var = tk.BooleanVar(value=bool(perms_cfg.get(key, True)))
            perm_vars[key] = var
            tk.Checkbutton(perm_frame, text=label, variable=var).grid(
                row=i // 2, column=i % 2, sticky="w", padx=5, pady=2
            )

        # Spara-knapp
        def on_save() -> None:
            # Validera tider
            pt = period_time_var.get().strip()
            ot = ot_time_var.get().strip()
            if _parse_time_to_seconds(pt) is None:
                messagebox.showerror("Fel", "Ogiltig periodtid (MM:SS).")
                return
            if _parse_time_to_seconds(ot) is None:
                messagebox.showerror("Fel", "Ogiltig OT-tid (MM:SS).")
                return

            # Spara scoreboard-input
            self.cfg["scoreboard"]["input"] = sb_var.get().strip()

            # Målgrafik
            self.cfg["scoreboard"]["goal_graphic_input"] = goal_var.get().strip()
            try:
                self.cfg["scoreboard"]["goal_overlay_channel"] = int(goal_ch_var.get().strip())
            except ValueError:
                self.cfg["scoreboard"]["goal_overlay_channel"] = 2
            try:
                self.cfg["scoreboard"]["goal_duration_ms"] = int(goal_dur_var.get().strip())
            except ValueError:
                self.cfg["scoreboard"]["goal_duration_ms"] = 5000

            # Efter-mål-grafik
            self.cfg["scoreboard"]["after_goal_graphic_input"] = after_goal_var.get().strip()
            try:
                self.cfg["scoreboard"]["after_goal_overlay_channel"] = int(after_goal_ch_var.get().strip())
            except ValueError:
                self.cfg["scoreboard"]["after_goal_overlay_channel"] = 2
            try:
                self.cfg["scoreboard"]["after_goal_duration_ms"] = int(after_goal_dur_var.get().strip())
            except ValueError:
                self.cfg["scoreboard"]["after_goal_duration_ms"] = 4000

            # Tider
            self.cfg["scoreboard"]["default_period_time"] = pt
            self.cfg["scoreboard"]["ot_time"] = ot

            global DEFAULT_PERIOD_TIME, DEFAULT_OT_TIME
            DEFAULT_PERIOD_TIME = pt
            DEFAULT_OT_TIME = ot

            # Overlay follow
            self.cfg["scoreboard"]["overlay_follow_clock"] = bool(overlay_var.get())

            # Penalty mapping
            new_pen_cfg = {}
            for slot in slots:
                v = slot_vars.get(slot)
                if not v:
                    continue
                new_pen_cfg[slot] = {
                    "time_field": v["time"].get().strip(),
                    "number_field": v["nr"].get().strip(),
                    "time_bg_field": v["bg_time"].get().strip(),
                    "number_bg_field": v["bg_nr"].get().strip(),
                    "name_field": None,
                }
            self.cfg["scoreboard"]["penalties"] = new_pen_cfg

            # Mobile permissions
            mob_perm = {}
            for label, key in perm_defs:
                mob_perm[key] = bool(perm_vars[key].get())
            self.cfg["scoreboard"]["mobile_permissions"] = mob_perm

            save_config(self.cfg)
            self._log("Inställningar sparade.")
            win.destroy()

        btn_wrap = tk.Frame(win)
        btn_wrap.pack(pady=8)
        ttk.Button(btn_wrap, text="Spara", command=on_save).pack(side="left", padx=5)
        ttk.Button(btn_wrap, text="Stäng", command=win.destroy).pack(side="left", padx=5)

    # --------------------------------------------------------
    # Ny period-dialog
    # --------------------------------------------------------
    def _ask_new_period(self) -> None:
        ans = messagebox.askyesno("Period slut", "Starta ny period?")
        if ans:
            # 1 → 2 → 3 → OT (4), sedan stannar på OT
            if self._current_period < 4:
                self._current_period += 1
            else:
                self._current_period = 4
            self._update_period_buttons()

            if self._require_controller():
                try:
                    # skriv period till scoreboard
                    val = "OT" if self._current_period == 4 else str(self._current_period)
                    self.controller.set_period(val)
                except Exception as e:
                    self._log(f"Fel vid set_period i _ask_new_period: {e}")

                # Välj rätt tid för nästa period
                period_time = DEFAULT_OT_TIME if self._current_period == 4 else DEFAULT_PERIOD_TIME
                try:
                    self.controller.set_match_time(period_time)
                    self._log(f"Ny periodtid satt: {period_time}")
                except Exception as e:
                    self._log(f"Kunde inte sätta ny periodtid: {e}")
        else:
            self._log("Användaren valde att inte starta ny period.")

    # --------------------------------------------------------
    # Helper
    # --------------------------------------------------------
    def _require_controller(self) -> bool:
        if not (self._connected and self.controller):
            messagebox.showwarning(
                "Ej ansluten", "Du måste ansluta till vMix först."
            )
            return False
        return True


# --------------------------------------------------------
# APP START
# --------------------------------------------------------
if __name__ == "__main__":
    app = ScoreboardApp()
    app.mainloop()
