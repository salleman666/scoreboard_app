import requests
import xml.etree.ElementTree as ET


class VMixClient:
    """
    High-level vMix API wrapper with:
    - XML status fetch
    - title field enumeration
    - safe countdown control
    - overlay toggling
    - text updates
    """

    def __init__(self, host="127.0.0.1", port=8088):
        self.host = host
        self.port = port
        self.base_url = f"http://{self.host}:{self.port}/api/?"
        self._cached_xml = None

    # --------------------------------------------------
    # Internal low-level GET wrapper
    # --------------------------------------------------
    def _get(self, query: str) -> str:
        url = self.base_url + query
        r = requests.get(url)
        r.raise_for_status()
        return r.text

    # --------------------------------------------------
    # vMix XML status
    # --------------------------------------------------
    def refresh_status(self):
        """Force refresh and return full XML"""
        self._cached_xml = self.get_status_xml()
        return self._cached_xml

    def get_status_xml(self) -> str:
        """
        Retrieves vMix status.
        vMix requires Function=None to return full XML.
        """
        xml = self._get("Function=None")
        self._cached_xml = xml
        return xml

    # --------------------------------------------------
    # Parsing helpers
    # --------------------------------------------------
    def list_inputs(self) -> list:
        """
        Returns every input title in the preset.
        """
        xml = self.get_status_xml()
        root = ET.fromstring(xml)

        res = []
        for inp in root.findall("./inputs/input"):
            title = inp.get("title") or inp.get("shortTitle") or ""
            if title:
                res.append(title)
        return res

    def list_title_fields(self, input_name: str) -> list:
        """
        Returns every <text name="..."> and <image name="..."> field for a specific title,
        suitable for mapping inside MappingDialog.
        """
        xml = self.get_status_xml()
        root = ET.fromstring(xml)

        for inp in root.findall("./inputs/input"):
            title = inp.get("title") or inp.get("shortTitle")
            if title != input_name:
                continue

            fields = []

            for node in inp.findall("./text"):
                nm = node.get("name")
                if nm:
                    fields.append(nm)

            for node in inp.findall("./image"):
                nm = node.get("name")
                if nm:
                    fields.append(nm)

            for node in inp.findall("./color"):
                nm = node.get("name")
                if nm:
                    fields.append(nm)

            return fields

        return []

    # --------------------------------------------------
    # Base API function executor
    # --------------------------------------------------
    def call_function(self, function: str, **kwargs):
        """
        Sends a vMix API function:
        e.g.
            call_function("SetText", Input="Scoreboard", SelectedName="HomeScore.Text", Value="5")
        """
        parts = [f"Function={function}"]
        for k, v in kwargs.items():
            if v is None:
                continue
            parts.append(f"{k}={v}")

        query = "&".join(parts)
        return self._get(query)

    # --------------------------------------------------
    # TEXT UPDATE
    # --------------------------------------------------
    def update_text(self, input_name: str, field_name: str, value: str):
        if not input_name or not field_name:
            return
        self.call_function("SetText", Input=input_name, SelectedName=field_name, Value=value)

    # --------------------------------------------------
    # IMAGE UPDATE
    # --------------------------------------------------
    def update_image(self, input_name: str, field_name: str, path_or_url: str):
        if not input_name or not field_name:
            return
        self.call_function("SetImage", Input=input_name, SelectedName=field_name, Value=path_or_url)

    # --------------------------------------------------
    # OVERLAY TOGGLE
    # --------------------------------------------------
    def overlay_toggle(self, overlay_number: int):
        self.call_function("OverlayInput", Value=str(overlay_number))

    # --------------------------------------------------
    # COUNTDOWN LOGIC (correct vMix usage)
    # --------------------------------------------------
    def set_countdown(self, input_name: str, field_name: str, mmss: str):
        """
        DOES NOT start clock, only sets initial value.
        Example: "20:00"
        """
        if not input_name or not field_name:
            return
        self.call_function(
            "SetCountdown",
            Input=input_name,
            SelectedName=field_name,
            Value=mmss,
        )

    def start_countdown(self, input_name: str, field_name: str):
        """
        FIRST start after a SetCountdown
        """
        if not input_name or not field_name:
            return
        self.call_function(
            "StartCountdown",
            Input=input_name,
            SelectedName=field_name,
        )

    def pause_countdown(self, input_name: str, field_name: str):
        """
        Toggle pause/resume for running clock
        """
        if not input_name or not field_name:
            return
        self.call_function(
            "PauseCountdown",
            Input=input_name,
            SelectedName=field_name,
        )

    def stop_countdown(self, input_name: str, field_name: str):
        """
        FULL stop — resets to initial time
        """
        if not input_name or not field_name:
            return
        self.call_function(
            "StopCountdown",
            Input=input_name,
            SelectedName=field_name,
        )

    def adjust_countdown(self, input_name: str, field_name: str, seconds: int):
        """
        Adjust ±seconds while running.
        Example: -5 or +10
        """
        if not input_name or not field_name:
            return
        self.call_function(
            "AdjustCountdown",
            Input=input_name,
            SelectedName=field_name,
            Value=str(seconds),
        )

    # --------------------------------------------------
    # ENABLED — for Empty Goal graphics
    # --------------------------------------------------
    def set_visible(self, input_name: str, overlay_number: int, enabled: bool):
        """
        toggles overlay on/off — but this depends on your graphics layout.
        """
        if enabled:
            self.call_function("OverlayInput", Input=input_name, Value=str(overlay_number))
        else:
            self.call_function("OverlayInputOff", Input=input_name, Value=str(overlay_number))
