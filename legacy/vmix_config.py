# VERSION 14.0 – unified config
# vmix_config.py

import json
import os

CONFIG_PATH = "vmix_config.json"

DEFAULT_CONFIG = {
    "vmix": {
        "host": "127.0.0.1",
        "port": 8088,
        "password": None,
    },
    "scoreboard": {
        # Titel / korttitel för scoreboard-input i vMix
        "input": "SCOREBOARD UPPE",

        # Fält på scoreboard
        "clock_field": "Time.Text",
        "home_score_field": "HomeScore.Text",
        "away_score_field": "AwayScore.Text",
        "period_field": "PeriodNr.Text",

        # Overlay / empty goal etc...
        # (resten identiskt med din nuvarande vmix_config.py)
    },
}


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
