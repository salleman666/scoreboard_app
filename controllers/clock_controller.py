import logging
from scoreboard_app.config_loader import save_config, load_config
from scoreboard_app.core.vmix_client import VMixClient

log = logging.getLogger(__name__)


class ClockController:
    """
    CONTROL FLOW LOGIC:

    clock mappings stored in vmix_config.json:
    {
      "mapping": {
        "clock": {
          "input": "<vmix title name>",
          "field": "<vmix text field name>",   e.g. "Time.Text"
          "start_time": "20:00"
        }
      }
    }

    ALL VMIX CLOCK ACTIONS USE:
      - StartCountdown
      - StopCountdown
      - PauseCountdown
      - AdjustCountdown
      - SetCountdown
    """

    def __init__(self, vmix_client: VMixClient, cfg: dict):
        self.client = vmix_client
        self.cfg = cfg

        # REQUIRED PATH
        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}

        if "clock" not in self.cfg["mapping"]:
            self.cfg["mapping"]["clock"] = {
                "input": "",
                "field": "",
                "start_time": "20:00"
            }
            save_config(self.cfg)

        self.clock_map = self.cfg["mapping"]["clock"]
        self.clock_input = self.clock_map.get("input")
        self.clock_field = self.clock_map.get("field")
        self.default_time = self.clock_map.get("start_time", "20:00")

    # ---------------------------------------
    # VALIDATION
    # ---------------------------------------
    def _is_ready(self):
        if not self.clock_input or not self.clock_field:
            log.error("[CLOCK] Missing mapping: cannot run")
            return False
        return True

    # ---------------------------------------
    # READ CLOCK VALUE (OPTIONAL)
    # ---------------------------------------
    def get_time(self):
        """
        Reads current time from vMix text field
        """
        if not self._is_ready():
            return None

        txt = self.client.read_text(self.clock_input, self.clock_field)
        return txt

    # ---------------------------------------
    # CLOCK ACTIONS
    # ---------------------------------------
    def set_time(self, mmss: str):
        """
        Manually set a time, before first start OR to reset after StopCountdown
        """
        if not self._is_ready():
            return

        log.info(f"[CLOCK] Set time => {mmss}")
        self.client.set_countdown(self.clock_input, self.clock_field, mmss)

    def start_clock(self):
        """
        First call should ALWAYS be StartCountdown
        """

        if not self._is_ready():
            return

        current = self.get_time()

        # If empty or 00:00 => restore starting time before start
        if not current or current in ["00:00", "0:00", "{0:00|mm:ss}"]:
            log.info(f"[CLOCK] First start => restoring {self.default_time}")
            self.set_time(self.default_time)

        log.info("[CLOCK] Start")
        self.client.start_countdown(self.clock_input, self.clock_field)

    def pause_clock(self):
        """
        Use PauseCountdown
        """
        if not self._is_ready():
            return

        log.info("[CLOCK] Pause")
        self.client.pause_countdown(self.clock_input, self.clock_field)

    def stop_clock(self):
        """
        StopCountdown means => reset field back to initial state (00:00 or default)
        """
        if not self._is_ready():
            return

        log.info("[CLOCK] Stop")
        self.client.stop_countdown(self.clock_input, self.clock_field)

    # ---------------------------------------
    # PERIOD ADJUSTMENT
    # ---------------------------------------
    def adjust_time(self, delta_seconds: int):
        """
        +5 / -5 etc using AdjustCountdown
        """
        if not self._is_ready():
            return

        log.info(f"[CLOCK] Adjust {delta_seconds:+} sec")
        self.client.adjust_countdown(self.clock_input, self.clock_field, delta_seconds)

    # ---------------------------------------
    # SAVE MAPPINGS FROM MAPPINGDIALOG
    # ---------------------------------------
    def update_mapping(self, input_name, field_name, start_time):
        """
        Called when user modifies mappings in MappingDialog
        """

        if "mapping" not in self.cfg:
            self.cfg["mapping"] = {}

        self.cfg["mapping"]["clock"] = {
            "input": input_name,
            "field": field_name,
            "start_time": start_time
        }

        save_config(self.cfg)

        # Reload internal values
        self.clock_map = self.cfg["mapping"]["clock"]
        self.clock_input = self.clock_map.get("input")
        self.clock_field = self.clock_map.get("field")
        self.default_time = self.clock_map.get("start_time", "20:00")

        log.info("[CLOCK] Mapping updated and saved")
