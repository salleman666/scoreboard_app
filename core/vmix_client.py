import requests
import xml.etree.ElementTree as ET


class VMixClient:
    """
    Minimal, reliable vMix HTTP API wrapper
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8088):
        self.host = host
        self.port = port
        self.base = f"http://{host}:{port}"

    # ----------------------------------------------------------
    # Core request
    # ----------------------------------------------------------
    def _api(self, **params):
        """
        Execute HTTP GET request to vMix API.
        """
        try:
            r = requests.get(self.base, params=params, timeout=1.5)
            r.raise_for_status()
            return r.text
        except Exception as e:
            raise RuntimeError(f"vMix API error: {e}")

    # ----------------------------------------------------------
    # Get full XML
    # ----------------------------------------------------------
    def get_status_xml(self):
        return self._api()

    # ----------------------------------------------------------
    # Parse XML & read a text field
    # ----------------------------------------------------------
    def get_text(self, input_name: str, field: str) -> str:
        """
        Read <text name="Field">...</text> from given input.
        """
        xml = self.get_status_xml()
        root = ET.fromstring(xml)

        input_node = root.find(f".//input[@title='{input_name}']")
        if input_node is None:
            return ""

        t = input_node.find(f".//text[@name='{field}']")
        if t is None or t.text is None:
            return ""

        return t.text.strip()

    # ----------------------------------------------------------
    # SET TEXT CONTENT
    # ----------------------------------------------------------
    def set_text(self, input_name: str, field: str, value: str):
        return self._api(Function="SetText",
                         Input=input_name,
                         SelectedName=field,
                         Value=value)

    # ----------------------------------------------------------
    # SET IMAGE CONTENT
    # ----------------------------------------------------------
    def set_image(self, input_name: str, field: str, path: str):
        return self._api(Function="SetImage",
                         Input=input_name,
                         SelectedName=field,
                         Value=path)

    # ----------------------------------------------------------
    # TEXT VISIBLE CONTROL
    # ----------------------------------------------------------
    def text_visible_on(self, input_name: str, field: str):
        return self._api(Function="SetTextVisibleOn",
                         Input=input_name,
                         SelectedName=field)

    def text_visible_off(self, input_name: str, field: str):
        return self._api(Function="SetTextVisibleOff",
                         Input=input_name,
                         SelectedName=field)

    # ----------------------------------------------------------
    # IMAGE VISIBLE CONTROL
    # ----------------------------------------------------------
    def image_visible_on(self, input_name: str, field: str):
        return self._api(Function="SetImageVisibleOn",
                         Input=input_name,
                         SelectedName=field)

    def image_visible_off(self, input_name: str, field: str):
        return self._api(Function="SetImageVisibleOff",
                         Input=input_name,
                         SelectedName=field)

    # ----------------------------------------------------------
    # COUNTDOWN
    # ----------------------------------------------------------
    def start_countdown(self, input_name: str, field: str = None):
        if field:
            return self._api(Function="StartCountdown",
                             Input=input_name,
                             SelectedName=field)
        return self._api(Function="StartCountdown",
                         Input=input_name)

    def pause_countdown(self, input_name: str, field: str = None):
        if field:
            return self._api(Function="PauseCountdown",
                             Input=input_name,
                             SelectedName=field)
        return self._api(Function="PauseCountdown",
                         Input=input_name)

    def stop_countdown(self, input_name: str, field: str = None):
        if field:
            return self._api(Function="StopCountdown",
                             Input=input_name,
                             SelectedName=field)
        return self._api(Function="StopCountdown",
                         Input=input_name)

