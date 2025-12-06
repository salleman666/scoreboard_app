import threading
import time

class ClockController:
    """
    Full clock backend with vMix sync, pause/start, period handling, adjust +/- seconds
    Uses standard vMix API.Function("PauseCountdown", SelectedName="Time.Text")
    """

    def __init__(self, client, cfg):
        self.client = client
        self.cfg = cfg

        # mapping
        m = cfg["mapping"]["scoreboard"]
        self.clock_field = m["clock"]
        self.period_field = m["period"]
        self.input_name = cfg["inputs"]["clock"]

        # state
        self.running = False
        self.current_period = 1
        self.refresh_ms = cfg["defaults"]["clock_refresh_ms"]

        # background sync thread
        self._stop = False
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    # ---------------------------------------------------------
    # INTERNAL SYNC LOOP
    # ---------------------------------------------------------
    def _loop(self):
        while not self._stop:
            try:
                if self.running:
                    # read clock from vmix
                    txt = self.client.get_text(self.input_name, self.clock_field)

                    # if vmix lost formatting, ignore
                    if txt and ":" in txt:
                        pass  # we could parse MM:SS here if needed

                # ignore else, GUI reads directly from vmix anyway

            except Exception as e:
                print("[ClockController] loop error:", e)

            time.sleep(self.refresh_ms / 1000)

    # ---------------------------------------------------------
    # API CALLS
    # ---------------------------------------------------------

    def start_clock(self):
        """Start the main scoreboard timer using PauseCountdown"""
        try:
            self.client.call_function(
                "PauseCountdown",
                Input=self.input_name,
                SelectedName=self.clock_field
            )
            self.running = True
        except Exception as e:
            print("[ClockController] start_clock ERROR:", e)

    def stop_clock(self):
        """Pause the main scoreboard timer using PauseCountdown"""
        try:
            self.client.call_function(
                "PauseCountdown",
                Input=self.input_name,
                SelectedName=self.clock_field
            )
            self.running = False
        except Exception as e:
            print("[ClockController] stop_clock ERROR:", e)

    # ---------------------------------------------------------
    # TIME ADJUSTMENT
    # ---------------------------------------------------------

    def adjust_time(self, seconds):
        """
        Adjust time by +- seconds.

        Reads current MM:SS from vMix, applies delta, rewrites formatted
        """
        try:
            cur = self.client.get_text(self.input_name, self.clock_field)
            if not cur or ":" not in cur:
                return

            mm, ss = cur.split(":")
            total = int(mm) * 60 + int(ss)
            total += seconds
            if total < 0:
                total = 0

            mm2 = total // 60
            ss2 = total % 60

            newtxt = f"{mm2:02d}:{ss2:02d}"

            self.client.set_text(
                self.input_name,
                self.clock_field,
                newtxt
            )

        except Exception as e:
            print("[ClockController] adjust_time ERROR:", e)

    # ---------------------------------------------------------
    # PERIOD HANDLING
    # ---------------------------------------------------------

    def set_period(self, p):
        """Update period in vMix and internal state"""
        try:
            self.current_period = p
            self.client.set_text(
                self.input_name,
                self.period_field,
                str(p)
            )
        except Exception as e:
            print("[ClockController] set_period ERROR:", e)

    # ---------------------------------------------------------
    # CLEANUP
    # ---------------------------------------------------------

    def shutdown(self):
        self._stop = True
