import requests
import xml.etree.ElementTree as ET

class VMixClient:
    def __init__(self, host="127.0.0.1", port=8088):
        self.base = f"http://{host}:{port}"

    # -----------------------------
    # GENERIC CALL WRAPPER
    # -----------------------------
    def call(self, function: str, **params):
        """
        Example:
        client.call("SetText", Input="SCOREBOARD", SelectedName="HomeScore.Text", Value="3")
        """
        url = self.base + "/api/?Function=" + function
        for k, v in params.items():
            url += f"&{k}={v}"

        try:
            r = requests.get(url)
            if r.status_code != 200:
                print(f"[VMixClient] CALL ERROR {url} -> HTTP {r.status_code}")
        except Exception as e:
            print(f"[VMixClient] CALL EXCEPTION: {e}")

    # -----------------------------
    # READ STATUS XML
    # -----------------------------
    def get_status_xml(self):
        r = requests.get(self.base + "/api")
        return r.text

    # -----------------------------
    # INPUT ENUMERATION
    # -----------------------------
    def list_inputs(self):
        """
        Returns list of input names from vMix XML
        """
        xml = self.get_status_xml()
        root = ET.fromstring(xml)

        names = []
        for inp in root.findall(".//input"):
            nm = inp.get("title") or inp.get("name")
            if nm:
                names.append(nm)

        return names

    # -----------------------------
    # TEXT READ
    # -----------------------------
    def get_text(self, input_name: str, field_name: str):
        """
        Read text value from a GT title field
        """
        xml = self.get_status_xml()
        root = ET.fromstring(xml)

        for inp in root.findall(".//input"):
            nm = inp.get("title") or inp.get("name")
            if nm == input_name:
                for tit in inp.findall("text"):
                    if tit.get("name") == field_name:
                        return tit.text or ""
        return ""

    # -----------------------------
    # TEXT WRITE
    # -----------------------------
    def set_text(self, input_name: str, field_name: str, value: str):
        self.call(
            "SetText",
            Input=input_name,
            SelectedName=field_name,
            Value=value
        )

    # -----------------------------
    # TEXT VISIBILITY
    # -----------------------------
    def set_text_visible(self, input_name: str, field_name: str, visible: bool):
        fn = "SetTextVisibleOn" if visible else "SetTextVisibleOff"
        self.call(
            fn,
            Input=input_name,
            SelectedName=field_name
        )

    # -----------------------------
    # IMAGE VISIBILITY
    # -----------------------------
    def set_image_visible(self, input_name: str, field_name: str, visible: bool):
        fn = "SetImageVisibleOn" if visible else "SetImageVisibleOff"
        self.call(
            fn,
            Input=input_name,
            SelectedName=field_name
        )

    # -----------------------------
    # CLOCK START
    # -----------------------------
    def start_clock(self, input_name: str, field_name: str):
        self.call(
            "StartCountdown",
            Input=input_name,
            SelectedName=field_name
        )

    # -----------------------------
    # CLOCK STOP
    # -----------------------------
    def stop_clock(self, input_name: str, field_name: str):
        self.call(
            "StopCountdown",
            Input=input_name,
            SelectedName=field_name
        )

    # -----------------------------
    # CLOCK ADJUST (+/- seconds)
    # -----------------------------
    def adjust_clock(self, input_name: str, field_name: str, seconds: int):
        self.call(
            "AdjustCountdown",
            Input=input_name,
            SelectedName=field_name,
            Value=seconds
        )
