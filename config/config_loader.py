import json
import os

# ----------------------------------------------------
# CONFIG PATH (ALWAYS FIXED)
# ----------------------------------------------------
# This is exactly where mappings and settings are stored
CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(CONFIG_DIR, "vmix_config.json")

# ----------------------------------------------------
# DEFAULT CONFIG SCHEMA — used if file missing or broken
# ----------------------------------------------------
DEFAULT_CONFIG = {
    "mapping": {
        "clock": {
            "input": "",
            "field": ""
        },
        "penalties": {
            "input": "",
            "home": {
                "p1_time": "",
                "p1_nr": "",
                "p2_time": "",
                "p2_nr": ""
            },
            "away": {
                "p1_time": "",
                "p1_nr": "",
                "p2_time": "",
                "p2_nr": ""
            }
        },
        "scoreboard": {
            "input": "",
            "home_score_field": "",
            "away_score_field": "",
            "period_field": ""
        },
        "goals": {
            "input": "",
            "scorer_name_field": "",
            "scorer_number_field": "",
            "scorer_team_field": "",
            "scorer_logo_field": ""
        },
        "empty_goal": {
            "input": "",
            "home_field": "",
            "away_field": "",
            "text": ""
        }
    }
}

# ----------------------------------------------------
# LOAD CONFIG FROM DISK
# ----------------------------------------------------
def load_config():
    """
    Reads config from disk.
    If missing or corrupt -> creates a fresh default.
    ALWAYS returns a dict.
    """
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Merge defaults if partial config
        merged = _merge(DEFAULT_CONFIG, data)
        return merged

    except Exception:
        # If file broken, restore default
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


# ----------------------------------------------------
# SAVE CONFIG TO DISK
# ----------------------------------------------------
def save_config(cfg: dict):
    """
    Writes config to disk — ALWAYS overwrites file.
    """
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[CONFIG] FAILED TO SAVE: {e}")


# ----------------------------------------------------
# INTERNAL: MERGE EXISTING CONFIG WITH DEFAULTS
# ensures no missing sections or keys
# ----------------------------------------------------
def _merge(default: dict, user: dict):
    """
    Recursively merges dicts:
    - If user missing keys → default fills them
    - Never deletes user data
    - Always returns a complete schema
    """
    result = dict(default)

    for k, v in user.items():
        if k not in default:
            # Allow new user keys
            result[k] = v
        else:
            if isinstance(v, dict) and isinstance(default[k], dict):
                result[k] = _merge(default[k], v)
            else:
                result[k] = v

    return result
