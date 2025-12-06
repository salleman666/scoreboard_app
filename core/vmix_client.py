import requests
import xml.etree.ElementTree as ET


class VMixClient:
    def __init__(self, host="127.0.0.1", port=8088):
        self.host = host
        self.port = port

    def _api(self, function: str, **params):
        url = f"http://{self.host}:{self.port}/api/"
        payload = {"Function": function}
        for k, v in params.items():
            payload[k] = v
        try:
            requests.get(url, params=payload, timeout=1)
        except:
            pass

    # ------------------------------
    # GET STATUS XML
    # ------------------------------
    def get_status_xml(self):
        url = f"http://{self.host}:{self.port}/api"
        r = requests.get(url, timeout=2)
        return r.text

    # ------------------------------
    # READ A TEXT FIELD
    # ------------------------------
    def get_text(self, input_name, field_name):
        """
        Reads a text field from vMix API XML
        """
        xml = self.get_status_xml()
        try:
            root = ET.fromstring(xml)
        except:
            return ""

        for inp in root.findall("input"):
            if inp.attrib.get("title") == input_name:
                for t in inp.findall("text"):
                    if t.attrib.get("name") == field_name:
                        return t.text or ""

        return ""

    # ------------------------------
    # WRITE TEXT FIELD
    # ------------------------------
    def set_text(self, input_name, field_name, value: str):
        self._api(
            "SetText",
            Input=input_name,
            SelectedName=field_name,
            Value=value
        )

    # ------------------------------
    # VISIBILITY — ON
    # ------------------------------
    def set_visible_on(self, input_name, field_name):
        self._api(
            "SetTextVisibleOn",
            Input=input_name,
            SelectedName=field_name
        )

    # ------------------------------
    # VISIBILITY — OFF
    # ------------------------------
    def set_visible_off(self, input_name, field_name):
        self._api(
            "SetTextVisibleOff",
            Input=input_name,
            SelectedName=field_name
        )

    # ------------------------------
    # GROUPED — ON/OFF
    # ------------------------------
    def set_text_visible_on_or_off(self, input_name, field_name, visible: bool):
        if visible:
            self.set_visible_on(input_name, field_name)
        else:
            self.set_visible_off(input_name, field_name)
