"""
scoreboard_app/config/vmix_config.py

Ansvar:
- Hålla koll på var config-filen ligger
- Ladda / spara config (JSON)
- Ge en DEFAULT_CONFIG-struktur som resten av appen kan lita på.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

# ---------------------------------------------------------
# Filvägar
# ---------------------------------------------------------

# Den här filen ligger i scoreboard_app/config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# Själva JSON-filen vi jobbar mot
CONFIG_PATH = os.path.join(CONFIG_DIR, "vmix_config.json")

# ---------------------------------------------------------
# Default-konfiguration
# ---------------------------------------------------------

DEFAULT_CONFIG: Dict[str, Any] = {
    "connection": {
        "host": "127.0.0.1",
        "port": 8088,
        "password": "",
    },
    "scoreboard": {
        # Huvud-scoreboarden (titel/korttitel/nummer)
        "input": "SCOREBOARD UPPE",

        # Fält i scoreboard-grafiken
        "home_score_field": "HomeScore.Text",
        "away_score_field": "AwayScore.Text",
        "period_field": "Period.Text",
        "clock_field": "Time.Text",

        # Overlay-kanal (1–4)
        "overlay_channel": 1,

        # SHOTS på scoreboarden – FÄLT i SCOREBOARD-grafiken
        "shots_home_field": "HomeShotNr.Text",
        "shots_away_field": "AwayShotNr.Text",

        # Lag-namn & logo i scoreboarden
        "team_home_name_field": "NameHome.Text",
        "team_away_name_field": "NameAway.Text",
        "team_home_logo_field": "HomeLogo.Source",
        "team_away_logo_field": "AwayLogo.Source",

        # Fritext-override för lag (kan lämnas tom, då används data från lineup/annat)
        "team_home_name_override": "",
        "team_away_name_override": "",
    },

    "goal_graphics": {
        # INPUT för själva målgrafiken (blinkande "GOAL" etc.)
        "goal_input": "MÅÅL",
        "goal_overlay_channel": 2,
        "goal_duration_ms": 2000,

        # AFTER GOAL – namnskylt / lower third
        "after_goal_input": "NAMNSKYLT MED Nr",
        "after_goal_overlay_channel": 3,
        "after_goal_duration_ms": 3000,
        "after_goal_pause_ms": 0,  # paus mellan GOAL och AFTER GOAL

        # Fält i AFTER GOAL-grafiken
        "after_goal_number_field": "Nr.Text",
        "after_goal_name_field": "Name.Text",
        "after_goal_team_field": "Team.Text",
        "after_goal_logo_field": "Logo.Source",

        # I nuvarande mål-grafik finns inga *Text/*Source att mappar mot,
        # men vi reserverar plats här för framtiden.
        "goal_number_field": None,
        "goal_name_field": None,
        "goal_team_field": None,
        "goal_logo_field": None,
    },

    "empty_goal": {
        # Vilken INPUT innehåller empty-goal-grafiken?
        "input": "EMPTY GOAL",  # kan ändras till exakt titel

        # Fält i denna grafik
        "home_text_field": "HomeEmpty.Text",
        "away_text_field": "AwayEmpty.Text",
        "home_bg_field": "HomeEmptyBg.Source",
        "away_bg_field": "AwayEmptyBg.Source",

        # Standardtext (kan ändras i settings)
        "text": "EMPTY GOAL",
    },

    "shots": {
        # Input som innehåller matchstatistik (skott)
        # T.ex. "MATCHSTATS" eller liknande – inte samma som scoreboard.
        "source_input": "MATCHSTATS",

        # Fält i matchstats-grafiken
        "source_home_field": "HomeShots.Text",
        "source_away_field": "AwayShots.Text",

        # Fälten i scoreboarden att skriva till (speglas även i scoreboard.score_shots_*_field)
        "scoreboard_home_field": "HomeShotNr.Text",
        "scoreboard_away_field": "AwayShotNr.Text",

        # Poll-intervall (ms) om/när vi gör auto-uppdatering
        "poll_interval_ms": 1000,
    },

    "time": {
        # Standardtider för perioder
        "period_1": "20:00",
        "period_2": "20:00",
        "period_3": "20:00",
        "overtime": "05:00",
    },

    "teams": {
        # INPUT som innehåller laguppställningar (lineup-grafik)
        "lineup_home_input": "LINEUP HOME",
        "lineup_away_input": "LINEUP AWAY",

        # Mönster för spelarnamn/nummer – samma för alla rader
        # Ex: "H{n}_Name.Text" → n = 1..20
        "home_number_pattern": None,
        "home_name_pattern": None,
        "away_number_pattern": None,
        "away_name_pattern": None,

        # Antal spelare som används per lag (för framtida automatiska listor)
        "home_player_count": 20,
        "away_player_count": 20,
    },
}

# ---------------------------------------------------------
# Hjälpfunktioner
# ---------------------------------------------------------


def ensure_config_dir() -> None:
    if not os.path.isdir(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)


def load_config(path: str | None = None) -> Dict[str, Any]:
    """
    Laddar config från JSON. Om filen saknas skapas den utifrån DEFAULT_CONFIG.
    """
    ensure_config_dir()
    cfg_path = path or CONFIG_PATH

    if not os.path.isfile(cfg_path):
        save_config(DEFAULT_CONFIG, cfg_path)
        return DEFAULT_CONFIG.copy()

    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # Om JSON är trasig -> skriv om med default för att inte krascha
        save_config(DEFAULT_CONFIG, cfg_path)
        return DEFAULT_CONFIG.copy()

    # Se till att alla default-nycklar finns (mjuk merge)
    def _merge(default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = dict(default)
        for k, v in loaded.items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = _merge(out[k], v)
            else:
                out[k] = v
        return out

    return _merge(DEFAULT_CONFIG, data)


def save_config(cfg: Dict[str, Any], path: str | None = None) -> None:
    ensure_config_dir()
    cfg_path = path or CONFIG_PATH
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
