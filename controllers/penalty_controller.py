# scoreboard_app/controllers/penalty_controller.py
import time
from typing import Dict, Optional

from scoreboard_app.core.vmix_client import VMixClient


class PenaltyState:
    """Håller koll på penalty-tider och aktiva overlay states."""

    def __init__(self):
        self.h1 = 0
        self.h2 = 0
        self.a1 = 0
        self.a2 = 0

        self.home_overlay_on = False
        self.away_overlay_on = False
        self.scoreboard_overlay_on = False

        self.period_timer_last_zero = False
        self.period_trigger_armed = False


class PenaltyController:
    """
    Automatik för utvisningar baserat på scoreboard-fält i vMix.
    Denna logik ersätter tidigare VB-Script.
    """

    def __init__(self, client: VMixClient, config: Dict):
        self.client = client
        self.cfg = config
        self.state = PenaltyState()

        self.input_name = self.cfg["inputs"]["scoreboard"]
        self.overlay_channel = self.cfg["mapping"]["scoreboard"].get("overlay_channel", 1)

        self.pen_map = self.cfg["mapping"]["penalties"]
        self.period_start_time = str(self.cfg["defaults"]["period_minutes"]) + ":00"

        self.use_auto_hide = True
        self.use_auto_multiview = True
        self.use_auto_overlay = True

    # -------------------------
    # helpers
    # -------------------------

    def _read_time(self, s: str) -> int:
        """
        Konvertera text t.ex. '1:20' eller '00:05' -> sekunder
        Riktigt robust, precis som VB-scriptet gjorde.
        """

        if not s:
            return 0

        s = s.strip()

        if s in ("0", "0:00", "00:00", "0.0", "00.0"):
            return 0

        if ":" in s:
            parts = s.split(":")
            if len(parts) == 2:
                try:
                    m = int(parts[0])
                    sec = int(parts[1])
                    return m * 60 + sec
                except:
                    return 0
            return 0

        try:
            v = int(s)
            return max(0, v)
        except:
            return 0

    # -------------------------------------------------------------
    def _get_penalty_times(self) -> None:
        """
        Läser penalty-fält från scoreboard-grafiken och lagrar dem i self.state
        """

        def read_side(side_cfg):
            num = self.client.get_text(self.input_name, side_cfg["number"])
            name = self.client.get_text(self.input_name, side_cfg["name"])
            t = self.client.get_text(self.input_name, side_cfg["time"])
            return {
                "number": num or "",
                "name": name or "",
                "seconds": self._read_time(t or "")
            }

        home1 = read_side(self.pen_map["home"]["p1"])
        home2 = read_side(self.pen_map["home"]["p2"])
        away1 = read_side(self.pen_map["away"]["p1"])
        away2 = read_side(self.pen_map["away"]["p2"])

        self.state.h1 = home1["seconds"]
        self.state.h2 = home2["seconds"]
        self.state.a1 = away1["seconds"]
        self.state.a2 = away2["seconds"]

    # -------------------------------------------------------------
    def _multiview_logic(self):
        """
        Samma logik som VB-scriptet:
        * Om en penalty <= 5 sek → visa MV overlay för det laget
        * Om ingen penalty aktiv → släck MV overlay
        """

        if not self.use_auto_multiview:
            return

        # HOME RULE
        home_alert = (
            (self.state.h1 > 0 and self.state.h1 <= 5)
            or (self.state.h2 > 0 and self.state.h2 <= 5)
        )

        if home_alert and not self.state.home_overlay_on:
            self.client.overlay_on(self.input_name, "9")
            self.state.home_overlay_on = True

        elif not home_alert and self.state.home_overlay_on:
            self.client.overlay_off(self.input_name, "9")
            self.state.home_overlay_on = False

        # AWAY RULE
        away_alert = (
            (self.state.a1 > 0 and self.state.a1 <= 5)
            or (self.state.a2 > 0 and self.state.a2 <= 5)
        )

        if away_alert and not self.state.away_overlay_on:
            self.client.overlay_on(self.input_name, "10")
            self.state.away_overlay_on = True

        elif not away_alert and self.state.away_overlay_on:
            self.client.overlay_off(self.input_name, "10")
            self.state.away_overlay_on = False

    # -------------------------------------------------------------
    def _auto_hide_logic(self):
        """
        Precis som i VB-scriptet:
        Om penalty = 0 → släck text + BG + Nummer + Nummer-BG
        """

        if not self.use_auto_hide:
            return

        for side in ("home", "away"):
            for p in ("p1", "p2"):
                cfg = self.pen_map[side][p]
                seconds = self._read_time(
                    self.client.get_text(self.input_name, cfg["time"]) or ""
                )

                if seconds == 0:
                    # time
                    self.client.set_text_visible(self.input_name, cfg["time"], False)

                    # TODO: when config is updated with BG fields…
                    # self.client.set_image_visible(...)

    # -------------------------------------------------------------
    def update(self) -> None:
        """
        UPDATE-LOOP:
        * läs nya penalty-tider
        * slå på/av MV overlays
        * auto-hide om aktiverat
        """

        self._get_penalty_times()
        self._multiview_logic()
        self._auto_hide_logic()

    # -------------------------------------------------------------
    def run_loop(self, interval_ms: int = 500):
        """
        Kör samma sak som Do While VB-scriptet.
        Kör tills applikationen avslutas.
        GUI kan köra detta i egen thread.
        """

        while True:
            try:
                self.update()
            except Exception as e:
                print("Penalty update error:", e)

            time.sleep(interval_ms / 1000.0)
