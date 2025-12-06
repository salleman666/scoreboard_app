# scoreboard_app/core/vmix_client.py

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any


class VMixClient:
    """
    Minimal vMix API client
    - Get status XML
    - Get/set text fields
    - Get/set image visibility
    - Countdown control
    """

    def __init__(self, host: str, port: int = 8088):
        self.host = host
        self.port = port

    # ---------------------------------------------------------------------
    def _api(self, function: str, **params) -> str:
        """Send a vMix HTTP API request"""
        query = urllib.parse.urlencode(
            {"Function": function, **params}
        )
        url = f"http://{self.host}:{self.port}/api/?{query}"
        with urllib.request.urlopen(url, timeout=1) as f:
            return f.read().decode("utf-8")

    # ---------------------------------------------------------------------
    def get_status_xml(self) -> str:
        url = f"http://{self.host}:{self.port}/api"
        with urllib.request.urlopen(url, timeout=1) as f:
            return f.read().decode("utf-8")

    # ---------------------------------------------------------------------
    def parse_xml(self) -> ET.Element:
        xml = self.get_status_xml()
        return ET.fromstring(xml)

    # ---------------------------------------------------------------------
    def find_input(self, name: str) -> Optional[ET.Element]:
        """Return <input> XML node with the given title"""
        root = self.parse_xml()
        for inp in root.findall(".//input"):
            if inp.get("title", "").strip().lower() == name.lower():
                return inp
        return None

    # ---------------------------------------------------------------------
    def get_text(self, input_name: str, field: str) -> Optional[str]:
        inp = self.find_input(input_name)
        if inp is None:
            return None

        for node in inp.findall(".//text"):
            if node.get("name") == field:
                return (node.text or "").strip()

        return None

    # ---------------------------------------------------------------------
    def set_text(self, input_name: str, field: str, value: str) -> None:
        self._api("SetText", Input=input_name, SelectedName=field, Value=value)

    # ---------------------------------------------------------------------
    def set_visible(self, input_name: str, field: str, visible: bool) -> None:
        func = "SetImageVisibleOn" if visible else "SetImageVisibleOff"
        self._api(func, Input=input_name, SelectedName=field)

    # ---------------------------------------------------------------------
    def set_text_visible(self, input_name: str, field: str, visible: bool) -> None:
        func = "SetTextVisibleOn" if visible else "SetTextVisibleOff"
        self._api(func, Input=input_name, SelectedName=field)

    # ---------------------------------------------------------------------
    def start_countdown(self, input_name: str, field: str) -> None:
        self._api("StartCountdown", Input=input_name, SelectedName=field)

    def pause_countdown(self, input_name: str, field: str) -> None:
        self._api("PauseCountdown", Input=input_name, SelectedName=field)

    def reset_countdown(self, input_name: str, field: str) -> None:
        self._api("ResetCountdown", Input=input_name, SelectedName=field)
