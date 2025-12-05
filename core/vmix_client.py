"""
VMixClient
==========

Minimal core client wrapper for vMix XML HTTP API.

Responsibility:
- Request XML status from vMix
- Parse XML into pythonic structures (not controllers!)
- Offer helper calls: list_inputs(), get_text(), set_text(), etc.

This module MUST NOT include GUI logic or controller logic.
"""

from __future__ import annotations
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional


class VMixClient:
    """
    Core HTTP client for communicating with vMix.

    Parameters
    ----------
    host : str
        Hostname or IP address of vMix machine
    port : int
        vMix API port (usually 8088)

    Notes
    -----
    All API calls are synchronous HTTP calls.
    Errors propagate upwards (controllers must handle them).
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    # ----------------------------------------------------------------------
    def _build_url(self, command: str) -> str:
        """Return vMix HTTP API URL for a given command."""
        return f"http://{self.host}:{self.port}/api/?{command}"

    # ----------------------------------------------------------------------
    def _get_xml(self, command: Optional[str] = None) -> ET.Element:
        """
        Perform a GET request to vMix API and return top-level XML element.

        Parameters
        ----------
        command : str, optional
            API command (e.g. "Function=FadeToBlack")

        Returns
        -------
        ET.Element
            Parsed XML root element

        Raises
        ------
        Exception
            If HTTP fails or XML is malformed
        """

        if command:
            url = self._build_url(command)
        else:
            url = f"http://{self.host}:{self.port}/api/"

        r = requests.get(url, timeout=3)
        r.raise_for_status()

        try:
            xml_root = ET.fromstring(r.text)
        except ET.ParseError as e:
            raise Exception(f"VMixClient: XML parse error ({e})")  # noqa

        return xml_root

    # ----------------------------------------------------------------------
    def get_status_xml(self) -> ET.Element:
        """
        Get entire XML state from vMix.

        Returns
        -------
        ET.Element
            Root XML document

        Example use
        -----------
        xml = client.get_status_xml()
        """
        return self._get_xml()

    # ----------------------------------------------------------------------
    def list_inputs(self) -> List[Dict[str, str]]:
        """
        Return a simplified list of vMix inputs (title, key, type).

        Returns
        -------
        List[Dict[str, str]]
            Each element is: { "title": "...", "key": "...", "type": "GT" }
        """

        xml = self.get_status_xml()

        inputs = []
        for inp in xml.findall("inputs/input"):
            inputs.append(
                {
                    "title": inp.get("title", ""),
                    "key": inp.get("key", ""),
                    "type": inp.get("type", ""),
                }
            )
        return inputs

    # ----------------------------------------------------------------------
    def get_text(self, input_key: str, field_name: str) -> Optional[str]:
        """
        Get a GT text field from vMix.

        Parameters
        ----------
        input_key : str
            vMix input key (GUID)
        field_name : str
            Title text field, must end with ".Text"

        Returns
        -------
        Optional[str]
            Field content or None if not found
        """

        command = f"Input={input_key}&Value&Function=GetText&SelectedName={field_name}"
        xml = self._get_xml(command)

        node = xml.find("text")
        if node is None:
            return None
        return node.text or ""

    # ----------------------------------------------------------------------
    def set_text(self, input_key: str, field_name: str, value: str) -> None:
        """
        Set a GT text field value in vMix.

        Parameters
        ----------
        input_key : str
        field_name : str
        value : str

        Notes
        -----
        Controllers must handle errors.
        """

        safe_val = value.replace("&", "&amp;")
        command = (
            f"Input={input_key}&Function=SetText&SelectedName={field_name}"
            f"&Value={safe_val}"
        )
        self._get_xml(command)

    # ----------------------------------------------------------------------
    def trigger_function(self, function_name: str) -> None:
        """
        Trigger a vMix API function, e.g. "FadeToBlack", "Start", etc.

        Parameters
        ----------
        function_name : str
            Must match documented vMix API function names
        """

        command = f"Function={function_name}"
        self._get_xml(command)

    # ----------------------------------------------------------------------
    def overlay_on(self, overlay_number: int) -> None:
        """
        Turn on overlay.

        Parameters
        ----------
        overlay_number : int
            1-4 (vMix overlay channels)
        """
        command = f"Function=OverlayInput{overlay_number}On"
        self._get_xml(command)

    # ----------------------------------------------------------------------
    def overlay_off(self, overlay_number: int) -> None:
        """Turn off overlay channel."""
        command = f"Function=OverlayInput{overlay_number}Off"
        self._get_xml(command)
