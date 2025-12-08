import json
import os


CONFIG_FILENAME = "vmix_config.json"


def _default_mapping():
    """
    Ensures a consistent JSON structure for mappings.
    We auto-fill missing sections if needed.
    """
    return {
        "mapping": {
            "clock": {
                "input": "",
                "field": ""
            },
            "penalties": {
                "home": {
                    "p1": {
                        "time_field": "",
                        "nr_field": "",
                        "bg_time_field": "",
                        "bg_nr_field": ""
                    },
                    "p2": {
                        "time_field": "",
                        "nr_field": "",
                        "bg_time_field": "",
                        "bg_nr_field": ""
                    }
                },
                "away": {
                    "p1": {
                        "time_field": "",
                        "nr_field": "",
                        "bg_time_field": "",
                        "bg_nr_field": ""
                    },
                    "p2": {
                        "time_field": "",
                        "nr_field": "",
                        "bg_time_field": "",
                        "bg_nr_field": ""
                    }
                }
            },
            "goals": {
                "popup": {
                    "input": "",
                    "overlay": "",
                    "duration_ms": ""
                },
                "after": {
                    "input": "",
                    "name_field": "",
                    "nr_field": "",
                    "logo_field": "",
                    "team_field": "",
                    "overlay": "",
                    "duration_ms": "",
                    "pause_between_ms": ""
                }
            },
            "empty_goal": {
                "input": "",
                "text_field": "",
                "bg_field": ""
            }
        }
    }


def load_config(app_root=None):
    """
    Reads vmix_config.json from project root.
    If missing or invalid -> return default structure.
    """

    # Determine path
    if app_root:
        config_path = os.path.join(app_root, CONFIG_FILENAME)
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(here)
        config_path = os.path.join(root, CONFIG_FILENAME)

    # If file missing -> write default
    if not os.path.exists(config_path):
        cfg = _default_mapping()
        save_config(cfg, app_root)
        return cfg

    # Try load file
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except:
        cfg = _default_mapping()
        save_config(cfg, app_root)
        return cfg

    # Guarantee full schema
    cfg = _repair_schema(cfg)
    save_config(cfg, app_root)
    return cfg


def save_config(cfg, app_root=None):
    """
    Writes configuration to vmix_config.json.
    Ensures UTF-8 and safe overwrite.
    """

    if app_root:
        config_path = os.path.join(app_root, CONFIG_FILENAME)
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(here)
        config_path = os.path.join(root, CONFIG_FILENAME)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def _repair_schema(cfg):
    """
    Ensures missing mapping branches are created.
    Extremely important: prevents GUI crashes.
    """

    base = _default_mapping()

    if "mapping" not in cfg:
        cfg["mapping"] = base["mapping"]

    # deep merge: we enforce structure forall children
    for section, default_value in base["mapping"].items():
        if section not in cfg["mapping"]:
            cfg["mapping"][section] = default_value
            continue

        target = cfg["mapping"][section]
        if isinstance(default_value, dict):
            for key, sub in default_value.items():
                if key not in target:
                    target[key] = sub

    return cfg
