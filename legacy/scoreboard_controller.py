# scoreboard_controller.py – Version 14.3
# ------------------------------------------------------------
# Fixar:
#  ✔ START/STOP styr både matchur OCH alla utvisningar (> 0 s)
#  ✔ Vid 00:00:
#       - matchur stoppas (StopCountdown)
#       - alla utvisningar PAUSAS (tid ligger kvar till nästa period)
#  ✔ Auto-clear av utvisning när den når 00:00
#       - MEN bara om matchuret > 0 (inte vid periodslut)
#  ✔ set_penalty(signatur) matchar GUI:
#       set_penalty(slot, nummer, namn, tid_str)
#    (namn ignoreras på SCOREBOARD UPPE)
#  ✔ is_scoreboard_overlay_active():
#       Läser <overlays><overlay number="X">INPUTNUMMER</overlay></overlays>
#       och kollar om scoreboard-inputen ligger på overlay_channel
#  ✔ set_scoreboard_overlay(visible) använder OverlayInput{N}In/Out
# ------------------------------------------------------------

from __future__ import annotations

from typing import Dict, Any, Optional

from vmix_client import VMixClient


def _parse_time_to_seconds(value: str | None) -> Optional[int]:
    """Tar emot 'MM:SS' och returnerar sekunder, eller None."""
    if not value:
        return None
    value = value.strip()
    parts = value.split(":")
    if len(parts) != 2:
        return None
    try:
        mm = int(parts[0])
        ss = int(parts[1])
    except ValueError:
        return None
    if ss < 0 or ss > 59 or mm < 0:
        return None
    return mm * 60 + ss


def _format_mmss(secs: int) -> str:
    if secs < 0:
        secs = 0
    m = secs // 60
    s = secs % 60
    return f"{m:02d}:{s:02d}"


class ScoreboardController:
    """Huvudlogik mot vMix scoreboard – Version 14.3"""

    def __init__(self, client: VMixClient, config: dict) -> None:
        self.client = client
        self.cfg = config
        self.sb_cfg = config.get("scoreboard", {})
        self.sb_input = self.sb_cfg.get("input", "")

        # intern state
        self._clock_running_flag: bool = False
        self._last_clock_secs: Optional[int] = None
        self._last_penalty_secs: Dict[str, Optional[int]] = {}

    # ------------------------------------------------------------
    # Hjälpare
    # ------------------------------------------------------------
    def _scoreboard_input_number(self) -> str:
        num = self.client.find_input_number(self.sb_input)
        if num is None:
            raise RuntimeError(f"Kunde inte hitta scoreboard-input: {self.sb_input}")
        return num

    def _penalty_fields(self, slot: str) -> Dict[str, Optional[str]]:
        """
        Returnerar fältnamn för en slot (H1/H2/A1/A2) med fallback mot
        riktig SCOREBOARD UPPE-layout.
        """
        slot = slot.upper()
        defaults: Dict[str, Dict[str, Optional[str]]] = {
            "H1": {
                "time_field": "HomeP1time.Text",
                "number_field": "HomeP1nr.Text",
                "name_field": None,
                "time_bg_field": "HomeP1bg.Source",
                "number_bg_field": "HomeP1bgnr.Source",
            },
            "H2": {
                "time_field": "HomeP2time.Text",
                "number_field": "HomeP2nr.Text",
                "name_field": None,
                "time_bg_field": "HomeP2bg.Source",
                "number_bg_field": "HomeP2bgnr.Source",
            },
            "A1": {
                "time_field": "AwayP1time.Text",
                "number_field": "AwayP1nr.Text",
                "name_field": None,
                "time_bg_field": "AwayP1bg.Source",
                "number_bg_field": "AwayP1bgnr.Source",
            },
            "A2": {
                "time_field": "AwayP2time.Text",
                "number_field": "AwayP2nr.Text",
                "name_field": None,
                "time_bg_field": "AwayP2bg.Source",
                "number_bg_field": "AwayP2bgnr.Source",
            },
        }

        cfg_pen = self.sb_cfg.get("penalties", {}).get(slot, {})
        base = defaults.get(slot, {})

        time_field = cfg_pen.get("time_field", base.get("time_field"))
        number_field = cfg_pen.get("number_field", base.get("number_field"))
        name_field = cfg_pen.get("name_field", base.get("name_field"))

        # stöd för både gamla "bg_field" och nya time_bg_field/number_bg_field
        time_bg_field = (
            cfg_pen.get("time_bg_field")
            or cfg_pen.get("bg_field")
            or base.get("time_bg_field")
        )
        number_bg_field = cfg_pen.get("number_bg_field") or base.get("number_bg_field")

        return {
            "time_field": time_field,
            "number_field": number_field,
            "name_field": name_field,
            "time_bg_field": time_bg_field,
            "number_bg_field": number_bg_field,
        }

    # ------------------------------------------------------------
    # Overlay-state från vMix XML
    # ------------------------------------------------------------
    def is_scoreboard_overlay_active(self) -> bool:
        """
        Läser <overlays><overlay number="1">1</overlay>...</overlays>
        och kollar om SCOREBOARD-inputnumret ligger på overlay_channel.
        """
        root = self.client.get_status_xml()
        sb_num = self._scoreboard_input_number()
        channel = int(self.sb_cfg.get("overlay_channel", 1))

        overlays_node = root.find("./overlays")
        if overlays_node is None:
            return False

        for ov in overlays_node.findall("overlay"):
            num_attr = ov.get("number")
            if num_attr != str(channel):
                continue
            text_val = (ov.text or "").strip()
            if text_val == sb_num:
                return True
        return False

    # ------------------------------------------------------------
    # State-läsning
    # ------------------------------------------------------------
    def get_state(self) -> Dict[str, Any]:
        """
        Läser XML från vMix och bygger state:
          - clock_raw / clock_secs
          - clock_running (från intern flagga)
          - mål
          - period
          - penalties: per slot time_raw, seconds, active, number
          - auto-clear penalties vid 00:00 (endast om matchuret > 0)
        """
        root = self.client.get_status_xml()
        sb_num = self._scoreboard_input_number()

        sb_node = None
        for inp in root.findall("./inputs/input"):
            if inp.get("number") == sb_num:
                sb_node = inp
                break
        if sb_node is None:
            raise RuntimeError("Kunde inte hitta SCOREBOARD-input i XML.")

        # Bygg text-tabell
        texts: Dict[str, str] = {}
        for t in sb_node.findall("text"):
            name = t.get("name") or ""
            texts[name] = (t.text or "").strip()

        # Matchur
        clock_field = self.sb_cfg["clock_field"]
        clock_raw = texts.get(clock_field, "00:00")
        clock_secs = _parse_time_to_seconds(clock_raw)

        if clock_secs == 0:
            # om vMix klocka är 0 → vår flagga är alltid False
            self._clock_running_flag = False
        running = self._clock_running_flag
        self._last_clock_secs = clock_secs

        # Mål & period
        home_score = texts.get(self.sb_cfg["home_score_field"], "")
        away_score = texts.get(self.sb_cfg["away_score_field"], "")
        period = texts.get(self.sb_cfg["period_field"], "")

        # Utvisningar
        penalties_state: Dict[str, Dict[str, Any]] = {}
        pen_cfg = self.sb_cfg.get("penalties", {})

        for slot in pen_cfg.keys():
            fields = self._penalty_fields(slot)
            tf = fields["time_field"]
            nf = fields["number_field"]

            t_raw = texts.get(tf or "", "00:00") if tf else "00:00"
            secs = _parse_time_to_seconds(t_raw)
            active = secs is not None and secs > 0

            penalties_state[slot] = {
                "slot": slot,
                "time_raw": t_raw,
                "seconds": secs,
                "active": active,
                "number": texts.get(nf or "", ""),
            }

        # Auto-clear penalties när de gått från >0 till 0
        # MEN endast om matchuret inte står på 0 (under pågående period).
        for slot, pdata in penalties_state.items():
            secs = pdata.get("seconds")
            prev = self._last_penalty_secs.get(slot)
            if (
                secs == 0
                and prev is not None
                and prev > 0
                and (clock_secs is None or clock_secs > 0)
            ):
                # penalty har tickat ner till 0 under spel → släck
                self.clear_penalty(slot)
                pdata["active"] = False
                pdata["time_raw"] = "00:00"
                pdata["seconds"] = 0

            self._last_penalty_secs[slot] = secs

        return {
            "clock_raw": clock_raw,
            "clock_secs": clock_secs,
            "clock_running": running,
            "home_score": home_score,
            "away_score": away_score,
            "period": period,
            "penalties": penalties_state,
        }

    # ------------------------------------------------------------
    # Matchur – START/STOP + 00:00
    # ------------------------------------------------------------
    def toggle_clock(self) -> None:
        """
        START/STOP för matchur OCH alla penalties med tid > 0.
        """
        state = self.get_state()
        sb_num = self._scoreboard_input_number()
        clock_field = self.sb_cfg["clock_field"]
        clock_secs = state.get("clock_secs")

        if self._clock_running_flag:
            # PAUS – paus både matchur och alla aktiva utvisningar
            self.client.call_function(
                "PauseCountdown",
                Input=sb_num,
                SelectedName=clock_field,
            )
            for slot, pdata in state["penalties"].items():
                if pdata.get("seconds") and pdata["seconds"] > 0:
                    fields = self._penalty_fields(slot)
                    tf = fields["time_field"]
                    if tf:
                        self.client.call_function(
                            "PauseCountdown",
                            Input=sb_num,
                            SelectedName=tf,
                        )
            self._clock_running_flag = False
            return

        # START
        if clock_secs is None or clock_secs <= 0:
            # ingen tid = GUI får hindra start
            self._clock_running_flag = False
            return

        # starta matchur
        self.client.call_function(
            "StartCountdown",
            Input=sb_num,
            SelectedName=clock_field,
        )

        # starta alla penalties med tid > 0
        for slot, pdata in state["penalties"].items():
            if pdata.get("seconds") and pdata["seconds"] > 0:
                fields = self._penalty_fields(slot)
                tf = fields["time_field"]
                if tf:
                    self.client.call_function(
                        "StartCountdown",
                        Input=sb_num,
                        SelectedName=tf,
                    )

        self._clock_running_flag = True

    def stop_clock_and_penalties_at_zero(self) -> None:
        """
        Körs när GUI ser att clock_secs == 0.
        Stoppar matchur helt (StopCountdown) och PAUSAR alla utvisningar.
        """
        state = self.get_state()
        if state.get("clock_secs") != 0:
            return

        sb_num = self._scoreboard_input_number()
        clock_field = self.sb_cfg["clock_field"]

        # Stoppa matchur (så vMix inte hoppar till starttid igen)
        self.client.call_function(
            "StopCountdown",
            Input=sb_num,
            SelectedName=clock_field,
        )

        # Pausa alla penalties (behåll kvarvarande tid)
        for slot, fields in (
            (slot, self._penalty_fields(slot))
            for slot in self.sb_cfg.get("penalties", {}).keys()
        ):
            tf = fields["time_field"]
            if tf:
                self.client.call_function(
                    "PauseCountdown",
                    Input=sb_num,
                    SelectedName=tf,
                )

        self._clock_running_flag = False

    # ------------------------------------------------------------
    # Justering
    # ------------------------------------------------------------
    def adjust_times(self, delta_sec: int) -> None:
        """
        Justerar matchur + alla penalties med AdjustCountdown (±delta_sec).
        """
        if delta_sec == 0:
            return

        sb_num = self._scoreboard_input_number()
        val = str(delta_sec)
        clock_field = self.sb_cfg["clock_field"]

        # matchur – bara om giltig tid
        cur = self.client.get_text_from_title(sb_num, clock_field)
        secs = _parse_time_to_seconds(cur)
        if secs is not None and secs > 0:
            self.client.call_function(
                "AdjustCountdown",
                Input=sb_num,
                SelectedName=clock_field,
                Value=val,
            )

        # penalties
        for slot in self.sb_cfg.get("penalties", {}).keys():
            fields = self._penalty_fields(slot)
            tf = fields["time_field"]
            if not tf:
                continue
            cur = self.client.get_text_from_title(sb_num, tf)
            secs = _parse_time_to_seconds(cur)
            if secs is not None and secs > 0:
                self.client.call_function(
                    "AdjustCountdown",
                    Input=sb_num,
                    SelectedName=tf,
                    Value=val,
                )

    # ------------------------------------------------------------
    # Period & matchtid
    # ------------------------------------------------------------
    def set_period(self, value: str) -> None:
        sb_num = self._scoreboard_input_number()
        field = self.sb_cfg["period_field"]
        self.client.set_text(sb_num, field, value)

    def set_match_time(self, time_str: str) -> None:
        secs = _parse_time_to_seconds(time_str)
        if secs is None or secs < 0:
            raise ValueError(f"Ogiltig matchtid: {time_str!r}")
        t_str = _format_mmss(secs)

        sb_num = self._scoreboard_input_number()
        field = self.sb_cfg["clock_field"]

        # nollställ & sätt countdown
        self.client.call_function(
            "StopCountdown",
            Input=sb_num,
            SelectedName=field,
        )
        self.client.set_countdown(sb_num, field, t_str)
        self.client.set_text(sb_num, field, t_str)

        self._last_clock_secs = secs
        self._clock_running_flag = False

    # ------------------------------------------------------------
    # Mål & mål-grafik
    # ------------------------------------------------------------
    def _change_score(self, field_name: str, delta: int) -> int:
        sb_num = self._scoreboard_input_number()
        cur_text = self.client.get_text_from_title(sb_num, field_name)
        try:
            cur = int(cur_text.strip())
        except Exception:
            cur = 0
        new = max(0, cur + delta)
        self.client.set_text(sb_num, field_name, str(new))
        return new

    def home_goal(self) -> int:
        return self._change_score(self.sb_cfg["home_score_field"], +1)

    def away_goal(self) -> int:
        return self._change_score(self.sb_cfg["away_score_field"], +1)

    def trigger_goal_graphic(self) -> None:
        """
        Tänder mål-grafik på goal_overlay_channel under goal_duration_ms.
        """
        goal_input = self.sb_cfg.get("goal_graphic_input")
        if not goal_input:
            return

        goal_channel = int(self.sb_cfg.get("goal_overlay_channel", 2))
        duration_ms = int(self.sb_cfg.get("goal_duration_ms", 5000))

        inp_num = self.client.find_input_number(goal_input) or goal_input

        def worker():
            import time as _t

            try:
                self.client.call_function(
                    f"OverlayInput{goal_channel}In",
                    Input=inp_num,
                )
                _t.sleep(duration_ms / 1000.0)
                self.client.call_function(
                    f"OverlayInput{goal_channel}Out",
                    Input=inp_num,
                )
            except Exception:
                pass

        import threading as _th

        _th.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------
    # Utvisningar
    # ------------------------------------------------------------
    def set_penalty(self, slot: str, number: str, name: str, time_str: str) -> None:
        """
        Sätter en utvisning:
          slot  = H1/H2/A1/A2
          number = tröjnummer
          name   = spelarnamn (IGNORERAS på SCOREBOARD UPPE)
          time_str = 'MM:SS'
        """
        slot = slot.upper()
        fields = self._penalty_fields(slot)
        tf = fields["time_field"]
        nf = fields["number_field"]

        if not tf or not nf:
            raise ValueError(f"Felfält för utvisning {slot}: saknar time/number_field")

        secs = _parse_time_to_seconds(time_str)
        if secs is None or secs < 0:
            raise ValueError(f"Ogiltig utvisningstid: {time_str!r}")
        t_str = _format_mmss(secs)

        sb_num = self._scoreboard_input_number()

        # nollställ intern timer → sätt ny countdown
        self.client.call_function(
            "StopCountdown",
            Input=sb_num,
            SelectedName=tf,
        )
        self.client.call_function(
            "SetCountdown",
            Input=sb_num,
            SelectedName=tf,
            Value=t_str,
        )
        self.client.set_text(sb_num, tf, t_str)

        # nummer
        self.client.set_text(sb_num, nf, number or "")

        # synlighet: tid/nummer + bakgrunder
        self.client.call_function("SetTextVisibleOn", Input=sb_num, SelectedName=tf)
        self.client.call_function("SetTextVisibleOn", Input=sb_num, SelectedName=nf)

        tbg = fields["time_bg_field"]
        nbg = fields["number_bg_field"]
        if tbg:
            self.client.call_function(
                "SetImageVisibleOn", Input=sb_num, SelectedName=tbg
            )
        if nbg:
            self.client.call_function(
                "SetImageVisibleOn", Input=sb_num, SelectedName=nbg
            )

        # starta bara om matchuret går
        if self._clock_running_flag and secs > 0:
            self.client.call_function(
                "StartCountdown",
                Input=sb_num,
                SelectedName=tf,
            )

        self._last_penalty_secs[slot] = secs

    def clear_penalty(self, slot: str) -> None:
        """
        Släcker en utvisning:
          - stoppar countdown
          - sätter 00:00
          - döljer tid/nummer + bakgrunder
        """
        slot = slot.upper()
        fields = self._penalty_fields(slot)
        tf = fields["time_field"]
        nf = fields["number_field"]

        if not tf or not nf:
            return

        sb_num = self._scoreboard_input_number()

        # stoppa + nollställ
        self.client.call_function(
            "StopCountdown",
            Input=sb_num,
            SelectedName=tf,
        )
        self.client.call_function(
            "SetCountdown",
            Input=sb_num,
            SelectedName=tf,
            Value="00:00",
        )
        self.client.set_text(sb_num, tf, "00:00")
        self.client.set_text(sb_num, nf, "")

        # synlighet AV
        self.client.call_function("SetTextVisibleOff", Input=sb_num, SelectedName=tf)
        self.client.call_function("SetTextVisibleOff", Input=sb_num, SelectedName=nf)

        tbg = fields["time_bg_field"]
        nbg = fields["number_bg_field"]
        if tbg:
            self.client.call_function(
                "SetImageVisibleOff", Input=sb_num, SelectedName=tbg
            )
        if nbg:
            self.client.call_function(
                "SetImageVisibleOff", Input=sb_num, SelectedName=nbg
            )

        self._last_penalty_secs[slot] = 0

    # ------------------------------------------------------------
    # Paus allt vid MÅL
    # ------------------------------------------------------------
    def pause_clock_and_penalties(self) -> None:
        """
        Pausar matchur + alla penalties med tid > 0 (vid MÅL).
        """
        state = self.get_state()
        sb_num = self._scoreboard_input_number()
        clock_field = self.sb_cfg["clock_field"]

        self.client.call_function(
            "PauseCountdown",
            Input=sb_num,
            SelectedName=clock_field,
        )

        for slot, pdata in state["penalties"].items():
            if pdata.get("seconds") and pdata["seconds"] > 0:
                fields = self._penalty_fields(slot)
                tf = fields["time_field"]
                if tf:
                    self.client.call_function(
                        "PauseCountdown",
                        Input=sb_num,
                        SelectedName=tf,
                    )

        self._clock_running_flag = False

    # ------------------------------------------------------------
    # Scoreboard overlay
    # ------------------------------------------------------------
    def set_scoreboard_overlay(self, visible: bool) -> None:
        """
        Slår på/av scoreboard-inputen på overlay_channel.
        """
        sb_num = self._scoreboard_input_number()
        channel = int(self.sb_cfg.get("overlay_channel", 1))
        func = f"OverlayInput{channel}In" if visible else f"OverlayInput{channel}Out"
        self.client.call_function(func, Input=sb_num)

    # ------------------------------------------------------------
    # Empty net
    # ------------------------------------------------------------
    def set_empty_net_home(self, visible: bool) -> None:
        field = self.sb_cfg.get("home_empty_field")
        bg = self.sb_cfg.get("home_empty_bg_field")
        if not field:
            return
        sb_num = self._scoreboard_input_number()
        func_text = "SetTextVisibleOn" if visible else "SetTextVisibleOff"
        self.client.call_function(func_text, Input=sb_num, SelectedName=field)
        if bg:
            func_img = "SetImageVisibleOn" if visible else "SetImageVisibleOff"
            self.client.call_function(func_img, Input=sb_num, SelectedName=bg)

    def set_empty_net_away(self, visible: bool) -> None:
        field = self.sb_cfg.get("away_empty_field")
        bg = self.sb_cfg.get("away_empty_bg_field")
        if not field:
            return
        sb_num = self._scoreboard_input_number()
        func_text = "SetTextVisibleOn" if visible else "SetTextVisibleOff"
        self.client.call_function(func_text, Input=sb_num, SelectedName=field)
        if bg:
            func_img = "SetImageVisibleOn" if visible else "SetImageVisibleOff"
            self.client.call_function(func_img, Input=sb_num, SelectedName=bg)
