import json
import os

# Location of vmix_config.json relative to project root
CONFIG_FILE = os.path.join(
    os.path.dirname(__file__), "..", "vmix_config.json"
)
CONFIG_FILE = os.path.abspath(CONFIG_FILE)

def load_config():
    """Reads JSON config, returns dict."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[CONFIG] load_config error: {e}")
        return {}

def save_config(cfg: dict):
    """Writes cfg dict to JSON safely."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"[CONFIG] save_config error: {e}")
