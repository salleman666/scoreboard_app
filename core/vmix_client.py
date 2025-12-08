import requests
import xml.etree.ElementTree as ET

class VMixClient:
    def __init__(self, host="127.0.0.1", port=8088, timeout=2):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.last_xml = None

    # -------------------------------------------
    # Basic HTTP util
    # -------------------------------------------
    def _get(self, query: str) -> str:
        url = f"http://{self.host}:{self.port}/api/?{query}"
        r = requests.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.text

    # -------------------------------------------
    # Status / XML
    # -------------------------------------------
    def get_status_xml(self) -> str:
        xml = self._get("")   # empty query returns full status
        self.last_xml = xml
        return xml

    def refresh_status(self):
        return self.get_status_xml()

    # -------------------------------------------
    # Input listing
    # -------------------------------------------
    def list_inputs(self):
        xml = self.get_status_xml()
        root = ET.fromstring(xml)
        res = []
        for inp in root.findall("./inputs/input"):
            title = inp.get("title")
            if title:
                res.append(title)
        return res

    # -------------------------------------------
    # FIELD EXTRACTION FIXED HERE
    # -------------------------------------------
    def list_title_fields(self, input_title: str):
        """
        Returns list of all GT field names (text, image, color)
        inside given input title.
        """
        xml = self.get_status_xml()
        root = ET.fromstring(xml)

        # find input
        for inp in root.findall("./inputs/input"):
            title = inp.get("title", "")
            if title.strip().lower() == input_title.strip().lower():

                fields = []

                # TEXT fields
                for t in inp.findall("./text"):
                    name = t.get("name")
                    if name:
                        fields.append(name)

                # IMAGE fields
                for im in inp.findall("./image"):
                    name = im.get("name")
                    if name:
                        fields.append(name)

                # COLOR fields
                for c in inp.findall("./color"):
                    name = c.get("name")
                    if name:
                        fields.append(name)

                return fields

        return []  # not found

    # -------------------------------------------
    # COUNTDOWN COMMANDS
    # -------------------------------------------
    def set_countdown(self, input_title, field_name, value: str):
        cmd = (
            f"Function=SetCountdown"
            f"&Input={input_title}"
            f"&SelectedName={field_name}"
            f"&Value={value}"
        )
        return self._get(cmd)

    def start_countdown(self, input_title, field_name):
        cmd = (
            f"Function=StartCountdown"
            f"&Input={input_title}"
            f"&SelectedName={field_name}"
        )
        return self._get(cmd)

    def pause_countdown(self, input_title, field_name):
        cmd = (
            f"Function=PauseCountdown"
            f"&Input={input_title}"
            f"&SelectedName={field_name}"
        )
        return self._get(cmd)

    def stop_countdown(self, input_title, field_name):
        cmd = (
            f"Function=StopCountdown"
            f"&Input={input_title}"
            f"&SelectedName={field_name}"
        )
        return self._get(cmd)
