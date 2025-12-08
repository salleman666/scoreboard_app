import requests
import xml.etree.ElementTree as ET
import logging

log = logging.getLogger(__name__)


class VMixClient:
    """
    Unified API client for vMix.

    All countdown operations MUST specify a SelectedName (text field)
    to target the correct countdown within a GT input.
    """

    def __init__(self, host="127.0.0.1", port=8088, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base = f"http://{self.host}:{self.port}/api/?"

    # ----------------------------------------------------------------------
    # LOW LEVEL CALL
    # ----------------------------------------------------------------------
    def call(self, query: str):
        """
        query = "Function=StartCountdown&Input=SCOREBOARD&SelectedName=Time.Text"
        """
        url = self.base + query
        try:
            r = requests.get(url, timeout=self.timeout)
            txt = (r.text or "").strip()
            if "completed successfully" not in txt:
                log.warning(f"[VMIX] call WARNING: {query} => {txt}")
            else:
                log.debug(f"[VMIX] call OK: {query}")
            return txt
        except Exception as e:
            log.error(f"[VMIX] call FAILED: {query} => {e}")
            return None

    def call_function(self, function: str, input_name: str = None, field: str = None, **params):
        """
        Utility to build a vMix Function call cleanly.

        Example:
        call_function("StartCountdown", "SCOREBOARD", "Time.Text")
        """
        parts = [f"Function={function}"]
        if input_name:
            parts.append(f"Input={input_name}")
        if field:
            parts.append(f"SelectedName={field}")
        for k, v in params.items():
            parts.append(f"{k}={v}")

        query = "&".join(parts)
        return self.call(query)

    # ----------------------------------------------------------------------
    # TEXT & VISIBILITY (NON-COUNTDOWN)
    # ----------------------------------------------------------------------
    def set_text(self, input_name: str, field: str, value: str):
        return self.call_function("SetText", input_name, field, Value=value)

    def set_visible(self, input_name: str, field: str, visible: bool):
        fn = "SetTextVisibleOn" if visible else "SetTextVisibleOff"
        return self.call_function(fn, input_name, field)

    def set_image_visible(self, input_name: str, field: str, visible: bool):
        fn = "SetImageVisibleOn" if visible else "SetImageVisibleOff"
        return self.call_function(fn, input_name, field)

    # ----------------------------------------------------------------------
    # COUNTDOWN SPECIFIC (REQUIRED FOR HOCKEY)
    # ----------------------------------------------------------------------
    def set_countdown(self, input_name: str, field: str, time_value: str):
        """
        Example:
        set_countdown("SCOREBOARD UPPE", "Time.Text", "20:00")
        """
        return self.call_function("SetCountdown", input_name, field, Value=time_value)

    def start_countdown(self, input_name: str, field: str):
        return self.call_function("StartCountdown", input_name, field)

    def pause_countdown(self, input_name: str, field: str):
        return self.call_function("PauseCountdown", input_name, field)

    def stop_countdown(self, input_name: str, field: str):
        """
        StopCountdown resets the countdown to its last SetCountdown value.
        """
        return self.call_function("StopCountdown", input_name, field)

    def adjust_countdown(self, input_name: str, field: str, seconds: int):
        """
        seconds may be positive or negative.
        """
        return self.call_function("AdjustCountdown", input_name, field, Value=str(seconds))

    # ----------------------------------------------------------------------
    # READ STATUS FROM VMIX (XML)
    # ----------------------------------------------------------------------
    def get_status(self):
        """
        Returns parsed XML root or None.
        """
        try:
            url = f"http://{self.host}:{self.port}/api"
            r = requests.get(url, timeout=self.timeout)
            root = ET.fromstring(r.text)
            return root
        except Exception as e:
            log.error(f"[VMIX] get_status FAILED: {e}")
            return None

    # ----------------------------------------------------------------------
    # ENUMERATE INPUTS AND FIELDS
    # ----------------------------------------------------------------------
    def list_inputs(self):
        """
        Returns list of input titles (strings)
        """
        root = self.get_status()
        if root is None:
            return []

        inputs = []
        for node in root.findall("inputs/input"):
            title = node.get("title") or node.get("shortTitle")
            if title:
                inputs.append(title.strip())
        return inputs

    def list_fields(self, input_name: str):
        """
        Returns all text and image fields for a GT input.

        [
            "Time.Text",
            "HomeP1time.Text",
            "HomeP1nr.Text",
            ...
            "HomeP1bg.Source",
            ...
        ]
        """
        root = self.get_status()
        if root is None:
            return []

        for node in root.findall("inputs/input"):
            title = node.get("title") or node.get("shortTitle")
            if title == input_name:
                fields = []

                # collect text fields
                for txt in node.findall("text"):
                    name = txt.get("name")
                    if name:
                        fields.append(name)

                # collect image fields
                for img in node.findall("image"):
                    name = img.get("name")
                    if name:
                        fields.append(name)

                return fields

        # no match
        return []
