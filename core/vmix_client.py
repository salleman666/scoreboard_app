import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any


class VMixClient:
    """
    Minimal HTTP API + XML API client for vMix.
    All controller logic must only use these methods.

    -----
    CORE RULE:
    We NEVER talk directly to requests or XML outside this class.
    All GUI/controllers call here only.
    -----

    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8088):
        self.base = f"http://{host}:{port}"

    # -------------------------------------------------------------
    # INTERNAL API REQUEST
    # -------------------------------------------------------------
    def _api(self, function: str, **params):
        """
        Execute vMix HTTP API:
        /api/?Function=OverlayInput1In&Input=SCOREBOARD
        """
        try:
            q = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.base}/api/?Function={function}"
            if q:
                url += "&" + q

            requests.get(url, timeout=1)
        except Exception as e:
            print(f"[VMixClient] API ERROR: {function} {e}")

    # -------------------------------------------------------------
    # XML STATUS
    # -------------------------------------------------------------
    def get_status_xml(self) -> ET.Element:
        """
        Returns root XML document
        """
        r = requests.get(f"{self.base}/api", timeout=1)
        return ET.fromstring(r.text)

    # -------------------------------------------------------------
    # INPUT FIELD ACCESS
    # -------------------------------------------------------------
    def get_input(self, input_name: str) -> Optional[ET.Element]:
        """
        Finds an input by title
        """
        root = self.get_status_xml()
        for i in root.findall("inputs/input"):
            if i.get("title") == input_name:
                return i
        return None

    def get_text(self, input_name: str, field: str) -> Optional[str]:
        """
        Reads <text name="..."> in a TITLE input
        """
        input_el = self.get_input(input_name)
        if input_el is None:
            return None

        for t in input_el.findall("text"):
            if t.get("name") == field:
                return t.text
        return None

    # -------------------------------------------------------------
    # FIELD WRITE OPERATIONS
    # -------------------------------------------------------------

    def set_text(self, input_name: str, field: str, value: str):
        """
        Set text inside title
        """
        self._api("SetText", Input=input_name, SelectedName=field, Value=value)

    def set_image(self, input_name: str, field: str, path: str):
        """
        Change image source
        """
        self._api("SetImage", Input=input_name, SelectedName=field, Value=path)

    # -------------------------------------------------------------
    # VISIBILITY
    # -------------------------------------------------------------

    def set_text_visible(self, input_name: str, field: str, visible: bool):
        if visible:
            self._api("SetTextVisibleOn", Input=input_name, SelectedName=field)
        else:
            self._api("SetTextVisibleOff", Input=input_name, SelectedName=field)

    def set_image_visible(self, input_name: str, field: str, visible: bool):
        if visible:
            self._api("SetImageVisibleOn", Input=input_name, SelectedName=field)
        else:
            self._api("SetImageVisibleOff", Input=input_name, SelectedName=field)

    # -------------------------------------------------------------
    # COUNTDOWN (CLOCK / PENALTIES)
    # -------------------------------------------------------------

    def start_countdown(self, input_name: str, field: Optional[str] = None):
        if field:
            self._api("StartCountdown", Input=input_name, SelectedName=field)
        else:
            self._api("StartCountdown", Input=input_name)

    def stop_countdown(self, input_name: str, field: Optional[str] = None):
        if field:
            self._api("StopCountdown", Input=input_name, SelectedName=field)
        else:
            self._api("StopCountdown", Input=input_name)

    def reset_countdown(self, input_name: str, field: Optional[str] = None):
        if field:
            self._api("ResetCountdown", Input=input_name, SelectedName=field)
        else:
            self._api("ResetCountdown", Input=input_name)

    # -------------------------------------------------------------
    # SCOREBOARD OVERLAY MANAGEMENT
    # -------------------------------------------------------------

    def show_overlay(self, input_name: str, channel=1):
        self._api(f"OverlayInput{channel}In", Input=input_name)

    def hide_overlay(self, input_name: str, channel=1):
        self._api(f"OverlayInput{channel}Out", Input=input_name)

    # -------------------------------------------------------------
    # MULTIVIEW OVERLAYS
    # -------------------------------------------------------------

    def mv_overlay_on(self, input_name: str, index: int):
        self._api("MultiViewOverlayOn", Input=input_name, Value=str(index))

    def mv_overlay_off(self, input_name: str, index: int):
        self._api("MultiViewOverlayOff", Input=input_name, Value=str(index))
