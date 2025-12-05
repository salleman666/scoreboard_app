import threading
import xml.etree.ElementTree as ET
import requests
from typing import Optional, Dict, Any


class VMixClient:
    """
    Unified API wrapper over vMix XML and function API.
    Adds helper methods so GUI controllers don't need to perform XML parsing.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.base = f"http://{host}:{port}"
        self._lock = threading.Lock()
        self._tk_safe = True

    # ----------------------------------------------------------------------
    # SAFE-UPDATE TOGGLE (controllers can disable thread-unsafe GUI refresh)
    # ----------------------------------------------------------------------
    def set_tk_safe_update(self, enabled: bool):
        self._tk_safe = enabled

    # ----------------------------------------------------------------------
    # BASIC API CALLS
    # ----------------------------------------------------------------------
    def _api(self, function: str, **params):
        url = f"{self.base}/api"
        q = {"function": function}
        q.update(params)

        with self._lock:
            return requests.get(url, params=q, timeout=1)

    def get_status_xml(self) -> ET.Element:
        url = f"{self.base}/api"
        with self._lock:
            r = requests.get(url, timeout=1)
        return ET.fromstring(r.text)

    # ----------------------------------------------------------------------
    # INPUT LOOKUP
    # ----------------------------------------------------------------------
    def find_input(self, input_name: str) -> Optional[ET.Element]:
        root = self.get_status_xml()
        for inp in root.findall("inputs/input"):
            if inp.get("title") == input_name:
                return inp
        return None

    # ----------------------------------------------------------------------
    # FIELD READERS
    # ----------------------------------------------------------------------
    def get_text(self, input_name: str, field_name: str) -> str:
        inp = self.find_input(input_name)
        if inp is None:
            return ""

        for t in inp.findall("text"):
            if t.get("name") == field_name:
                return t.text or ""
        return ""

    def get_image(self, input_name: str, field_name: str) -> str:
        inp = self.find_input(input_name)
        if inp is None:
            return ""

        for t in inp.findall("image"):
            if t.get("name") == field_name:
                return t.text or ""
        return ""

    # ----------------------------------------------------------------------
    # FIELD WRITERS
    # ----------------------------------------------------------------------
    def set_text(self, input_name: str, field_name: str, value: str):
        return self._api(
            "SetText",
            Input=input_name,
            SelectedName=field_name,
            Value=value,
        )

    def set_image(self, input_name: str, field_name: str, path: str):
        return self._api(
            "SetImage",
            Input=input_name,
            SelectedName=field_name,
            Value=path,
        )

    # ----------------------------------------------------------------------
    # VISIBILITY FOR TITLES
    # ----------------------------------------------------------------------
    def set_text_visible_on(self, input_name: str, field_name: str):
        return self._api(
            "SetTextVisibleOn",
            Input=input_name,
            SelectedName=field_name,
        )

    def set_text_visible_off(self, input_name: str, field_name: str):
        return self._api(
            "SetTextVisibleOff",
            Input=input_name,
            SelectedName=field_name,
        )

    def set_image_visible_on(self, input_name: str, field_name: str):
        return self._api(
            "SetImageVisibleOn",
            Input=input_name,
            SelectedName=field_name,
        )

    def set_image_visible_off(self, input_name: str, field_name: str):
        return self._api(
            "SetImageVisibleOff",
            Input=input_name,
            SelectedName=field_name,
        )

    # ----------------------------------------------------------------------
    # CLOCK CONTROL (COUNTDOWNS)
    # ----------------------------------------------------------------------
    def countdown_start(self, input_name: str, field_name: str):
        return self._api(
            "StartCountdown",
            Input=input_name,
            SelectedName=field_name,
        )

    def countdown_pause(self, input_name: str, field_name: str):
        return self._api(
            "PauseCountdown",
            Input=input_name,
            SelectedName=field_name,
        )

    def countdown_reset(self, input_name: str, field_name: str):
        return self._api(
            "ResetCountdown",
            Input=input_name,
            SelectedName=field_name,
        )
