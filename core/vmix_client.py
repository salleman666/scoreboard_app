import requests
import xml.etree.ElementTree as ET
import logging


class VMixClient:
    """
    Stable vMix API client.
    Uses XML /API endpoint for:
        - list_inputs()
        - list_fields(input)
        - all controllers can call get_status_xml()
    """

    def __init__(self, host="127.0.0.1", port=8088):
        self.host = host
        self.port = port
        self.timeout = 1.5

    # ----------------------------------------------------------------------
    # CORE
    # ----------------------------------------------------------------------

    def _api_url(self):
        return f"http://{self.host}:{self.port}/API"

    def get_status_xml(self):
        """Retrieve full XML status tree from vMix."""
        try:
            r = requests.get(self._api_url(), timeout=self.timeout)
            r.raise_for_status()
            return ET.fromstring(r.text)
        except Exception as e:
            logging.error(f"[VMIX] Unable to fetch XML status: {e}")
            raise

    # ----------------------------------------------------------------------
    # LIST INPUTS
    # ----------------------------------------------------------------------

    def list_inputs(self):
        """
        Returns list of input titles in vMix.
        Used by mapping dialog for section inputs.
        """
        xml = self.get_status_xml()
        titles = []
        for inp in xml.findall(".//input"):
            title = inp.get("title")
            if title:
                titles.append(title)
        return sorted(titles)

    # ----------------------------------------------------------------------
    # LIST FIELDS
    # ----------------------------------------------------------------------

    def list_fields(self, input_title):
        """
        Returns ALL text + image layer names inside given input.
        NOT filtered — filtering is done via mapping rules.
        """

        if not input_title:
            return []

        xml = self.get_status_xml()

        # find matching input
        for inp in xml.findall(".//input"):
            if inp.get("title") == input_title:

                fields = []

                # collect text layers
                for txt in inp.findall(".//text"):
                    nm = txt.get("name")
                    if nm:
                        fields.append(nm)

                # collect image layers
                for img in inp.findall(".//image"):
                    nm = img.get("name")
                    if nm:
                        fields.append(nm)

                return sorted(fields)

        return []
