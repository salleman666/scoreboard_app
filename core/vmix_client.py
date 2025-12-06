import requests
from lxml import etree


class VMixClient:
    def __init__(self, host: str, port: int = 8088):
        self.host = host
        self.port = port
        self.base = f"http://{host}:{port}"

    # ==========================================================
    # RAW STATUS XML
    # ==========================================================
    def get_status_xml(self) -> etree._Element:
        """
        Returns parsed XML from /api
        """
        url = f"{self.base}/api"
        r = requests.get(url)
        r.raise_for_status()
        return etree.fromstring(r.content)

    # ==========================================================
    # GET TEXT FIELD FROM A TITLE
    # ==========================================================
    def get_text(self, input_name: str, field_name: str) -> str:
        """
        Reads text value from a vMix title input (Title/Text)
        """
        xml = self.get_status_xml()

        # find input node
        node = xml.xpath(f"//input[@title='{input_name}']")
        if not node:
            return ""

        input_node = node[0]

        txt = input_node.xpath(f".//text[@name='{field_name}']/text()")
        if txt:
            return txt[0]
        return ""

    # ==========================================================
    # SET TEXT VISIBLE
    # ==========================================================
    def set_text_visible_on_or_off(self, input_name: str, field_name: str, visible: bool):
        """
        Uses vMix API function: SetTextVisibleOn/Off
        Documentation:
        https://www.vmix.com/help29/ShortcutFunctionReference.html
        """
        function = "SetTextVisibleOn" if visible else "SetTextVisibleOff"
        url = f"{self.base}/api/?Function={function}&Input={input_name}&SelectedName={field_name}"
        requests.get(url)

    # ==========================================================
    # SET IMAGE (BG) VISIBLE
    # ==========================================================
    def set_bg_visible_on_or_off(self, input_name: str, field_name: str, visible: bool):
        """
        Uses vMix API function: SetImageVisibleOn/Off
        """
        function = "SetImageVisibleOn" if visible else "SetImageVisibleOff"
        url = f"{self.base}/api/?Function={function}&Input={input_name}&SelectedName={field_name}"
        requests.get(url)

    # ==========================================================
    # OPTIONAL – SET TEXT VALUE
    # ==========================================================
    def set_text(self, input_name: str, field_name: str, value: str):
        """
        Set a text value inside a title field
        """
        url = f"{self.base}/api/?Function=SetText&Input={input_name}&SelectedName={field_name}&Value={value}"
        requests.get(url)

    # ==========================================================
    # OPTIONAL – SET IMAGE VALUE
    # ==========================================================
    def set_image(self, input_name: str, field_name: str, path: str):
        """
        Change image source for a field
        """
        url = f"{self.base}/api/?Function=SetImage&Input={input_name}&SelectedName={field_name}&Value={path}"
        requests.get(url)
