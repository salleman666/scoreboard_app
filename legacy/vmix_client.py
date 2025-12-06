# vmix_client.py – Version 14.0
# Enkel och ren klient mot vMix HTTP API.
# Används av:
#  - vmix_gui_tk.py (för att testa anslutning)
#  - scoreboard_controller.py (get_status_xml, find_input_number, set_text, set_countdown, call_function)
#
# Inga externa paket (requests) används – bara urllib i standardbiblioteket.

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import socket
from typing import Optional


class VMixClient:
    """
    Enkel klient mot vMix HTTP API.

    Bas-URL: http://host:port/api/
    Exempel:
      - GET /api/                        -> status XML
      - GET /api/?Function=StartCountdown&Input=1&SelectedName=Time.Text
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8088, password: str | None = None, timeout: float = 3.0):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout

    # ---------------------------------------------------------
    # Hjälpfunktioner – HTTP
    # ---------------------------------------------------------
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def _build_url(self, path: str = "/api/", params: dict | None = None) -> str:
        if not path.startswith("/"):
            path = "/" + path
        url = self.base_url + path
        if params:
            qs = urllib.parse.urlencode(params)
            url = url + "?" + qs
        return url

    def _http_get(self, url: str) -> str:
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, socket.timeout) as e:
            raise RuntimeError(f"vMix HTTP-fel: {e}") from e

    # ---------------------------------------------------------
    # Status XML
    # ---------------------------------------------------------
    def get_status_xml(self) -> ET.Element:
        """
        Hämtar vMix-XML (/api/) och returnerar root-elementet.
        """
        url = self._build_url("/api/")
        text = self._http_get(url)
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            raise RuntimeError(f"Kunde inte tolka vMix XML: {e}") from e
        return root

    # ---------------------------------------------------------
    # Inputs och fields
    # ---------------------------------------------------------
    def find_input_number(self, name_or_number: str | int) -> Optional[str]:
        """
        Tar antingen ett nummer (1, '1') eller en titel/korttitel (t.ex. 'SCOREBOARD UPPE')
        och returnerar input-numret som sträng, eller None om det inte hittas.
        """
        # om användaren skickar ren siffra -> använd direkt
        if isinstance(name_or_number, int):
            return str(name_or_number)
        s = str(name_or_number).strip()
        if s.isdigit():
            return s

        root = self.get_status_xml()
        inputs = root.findall("./inputs/input")
        s_lower = s.lower()

        for inp in inputs:
            num = inp.get("number")
            title = (inp.get("title") or "").strip()
            short_title = (inp.get("shortTitle") or "").strip()
            key = (inp.get("key") or "").strip()

            if (
                title.lower() == s_lower
                or short_title.lower() == s_lower
                or key.lower() == s_lower
            ):
                return num
        return None

    def _find_input_node(self, name_or_number: str | int) -> Optional[ET.Element]:
        num = self.find_input_number(name_or_number)
        if num is None:
            return None
        root = self.get_status_xml()
        for inp in root.findall("./inputs/input"):
            if inp.get("number") == num:
                return inp
        return None

    def get_text_from_title(self, input_name_or_number: str | int, field_name: str) -> str:
        """
        Hämtar text från ett TitleText-fält i en GT/Title-input.
        """
        node = self._find_input_node(input_name_or_number)
        if node is None:
            return ""
        for txt in node.findall("./text"):
            if (txt.get("name") or "") == field_name:
                return (txt.text or "").strip()
        return ""

    # ---------------------------------------------------------
    # SET text / countdown
    # ---------------------------------------------------------
    def set_text(self, input_name_or_number: str | int, field_name: str, value: str) -> None:
        """
        Sätter text i Title (TitleText-fält) via Function=SetText.
        """
        inp_num = self.find_input_number(input_name_or_number)
        if inp_num is None:
            raise ValueError(f"Kunde inte hitta input: {input_name_or_number}")

        self.call_function(
            "SetText",
            Input=inp_num,
            SelectedName=field_name,
            Value=str(value),
        )

    def set_countdown(self, input_name_or_number: str | int, field_name: str, value: str) -> None:
        """
        Sätter vMix interna countdown-värde (starttid) i ett fält.
        Exempel: '20:00'.
        """
        inp_num = self.find_input_number(input_name_or_number)
        if inp_num is None:
            raise ValueError(f"Kunde inte hitta input: {input_name_or_number}")

        self.call_function(
            "SetCountdown",
            Input=inp_num,
            SelectedName=field_name,
            Value=str(value),
        )

    # ---------------------------------------------------------
    # GENERELL FUNCTION-call
    # ---------------------------------------------------------
    def call_function(self, function_name: str, **params) -> None:
        """
        Kör en vMix Function, t.ex.:
          call_function("StartCountdown", Input=1, SelectedName="Time.Text")
        """
        q = {"Function": function_name}
        # lägg på övriga parametrar som strängar
        for k, v in params.items():
            if v is None:
                continue
            q[k] = str(v)

        url = self._build_url("/api/", q)
        _ = self._http_get(url)  # vi bryr oss inte om svaret här

    # ---------------------------------------------------------
    # Overlay-hjälpare (valfria)
    # ---------------------------------------------------------
    def overlay_on(self, input_name_or_number: str | int, channel: int = 1) -> None:
        """
        Slår på en input som overlay på given kanal (1–4).
        """
        inp_num = self.find_input_number(input_name_or_number)
        if inp_num is None:
            raise ValueError(f"Kunde inte hitta input: {input_name_or_number}")
        func = f"OverlayInput{int(channel)}In"
        self.call_function(func, Input=inp_num)

    def overlay_off(self, input_name_or_number: str | int, channel: int = 1) -> None:
        """
        Slår av en input från overlay på given kanal (1–4).
        """
        inp_num = self.find_input_number(input_name_or_number)
        if inp_num is None:
            raise ValueError(f"Kunde inte hitta input: {input_name_or_number}")
        func = f"OverlayInput{int(channel)}Out"
        self.call_function(func, Input=inp_num)

    # ---------------------------------------------------------
    # Poänghjälp (används ev. i andra moduler)
    # ---------------------------------------------------------
    def increment_score(self, input_name_or_number: str | int, field_name: str, delta: int = 1) -> int:
        """
        Hämtar nuvarande poäng (Text), ökar/minskar, skriver tillbaka.
        Om texten inte är ett tal börjar vi från 0.
        Returnerar nya värdet.
        """
        current_text = self.get_text_from_title(input_name_or_number, field_name)
        try:
            current = int(current_text)
        except (TypeError, ValueError):
            current = 0

        new_value = max(0, current + delta)
        self.set_text(input_name_or_number, field_name, str(new_value))
        return new_value
