import socket
import xml.etree.ElementTree as ET
from typing import Optional, Dict


class VMixClient:
    """
    Ny VMixClient – ren & stabil
    - Connect
    - get_status_xml()
    - set_text()
    - set_source()
    - overlay_on/off
    """

    def __init__(self, host="127.0.0.1", port=8099):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None

    # ---------------------------------------------------------
    # CONNECT
    # ---------------------------------------------------------
    def connect(self) -> bool:
        """Öppna TCP-socket till vMix"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2)
            self.sock.connect((self.host, self.port))

            # Prova handshake
            self.send("VERSION")
            return True

        except Exception as e:
            print(f"[VMixClient][ERROR] connect(): {e}")
            return False

    # ---------------------------------------------------------
    def send(self, cmd: str) -> str:
        """Skicka kommando och hämta svar"""
        if not self.sock:
            raise ConnectionError("VMixClient not connected")

        cmd_bytes = (cmd + "\r\n").encode("utf-8")

        self.sock.sendall(cmd_bytes)
        reply = self.sock.recv(4096)

        try:
            return reply.decode("utf-8", errors="ignore")
        except:
            return ""

    # ---------------------------------------------------------
    # XML STATUS
    # ---------------------------------------------------------
    def get_status_xml(self) -> Optional[ET.Element]:
        """
        Hämtar hela status-XML från VMIX
        -> RETURNERAR en ElementRoot
        """
        try:
            raw = self.send("XML")

            # Leta efter första "<"
            pos = raw.find("<")
            if pos < 0:
                print(f"[VMixClient] No XML start found in reply: {raw[:60]}")
                return None

            xml_data = raw[pos:]
            root = ET.fromstring(xml_data)
            return root

        except Exception as e:
            print(f"[VMixClient] XML parse error: {e}")
            return None

    # ---------------------------------------------------------
    # BASIC SETTERS
    # ---------------------------------------------------------
    def set_text(self, input_key: str, field_name: str, value: str) -> bool:
        """
        input_key = GT Input GUID
        field_name = t.ex. HomeScore.Text
        """
        try:
            cmd = f"FUNCTION SetText Input={input_key}&Value={value}&SelectedName={field_name}"
            self.send(cmd)
            return True
        except Exception as e:
            print(f"[VMixClient][ERROR] set_text(): {e}")
            return False

    def set_source(self, input_key: str, field_name: str, source: str) -> bool:
        """
        Set image source (PNG etc)
        """
        try:
            cmd = f"FUNCTION SetImage Input={input_key}&SelectedName={field_name}&Value={source}"
            self.send(cmd)
            return True
        except Exception as e:
            print(f"[VMixClient][ERROR] set_source(): {e}")
            return False

    # ---------------------------------------------------------
    # OVERLAY CONTROL
    # ---------------------------------------------------------
    def overlay_on(self, index: int) -> bool:
        try:
            self.send(f"FUNCTION OverlayInput{index}On")
            return True
        except Exception as e:
            print(f"[VMixClient][ERROR] overlay_on(): {e}")
            return False

    def overlay_off(self, index: int) -> bool:
        try:
            self.send(f"FUNCTION OverlayInput{index}Off")
            return True
        except Exception as e:
            print(f"[VMixClient][ERROR] overlay_off(): {e}")
            return False

    # ---------------------------------------------------------
    # SCOREBOARD HELPERS
    # ---------------------------------------------------------
    def update_score(self, input_key: str, home: str, away: str,
                     home_field="HomeScore.Text",
                     away_field="AwayScore.Text"):

        self.set_text(input_key, home_field, home)
        self.set_text(input_key, away_field, away)

    # ---------------------------------------------------------
    # PENALTIES
    # ---------------------------------------------------------
    def set_penalty(self, input_key: str, number: str, name: str,
                    time_str: str,
                    num_field="P1_Number.Text",
                    name_field="P1_Name.Text",
                    time_field="P1_Time.Text",
                    plate_field="P1_NumberBg.Source"):

        """
        No-player logic:
        - number == "" => hide plate
        """

        # time always visible
        self.set_text(input_key, time_field, time_str)

        if number:
            self.set_text(input_key, num_field, number)
            self.set_source(input_key, plate_field, "visible")
        else:
            self.set_text(input_key, num_field, "")
            self.set_source(input_key, plate_field, "")   # hides plate

        if name:
            self.set_text(input_key, name_field, name)
        else:
            self.set_text(input_key, name_field, "")

    # ---------------------------------------------------------
    # EMPTY GOAL
    # ---------------------------------------------------------
    def set_empty_goal(self, input_key: str, is_active: bool,
                       field_name="EmptyGoal.Text",
                       plate="EmptyGoalBg.Source",
                       override=""):

        """
        is_active = True => show EMPTY or override text
        override = custom text (max 10 chars)
        """

        if is_active:
            txt = override if override else "EMPTY"
            self.set_text(input_key, field_name, txt)
            self.set_source(input_key, plate, "visible")
        else:
            self.set_text(input_key, field_name, "")
            self.set_source(input_key, plate, "")

