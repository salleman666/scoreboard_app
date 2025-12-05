import socket
import xml.etree.ElementTree as ET
from typing import Optional


class VMixClient:
    """
    Client for communicating with vMix via TCP API.

    Methods allow setting text/image fields on inputs, overlay control,
    and retrieving the full vMix state as XML.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8099) -> None:
        """
        Initialize VMixClient.

        Args:
            host: vMix host IP or hostname.
            port: vMix TCP API port.
        """
        self.host: str = host
        self.port: int = port
        self.sock: Optional[socket.socket] = None
        self.connected: bool = False

    def connect(self) -> bool:
        """
        Connect to vMix TCP API server.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"[VMixClient] Could not connect: {e}")
            self.connected = False
            return False

    def _send(self, command: str) -> bool:
        """
        Send a command to vMix via TCP.

        Args:
            command: The command string to send (without CRLF).

        Returns:
            True if the send succeeded, False otherwise.
        """
        if not self.connected or self.sock is None:
            return False
        try:
            msg = (command + "\r\n").encode("utf-8")
            self.sock.sendall(msg)
            return True
        except Exception as e:
            print(f"[VMixClient] Send error: {e}")
            return False

    def set_text(self, input_name: str, field: str, value: str) -> bool:
        """
        Set a text field on a vMix input.

        Args:
            input_name: The name (or GUID) of the vMix input.
            field: The name of the text field (SelectedName).
            value: The text value to set.

        Returns:
            True on success, False otherwise.
        """
        return self._send(
            f'FUNCTION SetText Input="{input_name}" SelectedName="{field}" Value="{value}"'
        )

    def set_image(self, input_name: str, field: str, value: str) -> bool:
        """
        Set an image (source) field on a vMix input.

        Args:
            input_name: The name (or GUID) of the vMix input.
            field: The name of the image field (SelectedName).
            value: The image source path or URL.

        Returns:
            True on success, False otherwise.
        """
        return self._send(
            f'FUNCTION SetImage Input="{input_name}" SelectedName="{field}" Value="{value}"'
        )

    def set_source(self, input_name: str, field: str, value: str) -> bool:
        """
        Alias for set_image. Many controllers call set_source().

        Args same as set_image().
        """
        return self.set_image(input_name, field, value)

    def set_overlay(self, channel: int, input_name: str) -> bool:
        """
        Enable overlay of an input on a given overlay channel.

        Args:
            channel: Overlay channel number (e.g. 0, 1, 2...).
            input_name: The input you want to overlay.

        Returns:
            True on success, False otherwise.
        """
        return self._send(
            f'FUNCTION OverlayInput{channel} Input="{input_name}"'
        )

    def clear_overlay(self, channel: int) -> bool:
        """
        Disable overlay on the given channel.

        Args:
            channel: Overlay channel number to clear.

        Returns:
            True on success, False otherwise.
        """
        return self._send(f'FUNCTION OverlayInput{channel}Off')

    def get_state_xml(self) -> Optional[ET.Element]:
        """
        Request vMix to send full state as XML, parse and return it.

        Ignores any leading non-XML response (e.g. 'VERSION OK').

        Returns:
            ElementTree root of XML response, or None if parse failed or no XML yet.
        """
        if not self._send("XML"):
            return None
        try:
            raw = self.sock.recv(999999)
            if not raw:
                print("[VMixClient] Empty XML reply")
                return None
            text = raw.decode("utf-8", errors="ignore").strip()
            if text.startswith("VERSION OK"):
                return None
            if "<" not in text:
                print("[VMixClient] No XML yet")
                return None
            xml_start = text[text.index("<"):]
            root = ET.fromstring(xml_start)
            return root
        except Exception as e:
            print(f"[VMixClient] XML parse error: {e}")
            return None

    def get_status_xml(self) -> Optional[ET.Element]:
        """
        Alias for get_state_xml() to support older code calling get_status_xml().
        """
        return self.get_state_xml()
    # ------------------------------------------------------------
    # COUNTDOWN CONTROL FOR GT FIELDS (Clock, Penalties, etc.)
    # ------------------------------------------------------------
    def set_countdown_start(self, input_name: str, field: str):
        """
        Start a countdown for a specific GT text field.
        Example field: "ClockTime.Text"
        """
        self._call_api("StartCountdown", {
            "Input": input_name,
            "SelectedName": field
        })

    def set_countdown_pause(self, input_name: str, field: str):
        """
        Pause countdown for a specific GT text field.
        """
        self._call_api("PauseCountdown", {
            "Input": input_name,
            "SelectedName": field
        })

    def set_countdown_reset(self, input_name: str, field: str):
        """
        Reset a countdown field to default text (usually period start)
        """
        self._call_api("ResetCountdown", {
            "Input": input_name,
            "SelectedName": field
        })

