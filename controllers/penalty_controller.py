import logging
from typing import Any, Dict, List

from scoreboard_app.core.vmix_client import VMixClient

log = logging.getLogger(__name__)


class PenaltyController:
    """
    Controller för utvisningar.

    Användning i GUI (PenaltyPanel):

        data = controller.get_penalties()

        data har formatet:
        {
            "home": [
                {"time": "02:00", "number": "12", "name": ""},
                {"time": "00:00", "number": "",   "name": ""},
            ],
            "away": [
                {"time": "05:00", "number": "22", "name": ""},
                {"time": "00:00", "number": "",   "name": ""},
            ],
        }

    All logik för att läsa/skriva vMix-fält utgår från vmix_config.json:

      "scoreboard": {
        "input": "SCOREBOARD UPPE",
        ...
      },

      "mapping": {
        "penalties": {
          "home": {
            "p1": {
              "time": "HomeP1time.Text",
              "time_bg": "HomeP1bg.Source",
              "number": "HomeP1nr.Text",
              "number_bg": "HomeP1bgnr.Source"
            },
            "p2": { ... }
          },
          "away": {
            "p1": { ... },
            "p2": { ... }
          }
        }
      }

    Just nu används bara time och number för att uppdatera GUI.
    BG-fälten (time_bg / number_bg) kan användas senare för att
    tända/släcka grafik, men är inte nödvändiga för att undvika fel.
    """

    # ---------------------------------------------------------
    def __init__(self, client: VMixClient, config: Dict[str, Any]) -> None:
        self.client = client
        self.cfg = config

        # Scoreboard-input (t.ex. "SCOREBOARD UPPE")
        sb_cfg = self.cfg.get("scoreboard", {})
        self.scoreboard_input: str = sb_cfg.get("input", "")

        # Penalty-mapping från config["mapping"]["penalties"]
        mapping = self.cfg.get("mapping", {})
        self.penalty_map: Dict[str, Any] = mapping.get("penalties", {})

        if not self.scoreboard_input:
            log.warning(
                "[PENALTIES] Ingen scoreboard.input satt i config['scoreboard']['input']"
            )
        if not self.penalty_map:
            log.warning(
                "[PENALTIES] Ingen mapping.penalties hittades i config['mapping']"
            )

    # ---------------------------------------------------------
    @staticmethod
    def _base_name(field_name: str) -> str:
        """
        Tar ett fullständigt fältnamn från vMix (t.ex. 'HomeP1time.Text')
        och returnerar basnamnet utan suffix (t.ex. 'HomeP1time').

        Detta behövs eftersom VMixClient.get_text / set_text själva lägger
        till '.Text' i API-anropen.
        """
        if not field_name:
            return ""
        # Klipp av allt efter första punkten, t.ex. ".Text" eller ".Source"
        return field_name.split(".", 1)[0]

    # ---------------------------------------------------------
    def _read_field(self, element_full_name: str) -> str:
        """
        Läser textvärdet från ett GT-fält på scoreboard-inputen.

        element_full_name är exakt namnet från vMix / vmix_config.json,
        t.ex. 'HomeP1time.Text'. Vi gör om det till 'HomeP1time' innan
        vi skickar det vidare till VMixClient.
        """
        if not self.scoreboard_input or not element_full_name:
            return ""

        base = self._base_name(element_full_name)
        if not base:
            return ""

        try:
            value = self.client.get_text(self.scoreboard_input, base)
            return value or ""
        except Exception as exc:
            log.error(
                "[PENALTIES] Misslyckades att läsa fält '%s' på input '%s': %s",
                element_full_name,
                self.scoreboard_input,
                exc,
            )
            return ""

    # ---------------------------------------------------------
    def _build_side_data(self, side_key: str) -> List[Dict[str, str]]:
        """
        Bygger listan med två slots för 'home' eller 'away'.

        Varje slot är ett dict med:
           {"time": "...", "number": "...", "name": ""}

        Name används inte ännu (vi har ingen direkt mapping till spelarnamn),
        så den lämnas tom.
        """
        side_map = self.penalty_map.get(side_key, {})

        slots: List[Dict[str, str]] = []

        # Vi har två uttalat definierade platser: p1 och p2
        for slot_key in ("p1", "p2"):
            slot_cfg = side_map.get(slot_key, {}) or {}

            time_field = slot_cfg.get("time", "")
            nr_field = slot_cfg.get("number", "")

            time_val = self._read_field(time_field)
            nr_val = self._read_field(nr_field)

            slots.append(
                {
                    "time": time_val,
                    "number": nr_val,
                    # Spelarnamn har vi inte mappat in ännu
                    "name": "",
                }
            )

        # Säkerställ exakt två slots även om config är ofullständig
        while len(slots) < 2:
            slots.append({"time": "", "number": "", "name": ""})

        return slots

    # ---------------------------------------------------------
    def get_penalties(self) -> Dict[str, List[Dict[str, str]]]:
        """
        API som används av PenaltyPanel för att uppdatera GUI.

        Returnerar:
        {
          "home": [ {time, number, name}, {time, number, name} ],
          "away": [ {time, number, name}, {time, number, name} ]
        }
        """
        # Om config saknas: returnera tomma strukturer så att GUI inte kraschar
        if not self.scoreboard_input or not self.penalty_map:
            log.debug("[PENALTIES] get_penalties körs utan komplett mapping")
            empty_slot = {"time": "", "number": "", "name": ""}
            return {
                "home": [empty_slot.copy(), empty_slot.copy()],
                "away": [empty_slot.copy(), empty_slot.copy()],
            }

        home_slots = self._build_side_data("home")
        away_slots = self._build_side_data("away")

        return {"home": home_slots, "away": away_slots}
